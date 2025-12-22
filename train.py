import os
import sys
from ultralytics import YOLO

# --- DYNAMIC PATH CONFIGURATION ---
CURRENT_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_SCRIPT_DIR)
DATA_YAML_PATH = os.path.join(ROOT_DIR, "config", "data.yaml")
PROJECT_DIR = os.path.join(ROOT_DIR, "runs", "detect")

# --- HARDWARE CONFIGURATION (Optimized for RTX 3050 Ti Laptop) ---
BATCH_SIZE = 8
IMG_SIZE = 640
WORKERS = 2
EPOCHS = 50 

def main():
    print("=" * 40)
    print("      YOLOv8 TRAINING SESSION      ")
    print("=" * 40)
    
    # 1. Validation
    if not os.path.exists(DATA_YAML_PATH):
        print(f"[ERROR] Data config file not found at: {DATA_YAML_PATH}")
        print("Please check your 'config' folder.")
        sys.exit(1)

    print(f"[INFO] Project Root : {ROOT_DIR}")
    print(f"[INFO] Config File  : {DATA_YAML_PATH}")
    print(f"[INFO] Batch Size   : {BATCH_SIZE}")
    print(f"[INFO] Workers      : {WORKERS}")
    print("-" * 40)

    # 2. Load Model
    model_name = 'yolov8s.pt' 
    print(f"[INFO] Loading base model: {model_name}...")
    model = YOLO(model_name)

    # 3. Start Training
    print("[INFO] Starting training process...")
    try:
        model.train(
            data=DATA_YAML_PATH,
            epochs=EPOCHS,
            imgsz=IMG_SIZE,
            batch=BATCH_SIZE,
            device=0,
            workers=WORKERS,
            project=PROJECT_DIR,
            name='train_run',
            exist_ok=True,
            verbose=True
        )
        print("\n" + "=" * 40)
        print("[SUCCESS] Training completed successfully!")
        print(f"[INFO] Check results in: {PROJECT_DIR}")
        print("=" * 40)
        
    except Exception as e:
        print(f"\n[ERROR] Training failed: {e}")
        if "out of memory" in str(e).lower():
            print(">>> HINT: Try reducing BATCH_SIZE to 4.")

if __name__ == '__main__':
    main()