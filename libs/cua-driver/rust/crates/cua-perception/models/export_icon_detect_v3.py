#!/usr/bin/env python3
"""Convert Microsoft's MIT-licensed OmniParser icon_detect_v3 to Cua's detector ONNX.

icon_detect_v3 ships as a self-contained TorchScript module (YOLOv9-E trained
with the MIT-licensed MultimediaTechLab/YOLO code). It returns raw heads per
stride, `(cls_logits, box_ltrb)` for strides 8, 16 and 32. This script wraps
that module with the decoding documented in the upstream model card and exports
one ONNX graph whose single output is `[1, N, 6]` rows of
`[x1, y1, x2, y2, score, class]` in letterboxed input pixels. The worker's
existing `xyxy_score_class` postprocessing applies the confidence threshold,
NMS, and the letterbox restore, so no Rust decoding changes are needed.

No Ultralytics code is imported or executed. PyTorch is needed only here, at
artifact-generation time; the worker runs the result with ONNX Runtime.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
from pathlib import Path

SOURCE_URL = "https://huggingface.co/microsoft/OmniParser-v2.0"
SOURCE_REVISION = "f55d0750e5b94db2125ef0b45b0fa4a85ddc59b4"
EXPECTED_INPUT = "11c6cbb77f22569fab22d86c76407a83ec81ab89dbfe28279854822d6e3fb00c"
EXPECTED_VERSIONS = {"torch": "2.8.0", "onnx": "1.19.0"}
IMGSZ = 1280
STRIDES = (8, 16, 32)
OPSET = 17
INPUT_NAME = "images"
OUTPUT_NAME = "detections"


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def build_decoder(torch, scripted):
    """Upstream model-card decoding, scripted so the nested TorchScript module exports."""

    def centers(stride: int):
        grid = IMGSZ // stride
        gy, gx = torch.meshgrid(
            torch.arange(grid, dtype=torch.float32),
            torch.arange(grid, dtype=torch.float32),
            indexing="ij",
        )
        return (gx + 0.5).reshape(-1), (gy + 0.5).reshape(-1)

    class IconDetectV3Decoder(torch.nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.model = scripted
            for index, stride in enumerate(STRIDES):
                cx, cy = centers(stride)
                self.register_buffer(f"cx{index}", cx)
                self.register_buffer(f"cy{index}", cy)

        def level(self, cls_logits, box_ltrb, cx, cy, stride: float):
            cls = cls_logits.sigmoid()[0, 0].reshape(-1)
            ltrb = box_ltrb[0].reshape(4, -1)
            return torch.stack(
                [
                    (cx - ltrb[0]) * stride,
                    (cy - ltrb[1]) * stride,
                    (cx + ltrb[2]) * stride,
                    (cy + ltrb[3]) * stride,
                    cls,
                    torch.zeros_like(cls),
                ],
                dim=-1,
            )

        def forward(self, images):
            c8, b8, c16, b16, c32, b32 = self.model(images)
            rows = torch.cat(
                [
                    self.level(c8, b8, self.cx0, self.cy0, 8.0),
                    self.level(c16, b16, self.cx1, self.cy1, 16.0),
                    self.level(c32, b32, self.cx2, self.cy2, 32.0),
                ],
                dim=0,
            )
            return rows.unsqueeze(0)

    return torch.jit.script(IconDetectV3Decoder().eval())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_model", type=Path, help="icon_detect_v3/model.pt at SOURCE_REVISION")
    parser.add_argument("output", type=Path)
    parser.add_argument(
        "--expected-output-sha256",
        help="fail unless the exported ONNX has exactly this digest",
    )
    args = parser.parse_args()
    if digest(args.source_model) != EXPECTED_INPUT:
        parser.error("source model SHA-256 differs from the pinned icon_detect_v3 input")

    import onnx  # type: ignore[import-not-found]
    import torch  # type: ignore[import-not-found]

    actual = {"torch": torch.__version__.split("+")[0], "onnx": onnx.__version__}
    if actual != EXPECTED_VERSIONS:
        parser.error(f"exporter versions differ: expected {EXPECTED_VERSIONS}, got {actual}")

    torch.manual_seed(0)
    torch.use_deterministic_algorithms(True)
    scripted = torch.jit.load(str(args.source_model), map_location="cpu").eval()
    decoder = build_decoder(torch, scripted)
    example = torch.zeros(1, 3, IMGSZ, IMGSZ, dtype=torch.float32)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with torch.no_grad():
        torch.onnx.export(
            decoder,
            (example,),
            str(args.output),
            dynamo=False,
            opset_version=OPSET,
            input_names=[INPUT_NAME],
            output_names=[OUTPUT_NAME],
            do_constant_folding=True,
        )

    model = onnx.load(str(args.output))
    onnx.checker.check_model(model)
    del model.metadata_props[:]
    model.producer_name = "cua-perception-export-icon-detect-v3"
    model.producer_version = SOURCE_REVISION[:12]
    model.doc_string = f"{SOURCE_URL}@{SOURCE_REVISION} icon_detect_v3/model.pt (MIT)"
    onnx.save(model, str(args.output))

    output_digest = digest(args.output)
    print(f"{output_digest}  {args.output}")
    if args.expected_output_sha256 and output_digest != args.expected_output_sha256:
        parser.error("export completed, but output differs from the reviewed ONNX digest")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
