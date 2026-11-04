# 👁️ BlinkCode
### Your Eyes. Your Language.

BlinkCode is a Python-based eye-blink Morse code recognition application.

It uses computer vision to detect eye blinks through a webcam and converts them into Morse code and readable text.

## ✨ Features

- Live webcam detection
- Eye open/closed status monitoring
- Morse dot and dash recognition
- Morse code to text conversion
- Dark, Netflix-inspired GUI
- Morse history
- Clear message and history controls
- Enable/disable Morse mode

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| OpenCV | Webcam and image processing |
| MediaPipe | Facial landmark detection |
| NumPy | Numerical calculations |
| Tkinter | Graphical interface |
| Pillow | Displaying camera frames |

## 📁 Project Structure

```text
BlinkCode/
├── README.md
└── morse/
    ├── .gitignore
    ├── gui.py
    ├── decoder.py
    └── vision/
        ├── camera_test.py
        ├── eye_detection.py
        ├── face_detection.py
        └── face_landmarker.task