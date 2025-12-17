import os

script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = script_dir 

EXPECTED_VALUES_FOR_BBOX = 5


def find_polygon_files():
    print(f"--- Bat dau quet dataset tai: {base_dir} ---")
    
    polygon_files_found = []
    for split in ['train', 'valid', 'test']:
        label_dir = os.path.join(base_dir, split, 'labels')

        if not os.path.exists(label_dir):
            continue

        print(f"Dang quet trong: {label_dir}")
        
        for filename in os.listdir(label_dir):
            if not filename.endswith(".txt"):
                continue
                
            file_path = os.path.join(label_dir, filename)
            try:
                with open(file_path, 'r') as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) > EXPECTED_VALUES_FOR_BBOX:
                            polygon_files_found.append(file_path)
                            break 
            except Exception as e:
                print(f"Loi khi doc file {file_path}: {e}")

    print("\n--- KET QUA QUET ---")
    if not polygon_files_found:
        print("Khong tim thay file nao co dinh dang polygon.")
    else:
        print(f"Da tim thay {len(polygon_files_found)} file co dinh dang polygon can loai bo:")
        for path in polygon_files_found:
            print(f" - {path}")

if __name__ == '__main__':
    find_polygon_files()