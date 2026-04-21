import cv2
import numpy as np
import time
import os
import sys
import math
import threading
from dotenv import load_dotenv

# ==============================
# RESOLUÇÃO (SEM TKINTER)
# ==============================

def get_screen_resolution():
    width = int(os.getenv("SCREEN_WIDTH", 1920))
    height = int(os.getenv("SCREEN_HEIGHT", 1080))
    return width, height


SCREEN_WIDTH, SCREEN_HEIGHT = get_screen_resolution()

# ==============================
# CARREGAR CAMERAS
# ==============================

load_dotenv()

CAMERAS = [
    value for key, value in sorted(os.environ.items())
    if key.startswith("CAM")
]

if not CAMERAS:
    print("Nenhuma câmera encontrada.")
    sys.exit(1)

CAM_COUNT = len(CAMERAS)

WINDOW_NAME = "Central CFTV"
RESTART_TIME = 5 * 60

# ==============================
# GRID AUTOMÁTICO
# ==============================

def calculate_grid(n):
    cols = math.ceil(math.sqrt(n))
    rows = math.ceil(n / cols)
    return rows, cols


GRID_ROWS, GRID_COLS = calculate_grid(CAM_COUNT)

CELL_WIDTH = SCREEN_WIDTH // GRID_COLS
CELL_HEIGHT = SCREEN_HEIGHT // GRID_ROWS
FRAME_SIZE = (CELL_WIDTH, CELL_HEIGHT)

# ==============================
# CAMERA THREAD
# ==============================

class CameraStream:

    def __init__(self, url, index):
        self.url = url
        self.index = index
        self.frame = self.black_frame()
        self.running = True
        self.lock = threading.Lock()
        threading.Thread(target=self.update, daemon=True).start()

    def black_frame(self):
        return np.zeros((FRAME_SIZE[1], FRAME_SIZE[0], 3), dtype=np.uint8)

    def connect(self):
        cap = cv2.VideoCapture(self.url)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        return cap

    def update(self):

        cap = self.connect()

        while self.running:

            if not cap.isOpened():
                cap.release()
                time.sleep(2)
                cap = self.connect()
                continue

            ret, frame = cap.read()

            if not ret or frame is None:
                cap.release()
                time.sleep(2)
                cap = self.connect()
                continue

            frame = cv2.resize(frame, FRAME_SIZE)

            with self.lock:
                self.frame = frame

        cap.release()

    def read(self):
        with self.lock:
            return self.frame.copy()

    def stop(self):
        self.running = False


# ==============================
# ESTADO DA CENTRAL
# ==============================

fullscreen_cam = None
last_click_time = 0

# ==============================
# MOUSE EVENTS
# ==============================

def mouse_callback(event, x, y, flags, param):
    global fullscreen_cam, last_click_time

    if event == cv2.EVENT_LBUTTONDOWN:

        now = time.time()

        if now - last_click_time < 0.3:
            fullscreen_cam = None
            last_click_time = 0
            return

        last_click_time = now

        col = x // CELL_WIDTH
        row = y // CELL_HEIGHT
        index = int(row * GRID_COLS + col)

        if index < CAM_COUNT:
            fullscreen_cam = index


# ==============================
# RESTART
# ==============================

def restart_program(streams):

    for s in streams:
        s.stop()

    cv2.destroyAllWindows()

    os.execv(sys.executable, [sys.executable] + sys.argv)


# ==============================
# MAIN
# ==============================

def main():

    streams = [
        CameraStream(url, i)
        for i, url in enumerate(CAMERAS)
    ]

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)

    cv2.setWindowProperty(
        WINDOW_NAME,
        cv2.WND_PROP_FULLSCREEN,
        cv2.WINDOW_FULLSCREEN
    )

    cv2.setMouseCallback(WINDOW_NAME, mouse_callback)

    start_time = time.time()

    while True:

        if fullscreen_cam is not None:

            frame = streams[fullscreen_cam].read()
            frame = cv2.resize(frame, (SCREEN_WIDTH, SCREEN_HEIGHT))
            cv2.imshow(WINDOW_NAME, frame)

        else:

            frames = [s.read() for s in streams]

            total_cells = GRID_ROWS * GRID_COLS

            while len(frames) < total_cells:
                frames.append(
                    np.zeros((FRAME_SIZE[1], FRAME_SIZE[0], 3), dtype=np.uint8)
                )

            rows = []
            for i in range(GRID_ROWS):
                row = np.hstack(
                    frames[i * GRID_COLS:(i + 1) * GRID_COLS]
                )
                rows.append(row)

            grid = np.vstack(rows)
            cv2.imshow(WINDOW_NAME, grid)

        if cv2.waitKey(1) == 27:
            break

        if time.time() - start_time > RESTART_TIME:
            restart_program(streams)

    for s in streams:
        s.stop()

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()