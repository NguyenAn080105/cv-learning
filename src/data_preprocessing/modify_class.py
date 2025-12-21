import os

current_file = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file)
project_root = os.path.dirname(os.path.dirname(current_dir))

DATASET_ROOT_DIR = os.path.join(project_root, "datasets")

ORIGINAL_CLASS_NAMES = ['bus', 'car', 'motor', 'truck'] 
NEW_CLASS_NAMES = ['motor', 'car', 'bus', 'truck'] 

def reindex_yolo_labels(labels_dir, index_map):
    if not os.path.isdir(labels_dir):
        return 0, 0
        
    total_files_processed = 0
    total_annotations_updated = 0
    
    for filename in os.listdir(labels_dir):
        if not filename.endswith(".txt"):
            continue

        file_path = os.path.join(labels_dir, filename)
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            updated_lines = []
            file_updates_count = 0
            
            for line in lines:
                parts = line.strip().split()
                if parts:
                    try:
                        old_index = int(parts[0])
                        if old_index in index_map:
                            new_index = index_map[old_index]
                            new_line = f"{new_index} {' '.join(parts[1:])}\n"
                            updated_lines.append(new_line)
                            file_updates_count += 1
                        else:
                            updated_lines.append(line)
                    except ValueError:
                        updated_lines.append(line)
                else:
                    updated_lines.append(line)

            if file_updates_count > 0:
                with open(file_path, 'w') as f:
                    f.writelines(updated_lines)
                total_files_processed += 1
                total_annotations_updated += file_updates_count
            
        except Exception as e:
            print(f"Error processing file '{filename}': {e}")

    return total_files_processed, total_annotations_updated

def process_dataset_splits(root_dir, original_classes, new_classes):
    if not os.path.exists(root_dir):
        print(f"Error: Dataset directory not found at {root_dir}")
        return

    index_map_fixed = {}
    for new_idx, name in enumerate(new_classes):
        if name in original_classes:
            old_idx = original_classes.index(name)
            index_map_fixed[old_idx] = new_idx 

    print("--- Class Index Mapping (Old -> New) ---")
    for old, new in index_map_fixed.items():
        print(f"Class '{original_classes[old]}': {old} -> {new}")
    
    SPLITS = ['train', 'valid', 'test']
    
    total_dataset_files = 0
    total_dataset_annotations = 0
    
    for split in SPLITS:
        full_labels_dir = os.path.join(root_dir, split, 'labels')
        print(f"Processing split **{split.upper()}** at: {full_labels_dir}")
        
        files_processed, annotations_updated = reindex_yolo_labels(full_labels_dir, index_map_fixed)
        
        total_dataset_files += files_processed
        total_dataset_annotations += annotations_updated
        
    print(f"COMPLETED: Total {total_dataset_files} files updated.")

if __name__ == "__main__":
    process_dataset_splits(DATASET_ROOT_DIR, ORIGINAL_CLASS_NAMES, NEW_CLASS_NAMES)