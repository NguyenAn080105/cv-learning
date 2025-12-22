import cv2
import numpy as np
from ultralytics import YOLO
import time
import threading
import queue
import os
import sys

# --- Run MediaMTX and FFMPEG
# .\mediamtx.exe
# .\ffmpeg -re -stream_loop -1 -i vehicle_vid_12.mp4 -c:v copy -rtsp_transport tcp -f rtsp rtsp://localhost:8554/live_stream

# --- PATH CONFIGURATION ---
CURRENT_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_SCRIPT_DIR)

MODEL_PATH = os.path.join(ROOT_DIR, "models", "best.pt")
TRACKER_CONFIG = os.path.join(ROOT_DIR, "config", "my_tracker.yaml")
RTSP_URL = "rtsp://localhost:8554/live_stream"
VIDEO_FILE_PATH = os.path.join(ROOT_DIR, "tools", "vehicle_vid_12.mp4")
VIDEO_SOURCE = RTSP_URL

# --- VALIDATION ---
if not os.path.exists(MODEL_PATH):
    print(f"[ERROR] Model not found at: {MODEL_PATH}")
    sys.exit(1)
 
# --- VISUALIZATION CONFIG ---
POLYGON_ROI = np.array([[436, 419], [1919, 422], [1916, 651], [197, 651]], dtype=np.int32)
ROI_COLOR = (255, 0, 0)
ROI_ALPHA = 0.3
TEXT_COLOR = (255, 255, 255)
TEXT_COUNTED_COLOR = (0, 0, 255) # Red color for counted vehicles
DEFAULT_COLOR = (255, 255, 255)

CLASS_COLOR_MAP = {
    'car': (0, 255, 0),
    'bus': (255, 0, 0),
    'truck': (0, 51, 102),
    'motor': (0, 255, 255)
}

# --- THREADED VIDEO CAPTURE ---
class VideoCaptureThreading:
    def __init__(self, src):
        self.src = src
        os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"
        self.cap = cv2.VideoCapture(src, cv2.CAP_FFMPEG)
        
        if not self.cap.isOpened():
            print(f"[ERROR] Failed to open connection to: {src}")
            return
        
        self.q = queue.Queue(maxsize=10)
        self.stop_event = threading.Event()
        self.t = threading.Thread(target=self._reader)
        self.t.daemon = True
        self.t.start()

    def _reader(self):
        while not self.stop_event.is_set():
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.01)
                continue
            
            if not self.q.empty():
                try: self.q.get_nowait()
                except queue.Empty: pass
            self.q.put(frame)

    def read(self):
        try: 
            # Wait a bit longer for RTSP packets
            return True, self.q.get(timeout=1)
        except queue.Empty:
            return False, None

    def release(self):
        self.stop_event.set()
        self.t.join()
        self.cap.release()

