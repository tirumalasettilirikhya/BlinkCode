# 👁️ BlinkCode

### Your Eyes. Your Language.

**BlinkCode** is a Python-based eye-blink Morse code recognition application that converts eye-blink patterns into Morse code and then into readable text.

Using computer vision and facial landmark detection, BlinkCode monitors eye movements through a webcam and recognizes Morse signals.

The project explores how computer vision can support alternative communication methods through simple eye-blink interactions.

---

## ✨ Features

- 📷 **Live Webcam Detection** – Capture real-time video through a webcam.
- 👁️ **Eye Detection** – Identify whether the eyes are open or closed.
- • **Morse Signal Recognition** – Recognize dots and dashes from eye-blink patterns.
- 🔤 **Text Decoding** – Convert Morse code into readable letters, numbers and supported symbols.
- 🎬 **Interactive GUI** – User-friendly dark interface inspired by streaming platforms.
- 📜 **Morse History** – View previously decoded messages.
- 🧹 **Clear Controls** – Clear the current output or message history.
- ⏯️ **Morse Mode** – Enable or disable Morse recognition whenever needed.

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| OpenCV | Webcam access and image processing |
| MediaPipe | Facial landmark detection |
| NumPy | Numerical calculations |
| Tkinter | Graphical user interface |
| Pillow | Displaying camera frames |

---

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
```

---

## ⚙️ Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/tirumalasettilirikhya/BlinkCode.git
```

### 2. Navigate to the project folder

```bash
cd BlinkCode
```

### 3. Install the required libraries

```bash
py -m pip install opencv-python mediapipe numpy Pillow
```

### 4. Run the application

```bash
py morse/gui.py
```

**Note:** A working webcam is required to use the live eye-detection feature.

---

## 🚀 How to Use

1. Launch the BlinkCode application.
2. Click **START CAMERA**.
3. Allow webcam access if prompted.
4. Enable **MORSE MODE**.
5. Use comfortable, natural eye movements to enter Morse signals.
6. View the recognized Morse code and decoded text.
7. Check previously decoded messages in the Morse History panel.

---

## 🧠 How It Works

BlinkCode follows this processing pipeline:

**Webcam Input → Facial Landmark Detection → Eye State Detection → Morse Signal Recognition → Morse Code Decoding → Text Output**

The webcam captures facial images, facial landmarks help identify eye positions, and the application uses eye-state changes to recognize Morse signals.

---

## 🔮 Future Improvements

- Permanent storage of decoded messages.
- Adjustable