import os

current_file = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file)
project_root = os.path.dirname(os.path.dirname(current_dir))

BASE_DIR = os.path.join(project_root, "datasets")

EXPECTED_VALUES_FOR_BBOX = 5

def find_polygon_files():
    print(f"--- Starting dataset scan at: {BASE_DIR} ---")
    
    if not os.path.exists(BASE_DIR):
        print(f"Error: Directory {BASE_DIR} not found.")
        return

    polygon_files_found = []
    for split in ['train', 'valid', 'test']:
        label_dir = os.path.join(BASE_DIR, split, 'labels')

        if not os.path.exists(label_dir):
            continue

        print(f"Scanning: {label_dir}")
        
        for filename in os.listdir(label_dir):
            if not filename.endswith(".txt"):
                continue

            file_path = os.path.join(label_dir, filename)
            try:
                with open(file_path, 'r') as f:
                    for line in f:
                        parts = line.strip().split()
                        # If more than 5 values (class x y w h), it might be a polygon
                        if len(parts) > EXPECTED_VALUES_FOR_BBOX:
                            polygon_files_found.append(file_path)
                            break 
            except Exception as e:
                print(f"Error reading file {filename}: {e}")

    print("\n--- SCAN RESULTS ---")
    if not polygon_files_found:
        print("Dataset is CLEAN. No polygon formats found.")
    else:
        print(f"Found {len(polygon_files_found)} files with polygon format:")
        for path in polygon_files_found:
            print(f" - {path}")

if __name__ == '__main__':
    find_polygon_files()