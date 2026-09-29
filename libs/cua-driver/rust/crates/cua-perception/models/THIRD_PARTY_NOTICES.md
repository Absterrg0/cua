# Cua Perception Third-Party Notices

This Cua Perception bundle contains the following separately licensed
components. Exact revisions and SHA-256 digests are recorded in
`model-ledger.json` and `source-inventory.json` in each bundle. The full
license texts are in this `notices/` directory:

- `Apache-2.0.txt`: Apache License, Version 2.0.
- `MIT-OmniParser-icon_detect_v3.txt`: the MIT License file Microsoft publishes
  beside the `icon_detect_v3` weights.
- `onnxruntime-LICENSE.txt` and `onnxruntime-ThirdPartyNotices.txt`: the MIT
  License and third-party notices shipped with the pinned ONNX Runtime archive.

Cua Driver and the Cua Perception worker are MIT licensed. The extension as a
whole is not: each component below keeps its own license.

## ONNX Runtime

Copyright Microsoft Corporation. The bundle includes a CPU-only library from
the official <https://github.com/microsoft/onnxruntime> release `v1.26.0`, which
is licensed under the MIT License. Its license and third-party notices are
copied verbatim from the pinned release archive. The bundle's manifest and SBOM
identify the exact archive and library.

## OmniParser icon detector

The converted icon detector derives from Microsoft OmniParser v2.0 revision
`f55d0750e5b94db2125ef0b45b0fa4a85ddc59b4`, file `icon_detect_v3/model.pt`.
Microsoft trained it from YOLOv9-E with the MIT-licensed
MultimediaTechLab/YOLO implementation and publishes it under the MIT License,
in `icon_detect_v3/LICENSE` at that revision. The license text is copied
verbatim into `licenses/MIT-OmniParser-icon_detect_v3.txt`. Copyright (c)
Microsoft Corporation.

The conversion wraps the published TorchScript module with the decoding from
the upstream model card and exports it to ONNX with PyTorch. No Ultralytics
code, weights, or exporter source is used or shipped. The earlier AGPL-3.0
`icon_detect` detector is not part of this bundle, and the release check
rejects its known digests.

## PaddleOCR models and dictionary

The PP-OCRv5 mobile detector, English recognizer, and recognizer dictionary
derive from `PaddlePaddle/PP-OCRv5_mobile_det_onnx` revision
`e6f4fa85f00e168c862bc462aebca69eef9b3d3d` and
`PaddlePaddle/en_PP-OCRv5_mobile_rec_onnx` revision
`3fafbc3b5dcf93dd72add9f48368be8a3a2cd33b`. These artifacts are licensed under
the Apache License 2.0.

The components are provided without warranty, as their licenses state. This
notice is informational, is not legal advice, and does not replace the
applicable licenses.
