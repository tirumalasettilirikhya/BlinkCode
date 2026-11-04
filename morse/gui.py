
import tkinter as tk
from tkinter import messagebox
import cv2

from PIL import Image, ImageTk
from vision.eye_detection import BlinkMorseDetector


# -----------------------------
# MAIN WINDOW
# -----------------------------

root = tk.Tk()
root.title("BlinkCode | Eye Blink Morse Recognition")
root.geometry("1150x850")
root.minsize(950, 750)
root.configure(bg="#101010")


# -----------------------------
# COLORS
# -----------------------------

BG = "#101010"
CARD = "#202020"
RED = "#E50914"
WHITE = "#FFFFFF"
GREY = "#AAAAAA"
GREEN = "#46C37B"


# -----------------------------
# CAMERA VARIABLES
# -----------------------------

camera = None
detector = None

camera_running = False
morse_mode_enabled = False

last_seen_decoded = ""
history_current_line = ""


# -----------------------------
# LABEL HELPER
# -----------------------------

def create_label(parent, text, size, color,
                 weight="normal", bg=CARD):

    return tk.Label(
        parent,
        text=text,
        font=("Arial", size, weight),
        fg=color,
        bg=bg
    )


# -----------------------------
# HEADER
# -----------------------------

header = tk.Frame(root, bg=BG)
header.pack(fill="x", padx=35, pady=12)

create_label(
    header, "BLINK", 25, RED, "bold", BG
).pack(side="left")

create_label(
    header, "CODE", 25, WHITE, "bold", BG
).pack(side="left")

create_label(
    header,
    "EYE BLINK MORSE RECOGNITION",
    10, GREY, "bold", BG
).pack(side="right", pady=10)


# -----------------------------
# WELCOME SECTION
# -----------------------------

welcome = tk.Frame(root, bg=BG)
welcome.pack(fill="x", padx=35, pady=5)

create_label(
    welcome,
    "YOUR EYES. YOUR LANGUAGE.",
    25, WHITE, "bold", BG
).pack(anchor="w")

create_label(
    welcome,
    "Communicate through Morse code using eye blinks.",
    12, GREY, bg=BG
).pack(anchor="w", pady=5)


# -----------------------------
# MAIN CONTENT
# -----------------------------

main = tk.Frame(root, bg=BG)

main.pack(
    fill="both",
    expand=True,
    padx=35,
    pady=5
)

left = tk.Frame(main, bg=CARD)

left.pack(
    side="left",
    fill="both",
    expand=True,
    padx=(0, 12)
)

right = tk.Frame(main, bg=BG)

right.pack(
    side="right",
    fill="both",
    expand=True,
    padx=(12, 0)
)


# -----------------------------
# CAMERA CARD
# -----------------------------

create_label(
    left,
    "LIVE CAMERA",
    15, WHITE, "bold"
).pack(anchor="w", padx=20, pady=12)

camera_screen = tk.Label(
    left,
    text="◉\n\nCAMERA NOT STARTED",
    font=("Arial", 17, "bold"),
    fg=GREY,
    bg="#080808",
    width=35,
    height=8
)

camera_screen.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=8
)

camera_status = create_label(
    left, "● CAMERA OFF", 10, GREY
)

camera_status.pack(
    anchor="w", padx=20, pady=5
)

eye_status_label = create_label(
    left, "EYES: WAITING", 10, GREY
)

eye_status_label.pack(
    anchor="w", padx=20, pady=(0, 10)
)


# -----------------------------
# MORSE OUTPUT CARD
# -----------------------------

morse_card = tk.Frame(right, bg=CARD)
morse_card.pack(fill="x", pady=(0, 10))

create_label(
    morse_card,
    "MORSE OUTPUT",
    14, WHITE, "bold"
).pack(anchor="w", padx=20, pady=10)

morse_text = create_label(
    morse_card,
    "Waiting for input...",
    20, RED, "bold"
)

morse_text.pack(
    anchor="w", padx=20, pady=10
)


# -----------------------------
# DECODED MESSAGE CARD
# -----------------------------

message_card = tk.Frame(right, bg=CARD)
message_card.pack(fill="x", pady=(0, 10))

create_label(
    message_card,
    "DECODED MESSAGE",
    14, WHITE, "bold"
).pack(anchor="w", padx=20, pady=10)

decoded_text = create_label(
    message_card,
    "Your message will appear here.",
    17, WHITE
)

decoded_text.pack(
    anchor="w", padx=20, pady=10
)


