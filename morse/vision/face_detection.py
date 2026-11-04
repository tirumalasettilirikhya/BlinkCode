
import cv2
import mediapipe as mp
import time
from pathlib import Path

# Locate the downloaded model
model_path = Path(__file__).with_name("face_landmarker.task")

# Configure MediaPipe
BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
Options = mp.tasks.vision.FaceLandmarkerOptions
RunningMode = mp.tasks.vision.RunningMode

options = Options(
    base_options=BaseOptions(model_asset_path=str(model_path)),
    running_mode=RunningMode.VIDEO,
    num_faces=1,
    min_face_detection_confidence=0.3,
    min_face_presence_confidence=0.3,
    min_tracking_confidence=0.3
)
# Open webcam using DirectShow on Windows
camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not camera.isOpened():
    print("Could not open webcam")
    raise SystemExit

start_time = time.perf_counter()

try:
    with FaceLandmarker.create_from_options(options) as landmarker:

        while True:
            success, frame = camera.read()

            if not success:
                print("Could not read camera frame")
                break

            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(
                frame, cv2.COLOR_BGR2RGB
            )

            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=rgb_frame
            )

            # Detect facial landmarks
            timestamp = int(
                (time.perf_counter() - start_time) * 1000
            )

            result = landmarker.detect_for_video(
                mp_image, timestamp
            )

            if result.face_landmarks:

                left_eye = [362, 385, 387, 263, 373, 380]
                right_eye = [33, 160, 158, 133, 153, 144]

                for face in result.face_landmarks:

                    for eye in [left_eye, right_eye]:

                        points = []

                        for index in eye:
                            landmark = face[index]

                            x = int(
                                landmark.x * frame.shape[1]
                            )
                            y = int(
                                landmark.y * frame.shape[0]
                            )

                            points.append((x, y))

                        # Draw eye outline
                        for i in range(6):
                            cv2.line(
                                frame,
                                points[i],
                                points[(i + 1) % 6],
                                (0, 255, 0),
                                2
                            )

                        # Draw eye landmarks
                        for point in points:
                            cv2.circle(
                                frame,
                                point,
                                3,
                                (0, 0, 255),
                                -1
                            )

                cv2.putText(
                    frame,
                    "Eyes Detected",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2
                )

            else:
                cv2.putText(
                    frame,
                    "No Face Detected",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    2
                )

            cv2.imshow("Eye Landmark Detection", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

finally:
    camera.release()
    cv2.destroyAllWindows()
