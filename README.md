# 🖐️ Kinetic-OS
### Modular Hand-Tracking API & Virtual Interface

> A high-performance Computer Vision framework that converts real-time hand gestures into precise system-level commands.

Kinetic-OS is a modular hand-tracking API built on MediaPipe that powers a smooth, low-latency virtual mouse and diagnostic telemetry system.  
Designed with scalability, performance, and ML-integration in mind.

---

## 🎯 Highlights

- 🖱️ Smooth virtual mouse with zero-jitter interpolation
- ✌️ Gesture-based clicking & scrolling
- 🔴 Safety kill-switch gesture
- 📊 Built-in landmark data logger (CSV export)
- ⚙️ JSON-based persistent configuration system
- 🧠 ML-ready architecture

---

# 🏗️ System Architecture

Kinetic-OS follows a decoupled layered architecture to ensure maintainability and modularity.

```
Camera Input
     ↓
HandTrackingModule (Core Engine)
     ↓
Gesture Logic (AIMouse)
     ↓
OS Cursor / Scroll Events
```

---

## 🔹 Core Engine — `HandTrackingModule.py`

- MediaPipe landmark extraction
- Skeletal rendering
- Binary finger-state detection
- Clean, reusable API

---

## 🔹 Logic Layer — `AIMouse.py`

- Linear Interpolation (Lerp) smoothing
- Asymmetrical spatial mapping
- Gesture-to-command translation
- Cursor stabilization

---

## 🔹 Control Layer — `MouseSettingsGUI.py`

- CustomTkinter dashboard
- Persistent `settings.json`
- Adjustable margins & sensitivity

---

## 🔹 Diagnostic Layer — `HandTrackingGUI.py`

- Real-time landmark telemetry
- Debug visualization
- CSV dataset generation (`hand_data_log.csv`)

---

# 🚀 Gesture System

| Gesture | Action |
|----------|--------|
| ☝️ Index Finger | Cursor movement |
| ✌️ Index + Middle Join | Left Click |
| 🖐️ Four Fingers | Vertical Scroll |
| 🤏 Pinky Extension | Kill-Switch |

---

# ⚙️ Performance Optimizations

## 🔹 Asymmetrical Margins
Tracking zone is biased upward to compensate for webcam Field of View (FOV) limitations.

This allows full bottom-screen access without losing landmark visibility.

## 🔹 Low-Latency Execution
Optimized for:
- Intel i7-6600U (dual-core)
- Windows 10/11
- Minimal per-frame calculations
- Efficient NumPy vector operations

---

# 🧮 Spatial Interpolation

To bridge resolution differences:

Camera: `640x480`  
Screen: `1920x1080`

Weighted interpolation:

```
x_screen = interp(x_finger, [margin, W - margin], [0, ScreenWidth])
```

Ensures stable and resolution-aware mapping.

---

# 📊 Data-Driven Design

Landmarks are exported to:

```
hand_data_log.csv
```

This enables:

- Classical ML integration (Scikit-Learn)
- Deep Learning models (TensorFlow)
- Gesture classifier training
- Future LSTM-based temporal recognition

Hardcoded gesture logic can be replaced with trained models.

---

# 📦 Installation

```bash
pip install opencv-python mediapipe pyautogui customtkinter Pillow numpy
```

---

# ▶ Usage

### 1️⃣ Configure Sensitivity
```bash
python MouseSettingsGUI.py
```

### 2️⃣ Launch Virtual Mouse
```bash
python AIMouse.py
```

---

# 📂 Project Structure

```
Kinetic-OS/
│
|-- hand_landmarker.task  # MediaPipe API file
├── HandTrackingModule.py   # Core API
├── AIMouse.py              # Virtual Mouse Logic
├── MouseSettingsGUI.py     # Settings Dashboard
├── HTM_GUI.py      # Telemetry & Logger
├── settings.json           # Persistent Configuration
└── hand_data_log.csv     # Generated Dataset
```

---

# 🎓 Academic Context

**Developer:** github/i-hmzakhan  
**Institution:** University of Engineering & Applied Sciences (UEAS), Swat  
**Environment Target:** Windows 10/11 on mobile i7 hardware  

---

# 🔮 Future Roadmap

- [ ] ML-based gesture classification
- [ ] Multi-hand support
- [ ] Plugin gesture architecture
- [ ] Cross-platform abstraction
- [ ] Latency benchmarking study
- [ ] User evaluation & accuracy metrics

---

# ⭐ Why This Project Matters

Kinetic-OS is not just a gesture demo.

It is:

- A reusable hand-tracking engine  
- A lightweight HCI middleware prototype  
- A foundation for adaptive AI-based gesture systems  

---

# 📜 License

MIT License 

---

If you find this project interesting, consider giving it a ⭐

