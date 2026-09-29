# Cua perception third-party notices

This document describes the reviewed candidate inputs. It is not a substitute
for the `NOTICE`, model ledger, source ledger, SBOM, and license texts shipped
with an exact `cua-perception` artifact. If those authenticated records are
missing or disagree with this summary, do not publish or redistribute the
artifact.

The default Cua Driver remains a separate MIT-licensed component and does not
include the extension, model weights, or ONNX Runtime library.

## Before you install, redistribute, or host the extension

This section summarizes known precautions. It is not legal advice. Consult
your own counsel before redistributing the extension or offering it as part of
a service.

- **The Driver license does not cover the extension.** Cua Driver stays MIT
  licensed with or without the extension, because it talks to the extension
  worker as a separate process over a protocol. The extension artifact carries
  its own component licenses: MIT for the icon detector and ONNX Runtime,
  Apache-2.0 for the PP-OCR models.
- **The extension is opt-in.** A default Driver installation never installs the
  extension or downloads model weights. Driver keeps working without it, and
  `parse_visual_regions` returns `not_installed`.
- **Redistribution keeps the notices.** If you copy the extension artifact to
  anyone else, include the license texts under `licenses/`,
  `THIRD_PARTY_NOTICES.md`, the model and source ledgers, and the SBOM. No
  component in the bundle is copyleft, so no corresponding-source offer is
  required.
- **The earlier detector is retired.** Releases through 0.2.1 shipped the
  AGPL-3.0-only `icon_detect` detector. The artifact lock lists its source
  weights, its ONNX conversion, and the Ultralytics exporter snapshot as
  prohibited digests, and bundle verification rejects any file or archive
  member that matches them.
- **No warranty.** The extension and its model artifacts are provided without
  warranty, as their licenses state. Detection output can be wrong. Do not use
  it as the sole basis for irreversible actions.

## OmniParser icon detector (icon_detect_v3)

- Origin: `microsoft/OmniParser-v2.0` model repository.
- Pinned revision: `f55d0750e5b94db2125ef0b45b0fa4a85ddc59b4`.
- Source model: `icon_detect_v3/model.pt` (YOLOv9-E, TorchScript), SHA-256
  `11c6cbb77f22569fab22d86c76407a83ec81ab89dbfe28279854822d6e3fb00c`.
- License: MIT, from `icon_detect_v3/LICENSE` at the same revision, SHA-256
  `646f8936b8ddcd14e13e578ff6857e368780b0d1a4f6066bee89211923a373e2`.
  Microsoft states the detector was trained with the MIT-licensed
  MultimediaTechLab/YOLO implementation, which is what allows the permissive
  license, unlike the Ultralytics-based `icon_detect`.
- Converted ONNX artifact: SHA-256
  `67f21c6aaf04ccadef08ab63328d08b0fde71bf7cef542ad3e3fe6aa438625eb`,
  232,728,858 bytes, produced by `models/export_icon_detect_v3.py`.

This summary records the license Microsoft publishes with the pinned revision.
It is not a legal opinion; verify the exact revision above.

## PP-OCRv5

The reviewed OCR inputs are official PaddlePaddle model repositories and are
recorded as Apache-2.0:

| Role | Repository revision | Reviewed ONNX SHA-256 |
| --- | --- | --- |
| Mobile detector | `PaddlePaddle/PP-OCRv5_mobile_det_onnx` at `e6f4fa85f00e168c862bc462aebca69eef9b3d3d` | `a431985659dc921974177a95adcfbb90fd9e51989a5e04d70d0b75f597b6e61d` |
| English recognizer | `PaddlePaddle/en_PP-OCRv5_mobile_rec_onnx` at `3fafbc3b5dcf93dd72add9f48368be8a3a2cd33b` | `b5f833dfc5d0eb71da397b4efa06ebeee9b431b690a47d6af40d77d8eabc557f` |

The recognizer dictionary comes from the pinned recognizer repository's
`inference.yml`, SHA-256
`27e91d0582f40168aa218303c76e184bc78fa7a5d105aad0cfbad8458b441067`.
Preserve the Apache-2.0 license and any notices in the assembled artifact.

## ONNX Runtime and conversion provenance

The worker loads a CPU-only ONNX Runtime dynamic library from the extension
package. Its upstream is Microsoft's
[`microsoft/onnxruntime`](https://github.com/microsoft/onnxruntime) project,
which publishes ONNX Runtime under the MIT license. The reviewed candidate lock
pins official CPU-only ONNX Runtime 1.26.0 archives for each supported target.
Assembly must verify the selected archive and library hashes and record the
exact version, target, SHA-256, license, notices, and source location in the
artifact manifest and SBOM. These candidate records are not evidence that a
particular runtime shipped.

The icon_detect_v3 conversion used Python 3.12, PyTorch 2.8.0 and ONNX 1.19.0,
opset 17, a fixed 1280 input, the model card's head decoding folded into the
graph, and no model-side NMS. No Ultralytics code is involved. These are
conversion-provenance inputs; the Rust worker has no Python runtime dependency.
The ONNX Runtime version used during conversion does not establish which
runtime library was packaged for a release.