def main():
    print(f"[INFO] Loading model: {MODEL_PATH}")
    try:
        model = YOLO(MODEL_PATH)
    except Exception as e:
        print(f"[ERROR] Load model failed: {e}")
        return

    CLASS_NAMES = model.names
    vehicle_counts = {name: 0 for name in CLASS_NAMES.values()}
    id_da_dem = set()

    print(f"[INFO] Connecting to: {VIDEO_SOURCE}")
    cap = VideoCaptureThreading(VIDEO_SOURCE)
    
    print("[INFO] Waiting for stream buffer...")
    time.sleep(2.0)

    # --- RETRY LOGIC FOR FIRST FRAME ---
    sample = None
    for i in range(10):
        ret, sample = cap.read()
        if sample is not None:
            break
        print(f"[WARNING] Waiting for stream data... ({i+1}/10)")
        time.sleep(1.0)
        
    if sample is None:
        print("[ERROR] No video feed received.")
        print(" -> Check if Mediamtx is running.")
        print(" -> Check if FFmpeg is pushing video.")
        cap.release()
        return
    
    # Resize logic
    orig_h, orig_w = sample.shape[:2]
    display_w = 1280
    display_h = int(orig_h * (1280/orig_w))

    print(f"[INFO] Started. Display: {display_w}x{display_h}")
    print("[INFO] Press 'q' to exit.")

    # [FIXED] Create Window explicitly so it appears even if frames are laggy
    cv2.namedWindow("Traffic Monitoring System", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Traffic Monitoring System", display_w, display_h)

    prev_frame_time = 0
    fps_smoothed = 0
    alpha_fps = 0.9 

    try:
        while True:
            ret, frame = cap.read()
            
            # [FIXED] Handle empty frames without exiting
            if not ret or frame is None:
                # If it's a local file, we stop. If RTSP, we wait.
                if isinstance(VIDEO_SOURCE, str) and os.path.exists(VIDEO_SOURCE) and os.path.isfile(VIDEO_SOURCE):
                    print("[INFO] End of file.")
                    break
                
                # For RTSP, just log and continue waiting
                print("[WARNING] Frame buffer empty, waiting for stream...")
                time.sleep(0.1)
                
                # Keep window open and responsive even when no frame
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                continue

            # --- 1. TRACKING ---
            results = model.track(frame, persist=True, tracker=TRACKER_CONFIG, verbose=False, conf=0.25)

            frame_width = frame.shape[1]
            frame_height = frame.shape[0]

            font_scale = max(0.5, frame_width / 1500)
            line_height = int(font_scale * 40)

            # --- 2. DRAW ROI ---
            overlay = frame.copy()
            cv2.fillPoly(overlay, [POLYGON_ROI], ROI_COLOR)
            cv2.polylines(overlay, [POLYGON_ROI], isClosed=True, color=ROI_COLOR, thickness=2)
            cv2.addWeighted(overlay, ROI_ALPHA, frame, 1 - ROI_ALPHA, 0, dst=frame)

            # --- 3. DRAW TRACKING ---
            if results[0].boxes.id is not None:
                boxes = results[0].boxes.xyxy.cpu().numpy()
                ids = results[0].boxes.id.int().cpu().tolist()
                clss = results[0].boxes.cls.int().cpu().tolist()

                for box, track_id, cls in zip(boxes, ids, clss):
                    x1, y1, x2, y2 = box
                    cls_name = CLASS_NAMES.get(cls, str(cls))

                    cx, cy = int((x1 + x2)/2), int(y2)
                    is_inside = cv2.pointPolygonTest(POLYGON_ROI, (cx, cy), False)

                    if is_inside > 0:
                        if track_id not in id_da_dem:
                            id_da_dem.add(track_id)
                            if cls_name in vehicle_counts:
                                vehicle_counts[cls_name] += 1
                    
                    box_color = CLASS_COLOR_MAP.get(cls_name, DEFAULT_COLOR)
                    text_draw_color = box_color
                    
                    if track_id in id_da_dem and is_inside > 0:
                        text_draw_color = TEXT_COUNTED_COLOR

                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), box_color, 2)
                    label = f"ID:{track_id} {cls_name}"
                    cv2.putText(frame, label, (int(x1), int(y1)-10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_draw_color, 2)

            # --- 4. DASHBOARD ---
            # FPS
            curr_time = time.time()
            fps_instant = 1 / (curr_time - prev_frame_time) if prev_frame_time > 0 else 0
            prev_frame_time = curr_time
            fps_smoothed = (alpha_fps * fps_smoothed) + ((1 - alpha_fps) * fps_instant)
            
            fps_text = f"FPS: {int(fps_smoothed)}"
            fps_box_width = int(frame_width * 0.12)
            
            overlay_fps = frame.copy()
            cv2.rectangle(overlay_fps, (0, 0), (fps_box_width, line_height), (0, 0, 0), cv2.FILLED)
            cv2.addWeighted(overlay_fps, 0.6, frame, 0.4, 0, dst=frame)
            cv2.putText(frame, fps_text, (int(fps_box_width * 0.1), int(line_height * 0.75)), 
                        cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 255, 0), 2)

            # Statistics
            box_width = int(frame_width * 0.15)
            start_x = frame_width - box_width
            num_classes = len(vehicle_counts)
            box_height = (num_classes * line_height) + int(line_height / 2)
            
            overlay_box = frame.copy()
            cv2.rectangle(overlay_box, (start_x, 0), (frame_width, box_height), (0, 0, 0), cv2.FILLED)
            cv2.addWeighted(overlay_box, 0.6, frame, 0.4, 0, dst=frame)

            y_off = line_height
            for k, v in vehicle_counts.items():
                text = f"{k.capitalize()}: {v}"
                cv2.putText(frame, text, (start_x + int(box_width*0.1), y_off), 
                            cv2.FONT_HERSHEY_SIMPLEX, font_scale, TEXT_COLOR, 2)
                y_off += line_height

            # --- 5. REALTIME DISPLAY ---
            frame_show = cv2.resize(frame, (display_w, display_h))
            cv2.imshow("Traffic Monitoring System", frame_show)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        pass
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("\n[INFO] System terminated.")

if __name__ == "__main__":
    main()