import cv2
import os
import random
import tkinter as tk

DATASET_PATH = "D:/vehicle_dataset"
TRAIN_OR_VALID = 'train'
 
CLASS_NAMES = ['bus', 'car', 'motor', 'truck']

NUM_IMAGES_TO_CHECK = 200

COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
WINDOW_SCALE_FACTOR = 0.85

def get_screen_size():
    try:
        root = tk.Tk()
        root.withdraw()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.destroy()
        return screen_width, screen_height
    except tk.TclError:
        return 1920, 1080

def visualize_annotations():
    image_dir = os.path.join(DATASET_PATH, TRAIN_OR_VALID, 'images')
    label_dir = os.path.join(DATASET_PATH, TRAIN_OR_VALID, 'labels')
    
    if not os.path.exists(image_dir) or not os.path.exists(label_dir):
        print(f"Loi: Khong tim thay thu muc 'images' hoac 'labels'.")
        return

    image_files = [f for f in os.listdir(image_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
    if not image_files:
        print(f"Khong tim thay anh nao trong: {image_dir}")
        return

    screen_w, screen_h = get_screen_size()

    selected_images = random.sample(image_files, min(NUM_IMAGES_TO_CHECK, len(image_files)))
    print(f"--- Bat dau kiem tra {len(selected_images)} anh ngau nhien ---")
    print("Nhan phim bat ky de xem anh tiep theo. Nhan 'q' de thoat.")

    for image_name in selected_images:
        image_path = os.path.join(image_dir, image_name)
        image = cv2.imread(image_path)
        if image is None: continue
        
        h, w, _ = image.shape
        label_path = os.path.join(label_dir, os.path.splitext(image_name)[0] + ".txt")

        if os.path.exists(label_path):
            with open(label_path, 'r') as f:
                for line in f.readlines():
                    try:
                        parts = line.strip().split()
                        class_id = int(parts[0])
                        x_center, y_center, width, height = map(float, parts[1:])
                        bbox_width, bbox_height = int(width * w), int(height * h)
                        x_center_px, y_center_px = int(x_center * w), int(y_center * h)
                        x1 = x_center_px - bbox_width // 2
                        y1 = y_center_px - bbox_height // 2
                        class_name = CLASS_NAMES[class_id]
                        color = COLORS[class_id % len(COLORS)]
                        cv2.rectangle(image, (x1, y1), (x1 + bbox_width, y1 + bbox_height), color, 2)
                        cv2.putText(image, class_name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
                    except (ValueError, IndexError):
                        pass
        
        window_name = f"Kiem tra Label - {image_name}"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        target_h = int(screen_h * WINDOW_SCALE_FACTOR)
        scale = target_h / h
        target_w = int(w * scale)
        if target_w > screen_w:
            scale = (screen_w * 0.95) / w
            target_w = int(w * scale)
            target_h = int(h * scale)
        image_to_show = cv2.resize(image, (target_w, target_h))

        pos_x = (screen_w - target_w) // 2
        pos_y = (screen_h - target_h) // 2

        cv2.moveWindow(window_name, pos_x, pos_y)
        cv2.imshow(window_name, image_to_show)
        
        key = cv2.waitKey(0)
        if key == ord('q'): break
        cv2.destroyAllWindows()

    cv2.destroyAllWindows()
    print("\n--- Hoan tat kiem tra. ---")

if __name__ == '__main__':
    visualize_annotations()