# Refactoring Plan (Modernized + Low-End PC Friendly)

## 1. Baseline and Safety
- [ ] Add a clear project disclaimer and intended non-malicious usage scope.
- [ ] Measure current baseline: capture FPS, inference latency, control loop latency, CPU/GPU usage.
- [ ] Add basic runtime guards (window not found, empty frame, model load failure, inference timeout).
- [ ] Add graceful shutdown and logging initialization.

## 2. Project Structure Refactor
- [ ] Split monolithic script into modules:
- [ ] `src/capture.py` (screen/window capture)
- [ ] `src/detector.py` (model loading + inference)
- [ ] `src/target_selector.py` (target scoring and tracking state)
- [ ] `src/controller.py` (mouse movement + click policy)
- [ ] `src/main.py` (orchestration loop)
- [ ] Move constants into `config.yaml` (thresholds, ROI, smoothing, timing).

## 3. Capture Pipeline Upgrade
- [ ] Replace `pyautogui.screenshot` with `mss` for lower-latency capture.
- [ ] Support fixed central ROI capture (e.g., 512x512 or 640x640) to reduce compute.
- [ ] Add optional dynamic ROI following last known target position.
- [ ] Normalize color format once in capture stage (avoid repeated conversion overhead).

## 4. Detection Model Modernization
- [ ] Replace legacy TF Hub detector with a lightweight modern detector (nano/small tier).
- [ ] Export/convert model to ONNX for deployment-focused inference.
- [ ] Add ONNX Runtime backend with provider fallback (CUDA -> CPU).
- [ ] Add confidence threshold + class filtering from config.
- [ ] Benchmark model variants and keep a performance comparison table.

## 5. Low-End Performance Optimizations
- [ ] Add frame-skipping strategy: detect every `N` frames, track in between.
- [ ] Add simple tracker fallback (Kalman / KCF / CSRT) between detector updates.
- [ ] Add asynchronous pipeline:
- [ ] Capture thread/process
- [ ] Inference worker
- [ ] Control worker
- [ ] Add adaptive quality mode (auto-reduce resolution/FPS under high load).
- [ ] Add optional INT8 quantized model path for CPU-only systems.

## 6. Target Selection and Control Quality
- [ ] Replace nearest-center-only logic with score-based target ranking:
- [ ] Confidence term
- [ ] Distance penalty
- [ ] Temporal consistency/stickiness term
- [ ] Add smoothing/PID-style motion to reduce overshoot and jitter.
- [ ] Add configurable click policy with cooldown/debounce.
- [ ] Add deadzone handling to prevent micro-oscillation near center.

## 7. Config, CLI, and Developer UX
- [ ] Add CLI options (`--config`, `--debug`, `--benchmark`, `--headless`).
- [ ] Add live debug overlay toggle (boxes, selected target, FPS/latency text).
- [ ] Add deterministic test mode using recorded frames/video input.
- [ ] Document environment setup and OS-specific dependencies.

## 8. Validation and Regression Checks
- [ ] Add repeatable benchmark script (same scene, fixed duration, CSV output).
- [ ] Track key metrics: capture FPS, inference FPS, end-to-end latency, target stability.
- [ ] Add smoke tests for module imports and basic data flow.
- [ ] Add simple config validation test.

## 9. Documentation and Deliverables
- [ ] Update `README.md` with architecture diagram and module responsibilities.
- [ ] Add model card section (input size, classes, expected throughput on low-end hardware).
- [ ] Add tuning guide (how to trade accuracy vs latency).
- [ ] Add changelog section for each optimization milestone.

## 10. Suggested Milestones
- [ ] Milestone 1: Modular refactor + config + baseline metrics.
- [ ] Milestone 2: `mss` capture + ONNX detector + ROI optimization.
- [ ] Milestone 3: Async pipeline + frame skipping + tracker.
- [ ] Milestone 4: Control smoothing + benchmark/report finalization.
