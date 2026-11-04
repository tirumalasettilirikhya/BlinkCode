
import cv2
import mediapipe as mp
import numpy as np
import time
from pathlib import Path

from decoder import decode_morse


class BlinkMorseDetector:

    def __init__(self):

        # -----------------------------
        # MEDIAPIPE SETUP
        # -----------------------------

        BaseOptions = mp.tasks.BaseOptions
        FaceLandmarker = mp.tasks.vision.FaceLandmarker
        FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode

        model_path = Path(__file__).with_name("face_landmarker.task")

        options = FaceLandmarkerOptions(
            base_options=BaseOptions(
                model_asset_path=str(model_path)
            ),
            running_mode=VisionRunningMode.VIDEO,
            num_faces=1
        )

        self.landmarker = FaceLandmarker.create_from_options(options)

        # -----------------------------
        # EYE LANDMARK POINTS
        # -----------------------------

        self.left_eye = [362, 385, 387, 263, 373, 380]
        self.right_eye = [33, 160, 158, 133, 153, 144]

        # -----------------------------
        # SETTINGS
        # -----------------------------

        self.ear_threshold = 0.20
        self.stability_time = 0.08

        self.dot_dash_threshold = 0.35

        self.letter_gap = 1.0
        self.word_gap = 2.5

        # -----------------------------
        # STATE VARIABLES
        # -----------------------------

        self.eye_status = "OPEN"
        self.candidate_status = "OPEN"
        self.candidate_since = time.monotonic()

        self.closed_since = None

        # -----------------------------
        # MORSE VARIABLES
        # -----------------------------

        self.morse_mode = False

        self.morse_sequence = []
        self.decoded_text = ""

        self.last_symbol_time = None

        self.letter_finished = False
        self.word_finished = False

        self.last_timestamp_ms = 0

    # -----------------------------
    # CALCULATE EYE ASPECT RATIO
    # -----------------------------

    def calculate_ear(self, points):

        p1, p2, p3, p4, p5, p6 = points

        vertical_1 = np.linalg.norm(p2 - p6)
        vertical_2 = np.linalg.norm(p3 - p5)
        horizontal = np.linalg.norm(p1 - p4)

        if horizontal == 0:
            return 0

        return (vertical_1 + vertical_2) / (2 * horizontal)

    # -----------------------------
    # TURN MORSE MODE ON OR OFF
    # -----------------------------

    def set_morse_mode(self, enabled):

        self.morse_mode = enabled

        self.morse_sequence.clear()
        self.last_symbol_time = None

        self.letter_finished = False
        self.word_finished = False

        self.closed_since = None

        self.eye_status = "OPEN"
        self.candidate_status = "OPEN"
        self.candidate_since = time.monotonic()

    # -----------------------------
    # CLEAR MORSE INPUT
    # -----------------------------

    def clear(self):

        self.morse_sequence.clear()
        self.decoded_text = ""

        self.last_symbol_time = None

        self.letter_finished = False
        self.word_finished = False

        self.closed_since = None

    # -----------------------------
    # PROCESS CAMERA FRAME
    # -----------------------------

    def process_frame(self, frame):

        current_time = time.monotonic()

        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )

        timestamp_ms = int(current_time * 1000)

        # MediaPipe requires increasing timestamps.
        if timestamp_ms <= self.last_timestamp_ms:
            timestamp_ms = self.last_timestamp_ms + 1

        self.last_timestamp_ms = timestamp_ms

        result = self.landmarker.detect_for_video(
            mp_image,
            timestamp_ms
        )

        face_detected = False

        # -----------------------------
        # FACE AND EYE DETECTION
        # -----------------------------

        if result.face_landmarks:

            face_detected = True

            landmarks = result.face_landmarks[0]

            height, width, _ = frame.shape

            left_points = np.array([
                [
                    landmarks[i].x * width,
                    landmarks[i].y * height
                ]
                for i in self.left_eye
            ])

            right_points = np.array([
                [
                    landmarks[i].x * width,
                    landmarks[i].y * height
                ]
                for i in self.right_eye
            ])

            # Calculate EAR for both eyes.

            left_ear = self.calculate_ear(left_points)
            right_ear = self.calculate_ear(right_points)

            ear = (left_ear + right_ear) / 2

            # -----------------------------
            # OPEN OR CLOSED EYE DETECTION
            # -----------------------------

            if ear < self.ear_threshold:
                new_status = "CLOSED"
            else:
                new_status = "OPEN"

            # Stability check.

            if new_status != self.candidate_status:

                self.candidate_status = new_status
                self.candidate_since = current_time

            if (
                current_time - self.candidate_since
                >= self.stability_time
            ):

                if self.candidate_status != self.eye_status:

                    self.eye_status = self.candidate_status

                    # When eyes close.

                    if self.eye_status == "CLOSED":

                        self.closed_since = current_time

                    # When eyes open again.

                    else:

                        if self.closed_since is not None:

                            duration = (
                                current_time - self.closed_since
                            )

                            if self.morse_mode:

                                # Convert closure into dot or dash.

                                if duration < self.dot_dash_threshold:
                                    symbol = "."
                                else:
                                    symbol = "-"

                                self.morse_sequence.append(symbol)

                                self.last_symbol_time = current_time

                                self.letter_finished = False
                                self.word_finished = False

                            self.closed_since = None

            # -----------------------------
            # DRAW EYE LANDMARKS
            # -----------------------------

            for point in np.concatenate(
                (left_points, right_points)
            ):

                cv2.circle(
                    frame,
                    (int(point[0]), int(point[1])),
                    2,
                    (0, 255, 0),
                    -1
                )

            cv2.putText(
                frame,
                f"EAR: {ear:.3f} | Eyes: {self.eye_status}",
                (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

        else:

            cv2.putText(
                frame,
                "No face detected",
                (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2
            )

        # -----------------------------
        # LETTER AND WORD DETECTION
        # -----------------------------

        if (
            face_detected
            and self.morse_mode
            and self.eye_status == "OPEN"
            and self.last_symbol_time is not None
            and (self.morse_sequence or self.letter_finished)
        ):

            gap = current_time - self.last_symbol_time

            # Finish the current letter.

            if (
                gap >= self.letter_gap
                and self.morse_sequence
                and not self.letter_finished
            ):

                pattern = "".join(self.morse_sequence)

                letter = decode_morse(pattern)

                self.decoded_text += letter

                self.morse_sequence.clear()

                self.letter_finished = True

            # Finish the current word.

            if (
                gap >= self.word_gap
                and self.letter_finished
                and not self.word_finished
            ):

                if (
                    self.decoded_text
                    and not self.decoded_text.endswith(" ")
                ):
                    self.decoded_text += " "

                self.word_finished = True

        # -----------------------------
        # DISPLAY MORSE INFORMATION
        # -----------------------------

        mode_text = "ON" if self.morse_mode else "OFF"

        cv2.putText(
            frame,
            f"Morse Mode: {mode_text}",
            (20, 65),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 255),
            2
        )

        cv2.putText(
            frame,
            "Morse: " + "".join(self.morse_sequence),
            (20, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 0),
            2
        )

        cv2.putText(
            frame,
            "Text: " + self.decoded_text[-30:],
            (20, 135),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

        return frame

    # -----------------------------
    # CLOSE MEDIAPIPE
    # -----------------------------

    def close(self):

        if self.landmarker is not None:
            self.landmarker.close()
            self.landmarker = None
