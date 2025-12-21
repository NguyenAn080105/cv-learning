import os

current_file = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file)
project_root = os.path.dirname(os.path.dirname(current_dir))

DATASET_ROOT_DIR = os.path.join(project_root, "datasets")
CLASS_NAMES = ['bus', 'car', 'motor', 'truck']
SPLITS = ['train', 'valid', 'test']

def count_yolo_classes_in_dir(labels_dir, class_names):
    class_counts = {name: 0 for name in class_names}
    num_classes = len(class_names)
    
    if not os.path.isdir(labels_dir):
        return class_counts, 0

    total_files_processed = 0
    
    for filename in os.listdir(labels_dir):
        if not filename.endswith(".txt"):
            continue
            
        file_path = os.path.join(labels_dir, filename)
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if parts:
                        try:
                            class_index = int(parts[0])
                            if 0 <= class_index < num_classes:
                                class_name = class_names[class_index]
                                class_counts[class_name] += 1
                        except ValueError:
                            continue
            total_files_processed += 1
        except Exception:
            continue

    return class_counts, total_files_processed

# --- MAIN EXECUTION ---
print(f"Starting Statistics at: {DATASET_ROOT_DIR}\n")

if not os.path.exists(DATASET_ROOT_DIR):
    print(f"Error: Directory {DATASET_ROOT_DIR} not found.")
else:
    all_results = {}
    total_dataset_instances = 0

    for split in SPLITS:
        full_labels_dir = os.path.join(DATASET_ROOT_DIR, split, 'labels')
        
        print(f"Processing split **{split.upper()}**...")
        split_counts, files_processed = count_yolo_classes_in_dir(full_labels_dir, CLASS_NAMES)
        
        all_results[split] = split_counts
        split_total = sum(split_counts.values())
        total_dataset_instances += split_total
        
        print(f" -> Done. Total objects: {split_total}.\n")

    # PRINT SUMMARY TABLE
    print("-" * 70)
    print("--- DETAILED CLASS STATISTICS ---")
    print("-" * 70)

    header = f"{'SPLIT':<10}|"
    for name in CLASS_NAMES:
        header += f"{name.upper():^10}|"
    header += f"{'TOTAL':^10}"
    print(header)
    print("-" * 70)

    for split in SPLITS:
        if split in all_results:
            counts = all_results[split]
            row = f"{split.upper():<10}|"
            for name in CLASS_NAMES:
                count = counts.get(name, 0)
                row += f"{count:^10}|"
            row += f"{sum(counts.values()):^10}"
            print(row)
        else:
            print(f"{split.upper():<10}|{'Not Found':^59}")

    print("-" * 70)
    print(f"GRAND TOTAL OBJECTS: {total_dataset_instances}")
    print("-" * 70)