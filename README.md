# AI Aimbot Experiment (YOLO26n + GPU + GUI)

This project is a Windows computer-vision experiment pipeline:
window capture -> person detection -> target selection -> mouse movement.

## Highlights

- modular runtime split by major categories:
  - `resource` (screen/model I/O)
  - `utils` (selection logic)
  - `hooks` (F12 runtime toggle)
  - `interface` (detection + box visualization)
- lightweight YOLO model path defaulted to `yolo26n.pt`
- CUDA auto-detection for GPU acceleration (falls back to CPU)
- live OpenCV detection GUI with bounding boxes and FPS
- F12 toggles aimbot enabled/disabled while running
- open-source license included in `LICENSE` (Apache 2.0)

## Project Layout

```text
.
├── aimbot.py
├── config.yaml
├── requirements.txt
├── LICENSE
└── src/
    └── aimbot/
        ├── hooks/
        ├── interface/
        ├── resource/
        ├── utils/
        ├── config.py
        ├── controller.py
        └── main.py
```

## Install

```bash
pip install -r requirements.txt
```

For GTX 1060 CUDA acceleration, install a CUDA-enabled PyTorch build appropriate for your driver/CUDA toolkit before running.

## Run

```bash
python aimbot.py --config config.yaml
```

## Runtime Controls

- `F12`: toggle aimbot on/off
- `Q` or `Esc`: quit