# -----------------------------
# MORSE HISTORY CARD
# -----------------------------

history_card = tk.Frame(right, bg=CARD)

history_card.pack(
    fill="both",
    expand=True
)

history_header = tk.Frame(
    history_card,
    bg=CARD
)

history_header.pack(
    fill="x",
    padx=15,
    pady=10
)

create_label(
    history_header,
    "MORSE HISTORY",
    14, WHITE, "bold"
).pack(side="left")

create_label(
    history_header,
    "RECENT WORDS",
    9, GREY, "bold"
).pack(side="right")


# History list and scrollbar

history_container = tk.Frame(
    history_card,
    bg=CARD
)

history_container.pack(
    fill="both",
    expand=True,
    padx=15,
    pady=(0, 12)
)

history_scrollbar = tk.Scrollbar(
    history_container
)

history_scrollbar.pack(
    side="right",
    fill="y"
)

history_list = tk.Listbox(
    history_container,
    bg="#151515",
    fg=WHITE,
    font=("Arial", 13),
    selectbackground=RED,
    borderwidth=0,
    highlightthickness=0,
    yscrollcommand=history_scrollbar.set
)

history_list.pack(
    side="left",
    fill="both",
    expand=True
)

history_scrollbar.config(
    command=history_list.yview
)


# -----------------------------
# MODE STATUS
# -----------------------------

mode_status = create_label(
    right,
    "MORSE MODE: OFF",
    11, GREY, "bold", BG
)

mode_status.pack(
    anchor="w",
    pady=8
)


# -----------------------------
# HISTORY UPDATE FUNCTION
# -----------------------------

def update_history(current_text):

    global last_seen_decoded
    global history_current_line

    # Handle a cleared or reset message.

    if len(current_text) < len(last_seen_decoded):

        last_seen_decoded = ""
        history_current_line = ""

    # Find only the newly decoded characters.

    if current_text.startswith(last_seen_decoded):

        new_text = current_text[len(last_seen_decoded):]

    else:

        new_text = current_text
        history_current_line = ""

    last_seen_decoded = current_text

    for character in new_text:

        if character.isspace():

            history_current_line = ""
            continue

        history_current_line += character

        # Update the current word instead of
        # creating a separate entry for every letter.

        if history_list.size() > 0:

            if history_list.get("end") == history_current_line:
                continue

            if history_current_line[:-1] == history_list.get("end"):
                history_list.delete("end")

        history_list.insert(
            "end",
            history_current_line
        )

        history_list.yview_moveto(1)


# -----------------------------
# CLEAR HISTORY
# -----------------------------

def clear_history():

    global history_current_line

    history_list.delete(0, "end")
    history_current_line = ""


# -----------------------------
# UPDATE CAMERA
# -----------------------------

def update_camera():

    if not camera_running or camera is None:
        return

    success, frame = camera.read()

    if success:

        if detector is not None:

            frame = detector.process_frame(frame)

            eye_status_label.configure(
                text="EYES: " + detector.eye_status
            )

            current_morse = "".join(
                detector.morse_sequence
            )

            if current_morse:

                morse_text.configure(
                    text=current_morse
                )

            else:

                morse_text.configure(
                    text="Waiting for input..."
                )

            current_message = detector.decoded_text

            if current_message.strip():

                decoded_text.configure(
                    text=current_message
                )

                update_history(current_message)

            else:

                decoded_text.configure(
                    text="Your message will appear here."
                )

        # Convert camera frame for Tkinter.

        frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        image = Image.fromarray(frame)
        image = image.resize((500, 350))

        photo = ImageTk.PhotoImage(image=image)

        camera_screen.configure(
            image=photo,
            text=""
        )

        camera_screen.image = photo

    root.after(20, update_camera)


# -----------------------------
# START CAMERA
# -----------------------------

def start_camera():

    global camera
    global detector
    global camera_running

    if camera_running:
        return

    try:

        camera = cv2.VideoCapture(0)

        if not camera.isOpened():

            camera_status.configure(
                text="● CAMERA ERROR",
                fg=RED
            )

            camera.release()
            camera = None
            return

        detector = BlinkMorseDetector()

        detector.set_morse_mode(
            morse_mode_enabled
        )

        camera_running = True

        camera_status.configure(
            text="● CAMERA ON",
            fg=GREEN
        )

        update_camera()

    except Exception as error:

        print("Camera startup error:", error)

        if camera is not None:
            camera.release()
            camera = None

        if detector is not None:
            detector.close()
            detector = None

        camera_running = False

        camera_status.configure(
            text="● STARTUP ERROR",
            fg=RED
        )


