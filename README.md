# Tensorflow Hub Aimbot (Refactor Scaffold)

Computer-vision experiment project with a real-time loop:
window capture -> person detection -> target selection -> mouse control.

## Current Branch Status

This repository now includes an initial v2 refactor scaffold focused on:

- module separation (`capture`, `detector`, `target_selector`, `controller`, `main`)
- externalized runtime config (`config.yaml`)
- legacy entrypoint compatibility (`aimbot.py`)
- Apache License 2.0 notice metadata (`NOTICE`)

## Project Layout

```text
.
├── aimbot.py
├── config.yaml
├── requirements.txt
├── src/
│   └── aimbot/
│       ├── capture.py
│       ├── config.py
│       ├── controller.py
│       ├── detector.py
│       ├── main.py
│       └── target_selector.py
└── TODO.md
```

## Run

```bash
pip install -r requirements.txt
python aimbot.py --config config.yaml
```

## Notes

- Windows-specific dependencies are required (`pywin32`).
- This branch is a restructuring baseline before model/runtime modernization.
