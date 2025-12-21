import os
import shutil

current_file = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file)
project_root = os.path.dirname(os.path.dirname(current_dir))
raw_data_path = os.path.join(project_root, "assets", "raw_data_sample")

SOURCE_DATASET_DIRS = raw_data_path

OUTPUT_DIR = os.path.join(project_root, "datasets")

def merge_datasets_with_renaming():
    print(f"--- Starting merge process into: {OUTPUT_DIR} ---")

    # Create output directories
    for split in ['train', 'valid', 'test']:
        os.makedirs(os.path.join(OUTPUT_DIR, split, 'images'), exist_ok=True)
        os.makedirs(os.path.join(OUTPUT_DIR, split, 'labels'), exist_ok=True)

    for source_dir in SOURCE_DATASET_DIRS:
        dataset_name = os.path.basename(os.path.normpath(source_dir))
        print(f"\nProcessing source dataset: '{dataset_name}'...")
        
        if not os.path.exists(source_dir):
             print(f"Warning: Source path not found: {source_dir}")
             continue

        for split in ['train', 'valid', 'test']:
            src_image_dir = os.path.join(source_dir, split, 'images')
            src_label_dir = os.path.join(source_dir, split, 'labels')

            if not os.path.exists(src_image_dir):
                print(f"  - Skipping split '{split}' (images folder not found).")
                continue
            
            file_counter = 1
            # Get sorted list of files
            sorted_filenames = sorted([f for f in os.listdir(src_image_dir) if os.path.isfile(os.path.join(src_image_dir, f))])

            for filename in sorted_filenames:
                base_name = os.path.splitext(filename)[0]
                ext = os.path.splitext(filename)[1]
                
                new_basename = f"{dataset_name}_{file_counter:05d}"
                new_filename = new_basename + ext

                src_img_path = os.path.join(src_image_dir, filename)
                src_label_path = os.path.join(src_label_dir, base_name + ".txt")
                
                dst_img_path = os.path.join(OUTPUT_DIR, split, 'images', new_filename)
                dst_label_path = os.path.join(OUTPUT_DIR, split, 'labels', new_basename + ".txt")
                
                shutil.copy2(src_img_path, dst_img_path)

                if os.path.exists(src_label_path):
                    shutil.copy2(src_label_path, dst_label_path)
                
                file_counter += 1
    
    print("\n--- DATASET MERGE COMPLETED ---")

if __name__ == '__main__':
    merge_datasets_with_renaming()