# -----------------------------
# STOP CAMERA
# -----------------------------

def stop_camera():

    global camera
    global detector
    global camera_running
    global morse_mode_enabled
    global last_seen_decoded
    global history_current_line

    camera_running = False

    if camera is not None:

        camera.release()
        camera = None

    if detector is not None:

        detector.close()
        detector = None

    morse_mode_enabled = False
    last_seen_decoded = ""
    history_current_line = ""

    camera_screen.configure(
        image="",
        text="◉\n\nCAMERA NOT STARTED"
    )

    camera_screen.image = None

    camera_status.configure(
        text="● CAMERA OFF",
        fg=GREY
    )

    eye_status_label.configure(
        text="EYES: WAITING"
    )

    morse_text.configure(
        text="Waiting for input..."
    )

    decoded_text.configure(
        text="Your message will appear here."
    )

    mode_status.configure(
        text="MORSE MODE: OFF",
        fg=GREY
    )

    mode_button.configure(
        text="ENABLE MORSE MODE"
    )


# -----------------------------
# TOGGLE MORSE MODE
# -----------------------------

def toggle_morse_mode():

    global morse_mode_enabled

    morse_mode_enabled = not morse_mode_enabled

    if detector is not None:

        detector.set_morse_mode(
            morse_mode_enabled
        )

    if morse_mode_enabled:

        mode_status.configure(
            text="MORSE MODE: ON",
            fg=GREEN
        )

        mode_button.configure(
            text="DISABLE MORSE MODE"
        )

        morse_text.configure(
            text="Ready for Morse input..."
        )

    else:

        mode_status.configure(
            text="MORSE MODE: OFF",
            fg=GREY
        )

        mode_button.configure(
            text="ENABLE MORSE MODE"
        )

        morse_text.configure(
            text="Morse mode disabled."
        )


# -----------------------------
# CLEAR CURRENT OUTPUT
# -----------------------------

def clear_output():

    global last_seen_decoded
    global history_current_line

    if detector is not None:
        detector.clear()

    last_seen_decoded = ""
    history_current_line = ""

    morse_text.configure(
        text="Waiting for input..."
    )

    decoded_text.configure(
        text="Your message will appear here."
    )


# -----------------------------
# FOOTER
# -----------------------------

footer = create_label(
    root,
    "BLINKCODE | COMMUNICATE BEYOND WORDS",
    9, GREY, bg=BG
)

footer.pack(
    side="bottom",
    pady=5
)


# -----------------------------
# BUTTONS
# -----------------------------

buttons = tk.Frame(root, bg=BG)

buttons.pack(
    side="bottom",
    pady=8
)


start_button = tk.Button(
    buttons,
    text="▶ START CAMERA",
    command=start_camera,
    bg=RED,
    fg=WHITE,
    font=("Arial", 10, "bold"),
    padx=12,
    pady=9,
    relief="flat"
)

start_button.pack(side="left", padx=4)


stop_button = tk.Button(
    buttons,
    text="■ STOP CAMERA",
    command=stop_camera,
    bg="#333333",
    fg=WHITE,
    font=("Arial", 10, "bold"),
    padx=12,
    pady=9,
    relief="flat"
)

stop_button.pack(side="left", padx=4)


mode_button = tk.Button(
    buttons,
    text="ENABLE MORSE MODE",
    command=toggle_morse_mode,
    bg="#333333",
    fg=WHITE,
    font=("Arial", 10, "bold"),
    padx=12,
    pady=9,
    relief="flat"
)

mode_button.pack(side="left", padx=4)


clear_button = tk.Button(
    buttons,
    text="CLEAR",
    command=clear_output,
    bg="#333333",
    fg=WHITE,
    font=("Arial", 10, "bold"),
    padx=12,
    pady=9,
    relief="flat"
)

clear_button.pack(side="left", padx=4)


history_clear_button = tk.Button(
    buttons,
    text="CLEAR HISTORY",
    command=clear_history,
    bg="#333333",
    fg=WHITE,
    font=("Arial", 10, "bold"),
    padx=12,
    pady=9,
    relief="flat"
)

history_clear_button.pack(side="left", padx=4)


# -----------------------------
# CLOSE APPLICATION
# -----------------------------

def on_close():

    stop_camera()
    root.destroy()


root.protocol(
    "WM_DELETE_WINDOW",
    on_close
)


# -----------------------------
# RUN APPLICATION
# -----------------------------

root.mainloop()
