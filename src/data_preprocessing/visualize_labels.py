import cv2
import os
import random
import sys
import tkinter as tk

current_file = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file)
project_root = os.path.dirname(os.path.dirname(current_dir))

DATASET_PATH = os.path.join(project_root, "datasets")
TRAIN_OR_VALID = 'train'
 
CLASS_NAMES = ['bus', 'car', 'motor', 'truck']
NUM_IMAGES_TO_CHECK = 200
COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
WINDOW_SCALE_FACTOR = 0.85

if not os.path.exists(DATASET_PATH):
    print(f"Error: Dataset directory not found at: {DATASET_PATH}")
    print("Please create 'datasets' folder in the project root.")
    sys.exit(1)

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
        print(f"Error: Could not find 'images' or 'labels' in {os.path.join(DATASET_PATH, TRAIN_OR_VALID)}")
        return

    all_files = os.listdir(image_dir)
    image_files = [f for f in all_files if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    if not image_files:
        print(f"No images found in: {image_dir}")
        return

    screen_w, screen_h = get_screen_size()
    selected_images = random.sample(image_files, min(NUM_IMAGES_TO_CHECK, len(image_files)))
    
    print(f"--- Starting check for {len(selected_images)} random images from: {DATASET_PATH} ---")
    print("Press any key to show next image. Press 'q' to exit.")

    for image_name in selected_images:
        image_path = os.path.join(image_dir, image_name)
        image = cv2.imread(image_path)
        if image is None: continue
        
        h, w, _ = image.shape
        label_filename = os.path.splitext(image_name)[0] + ".txt"
        label_path = os.path.join(label_dir, label_filename)

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
                        
                        class_name = CLASS_NAMES[class_id] if class_id < len(CLASS_NAMES) else str(class_id)
                        color = COLORS[class_id % len(COLORS)]
                        
                        cv2.rectangle(image, (x1, y1), (x1 + bbox_width, y1 + bbox_height), color, 2)
                        cv2.putText(image, class_name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
                    except (ValueError, IndexError):
                        pass
        
        window_name = f"Check Label - {image_name}"
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
    print("\n--- Validation Complete ---")

if __name__ == '__main__':
    visualize_annotations()