# Cua Perception Model Ledger

This directory records the reviewed inputs for an offline worker package. It
does not contain weights. A distributor must place the named files beside a
copy of `model-manifest.template.json`, replace the platform-specific ONNX
Runtime fields, and preserve the listed hashes. The worker performs no network
access and refuses missing or mismatched files before creating a model session.

## OmniParser icon detector (icon_detect_v3)

- Source: `microsoft/OmniParser-v2.0` on Hugging Face
- Revision: `f55d0750e5b94db2125ef0b45b0fa4a85ddc59b4`
- Immutable source URL: `https://huggingface.co/microsoft/OmniParser-v2.0/resolve/f55d0750e5b94db2125ef0b45b0fa4a85ddc59b4/icon_detect_v3/model.pt`
- Source file: `icon_detect_v3/model.pt` (self-contained TorchScript, YOLOv9-E)
- Source SHA-256: `11c6cbb77f22569fab22d86c76407a83ec81ab89dbfe28279854822d6e3fb00c`
  (equal to the Hugging Face `X-Linked-ETag` at that revision)
- Source size: 281,182,680 bytes
- License: MIT, from `icon_detect_v3/LICENSE` at the same revision
  (SHA-256 `646f8936b8ddcd14e13e578ff6857e368780b0d1a4f6066bee89211923a373e2`)
- Converted file: `omniparser-icon-detect-v3-1280-opset17.onnx`
- Converted SHA-256: `67f21c6aaf04ccadef08ab63328d08b0fde71bf7cef542ad3e3fe6aa438625eb`
- Converted size: 232,728,858 bytes
- Input: `images`, float32 `[1,3,1280,1280]`, RGB, `1/255`, 114 letterbox
- Output: `detections`, float32 `[1,33600,6]`, rows of
  `x1,y1,x2,y2,score,class` in letterboxed input pixels (`xyxy_score_class`)

`export_icon_detect_v3.py` is the executable conversion. It loads the
TorchScript module, adds the model card's decoding (sigmoid class logits and
left/top/right/bottom distances from each grid-cell center at strides 8, 16
and 32), and exports opset 17 with the legacy TorchScript exporter. Python
3.12, PyTorch 2.8.0 and ONNX 1.19.0 reproduce the digest above byte for byte.
The worker keeps its existing letterbox, threshold, NMS and restore code;
Microsoft's own pipeline decoder (`util/yolov9.py`) uses the same centered
114 letterbox and RGB `1/255` input.

Parity against that decoder on `tests/quality-corpus`: decoded boxes differ by
at most 0.03 px on the 1280 canvas and scores by at most 2e-6. After the
worker's postprocess, every non-degenerate Microsoft detection is matched at
IoU > 0.7; the only boxes the worker drops are zero-height boxes clamped out
of the letterbox padding, which `valid()` rejects by design.

The upstream model card recommends a 0.05 confidence threshold because the
detector is deliberately low-confidence on small controls, so the manifest
uses 0.05 and callers raise it per parse with `min_confidence`.

## PP-OCRv5 detector

- Source: official PaddlePaddle `PP-OCRv5_mobile_det_onnx` Hugging Face repository
- Revision: `e6f4fa85f00e168c862bc462aebca69eef9b3d3d`
- Immutable ONNX URL: `https://huggingface.co/PaddlePaddle/PP-OCRv5_mobile_det_onnx/resolve/e6f4fa85f00e168c862bc462aebca69eef9b3d3d/inference.onnx`
- ONNX SHA-256: `a431985659dc921974177a95adcfbb90fd9e51989a5e04d70d0b75f597b6e61d`
- `inference.yml` SHA-256: `98069072e1b6b37d727fd9d9f11725faa46d6ea0de012f2ed26caea011c37699`
- License: Apache-2.0
- Input/output: `x` / `fetch_name_0`
- Reviewed preprocessing: BGR, `1/255`, ImageNet mean/std, CHW
- Reviewed postprocessing: DB threshold 0.3, box threshold 0.6, unclip ratio 1.5

## PP-OCRv5 English recognizer

- Source: official PaddlePaddle `en_PP-OCRv5_mobile_rec_onnx` Hugging Face repository
- Revision: `3fafbc3b5dcf93dd72add9f48368be8a3a2cd33b`
- Immutable ONNX URL: `https://huggingface.co/PaddlePaddle/en_PP-OCRv5_mobile_rec_onnx/resolve/3fafbc3b5dcf93dd72add9f48368be8a3a2cd33b/inference.onnx`
- Immutable dictionary URL: `https://huggingface.co/PaddlePaddle/en_PP-OCRv5_mobile_rec_onnx/resolve/3fafbc3b5dcf93dd72add9f48368be8a3a2cd33b/inference.yml`
- ONNX SHA-256: `b5f833dfc5d0eb71da397b4efa06ebeee9b431b690a47d6af40d77d8eabc557f`
- `inference.yml` SHA-256: `27e91d0582f40168aa218303c76e184bc78fa7a5d105aad0cfbad8458b441067`
- License: Apache-2.0
- Input/output: `x` / `fetch_name_0`
- Reviewed input: BGR float32 `[1,3,48,320]`
- Dictionary: `PostProcess.character_dict` in the hashed `inference.yml`

## Packaging checklist

1. Obtain each artifact from its pinned source revision and verify SHA-256.
2. Convert `icon_detect_v3` with `export_icon_detect_v3.py` and the recorded
   toolchain and compare the converted SHA-256; a different conversion must
   receive a new ledger entry.
3. Package a CPU-only ONNX Runtime dynamic library and record its exact version
   and SHA-256 in the copied manifest. Set `intra_threads` to the bounded CPU
   concurrency selected for that package and target.
4. Keep every artifact path relative to the manifest. Absolute paths, parent
   traversal, symlinks, empty files, and hash mismatches are rejected.
5. Start with `cua-perception --manifest <path> --onnx-runtime-library <path>`.
   Use `--fixture` only for deterministic protocol tests.

PP-OCR DB detections are returned as axis-aligned bounds. Rotated probability
map regions are not perspective-corrected before recognition; health and parse
identity expose this limitation so a caller can decide whether it is suitable.

## ONNX Runtime CPU library

The reviewed candidate lock pins official CPU-only archives at immutable tag
`v1.26.0` for all three targets. The assembler verifies each platform archive,
extracts exactly one target member, and verifies its digest:

- macOS arm64 archive `7a1280bbb1701ea514f71828765237e7896e0f2e1cd332f1f70dbd5c3e33aca3`; `libonnxruntime.dylib` `cb0462c3fd35ad722e8772313030a33c182f3d4c6b33f4e5e1fcb2ce3199b86c`
- Windows x64 archive `6ebe99b5564bf4d029b6e93eac9ff423682b6212eade769e9ca3f685eaf500b4`; `onnxruntime.dll` `b2ba7ca16e0e4fe71ad5148744ab885a2f5809e52a0c3de4d9ba3853a03977f9`
- Linux x64 archive `1254da24fb389cf39dc0ff3451ab48301740ffbfcbaf646849df92f80ee92c57`; `libonnxruntime.so` `5bd5bedf736fc501692435d0ec4f6e8b2bdf48cd30af8e6d00d61b3ddc9a7ab8`

`scripts/artifacts.lock.json` is the machine-readable authority for URLs,
archive members, sizes, target identities, and hashes. `THIRD_PARTY_NOTICES.md`
and the `licenses/` texts must accompany every assembled bundle. The lock's
`prohibited_artifacts` list names the retired AGPL detector, its conversion,
and the Ultralytics source bundled for it; bundle verification rejects any
file or archive member with those digests.
