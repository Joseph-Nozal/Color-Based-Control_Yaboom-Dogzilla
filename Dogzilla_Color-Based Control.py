# ==== DOGZILLA Color Navigation (Optimized Continuous Version) ====
import cv2, numpy as np, threading, time, ipywidgets as widgets
from IPython.display import display
from DOGZILLALib import DOGZILLA

# --- Initialize Dogzilla robot ---
g_dog = DOGZILLA()
try: g_dog.Init()
except: pass
try: g_dog.reset()
except: pass

# --- HSV Color Ranges ---
HSV_RANGES = {
    "red1": ((0, 130, 120), (10, 255, 255)),
    "red2": ((160,130,120), (179,255,255)),
    "green": ((35, 120, 80), (85, 255, 255)),
    "blue": ((95, 130, 80), (130, 255, 255)),
    "yellow": ((20, 140, 100), (35, 255, 255)),
    "purple": ((130, 100, 80), (160, 255, 255))
}

# --- Global State ---
_camera_running = False
_current_motion = None
_motion_lock = threading.Lock()

# --- Speed Control ---
speed_mode = widgets.ToggleButtons(
    options=[('🐢 Slow','slow'),('⚙️ Normal','normal'),('🚀 Fast','fast')],
    value='normal',
    description='Speed:'
)

def get_speed_factor():
    if speed_mode.value == 'slow': return 0.6
    if speed_mode.value == 'fast': return 1.4
    return 1.0

# --- Movement wrappers using DOGZILLA API ---
BASE_STEP = 25
BASE_TURN = 30

def move_forward_continuous():
    while _camera_running and _current_motion == 'forward':
        factor = get_speed_factor()
        g_dog.forward(int(BASE_STEP * factor))
        time.sleep(0.3 / factor)

def move_backward_continuous():
    while _camera_running and _current_motion == 'backward':
        factor = get_speed_factor()
        g_dog.back(int(BASE_STEP * factor))
        time.sleep(0.3 / factor)

def turn_right_continuous():
    while _camera_running and _current_motion == 'right':
        factor = get_speed_factor()
        g_dog.turnright(int(BASE_TURN * factor))
        time.sleep(0.4 / factor)

def turn_left_continuous():
    while _camera_running and _current_motion == 'left':
        factor = get_speed_factor()
        g_dog.turnleft(int(BASE_TURN * factor))
        time.sleep(0.4 / factor)

def stop_robot():
    try:
        g_dog.stop()
    except:
        pass

def set_motion(new_motion):
    global _current_motion
    with _motion_lock:
        if _current_motion == new_motion:
            return
        _current_motion = new_motion
        stop_robot()
        if not new_motion: return
        if new_motion == 'forward':
            threading.Thread(target=move_forward_continuous, daemon=True).start()
        elif new_motion == 'backward':
            threading.Thread(target=move_backward_continuous, daemon=True).start()
        elif new_motion == 'right':
            threading.Thread(target=turn_right_continuous, daemon=True).start()
        elif new_motion == 'left':
            threading.Thread(target=turn_left_continuous, daemon=True).start()

# --- Widgets ---
image_widget = widgets.Image(format='jpeg', width=640, height=480)
btn_start = widgets.Button(description="▶ Start", button_style='success')
btn_stop = widgets.Button(description="⏹ Stop", button_style='danger')
status = widgets.HTML(value="<b>Status:</b> Idle")
display(widgets.VBox([widgets.HBox([btn_start, btn_stop, speed_mode, status]), image_widget]))

# --- Color Detection ---
def detect_color_and_box(hsv):
    detected_color, largest_area, best_box = None, 0, None
    mask_r1 = cv2.inRange(hsv, np.array(HSV_RANGES["red1"][0]), np.array(HSV_RANGES["red1"][1]))
    mask_r2 = cv2.inRange(hsv, np.array(HSV_RANGES["red2"][0]), np.array(HSV_RANGES["red2"][1]))
    mask_red = cv2.bitwise_or(mask_r1, mask_r2)
    color_masks = {
        "red": mask_red,
        "green": cv2.inRange(hsv, np.array(HSV_RANGES["green"][0]), np.array(HSV_RANGES["green"][1])),
        "blue": cv2.inRange(hsv, np.array(HSV_RANGES["blue"][0]), np.array(HSV_RANGES["blue"][1])),
        "yellow": cv2.inRange(hsv, np.array(HSV_RANGES["yellow"][0]), np.array(HSV_RANGES["yellow"][1])),
        "purple": cv2.inRange(hsv, np.array(HSV_RANGES["purple"][0]), np.array(HSV_RANGES["purple"][1]))
    }

    for color, mask in color_masks.items():
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        mask = cv2.GaussianBlur(mask, (5,5), 0)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours: continue
        c = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(c)
        if area > 1000 and area > largest_area:
            largest_area = area
            detected_color = color
            x, y, w, h = cv2.boundingRect(c)
            best_box = (x, y, w, h)
    return detected_color, best_box

# --- Camera Loop ---
def camera_loop():
    global _camera_running, _current_motion
    cap = None
    for i in range(3):
        cap = cv2.VideoCapture(i)
        if cap.isOpened(): break
    if not cap or not cap.isOpened():
        status.value = "❌ No camera found"
        return
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    color_memory, stable_color = [], None
    while _camera_running:
        for _ in range(2): cap.grab()
        ret, frame = cap.read()
        if not ret: continue
        frame_small = cv2.resize(frame, (320, 240))
        hsv = cv2.cvtColor(frame_small, cv2.COLOR_BGR2HSV)
        color, box = detect_color_and_box(hsv)

        if color:
            color_memory.append(color)
        if len(color_memory) > 7:
            color_memory.pop(0)
        if len(color_memory) == 7:
            stable = max(set(color_memory), key=color_memory.count)
            if stable != stable_color:
                stable_color = stable
                if stable == "green":
                    set_motion('forward')
                    status.value = f"🟢 Moving Forward ({speed_mode.value})"
                elif stable == "red":
                    set_motion(None)
                    stop_robot()
                    status.value = "🔴 Stop"
                elif stable == "yellow":
                    set_motion('right')
                    status.value = f"🟡 Turning Right ({speed_mode.value})"
                elif stable == "blue":
                    set_motion('left')
                    status.value = f"🔵 Turning Left ({speed_mode.value})"
                elif stable == "purple":
                    set_motion('backward')
                    status.value = f"🟣 Moving Backward ({speed_mode.value})"

        disp = cv2.resize(frame_small, (640, 480))
        if box:
            x, y, w, h = [int(v * 2) for v in box]
            cv2.rectangle(disp, (x, y), (x+w, y+h), (255,255,255), 3)
            cv2.putText(disp, f"{stable_color or color}", (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255,255,255), 3)

        _, buf = cv2.imencode('.jpg', disp)
        image_widget.value = buf.tobytes()
        time.sleep(0.03)

    stop_robot()
    cap.release()
    status.value = "⏹ Stopped"

# --- Buttons ---
def start_camera(b):
    global _camera_running
    if _camera_running: return
    _camera_running = True
    threading.Thread(target=camera_loop, daemon=True).start()
    status.value = "Starting..."

def stop_camera(b):
    global _camera_running, _current_motion
    _camera_running = False
    _current_motion = None
    stop_robot()
    status.value = "Stopped by user"

btn_start.on_click(start_camera)
btn_stop.on_click(stop_camera)
