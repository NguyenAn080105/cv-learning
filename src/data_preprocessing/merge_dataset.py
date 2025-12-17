import os
import shutil

# --- CẤU HÌNH ---

SOURCE_DATASET_DIRS = [
    "D:/DATASETS/vehicle06_china"
]

OUTPUT_DIR = "D:/vehicle_dataset" 

def merge_datasets_with_renaming():
    print("--- Bat dau qua trinh gop va doi ten dataset ---")

    for split in ['train', 'valid', 'test']:
        os.makedirs(os.path.join(OUTPUT_DIR, split, 'images'), exist_ok=True)
        os.makedirs(os.path.join(OUTPUT_DIR, split, 'labels'), exist_ok=True)

    for source_dir in SOURCE_DATASET_DIRS:
        dataset_name = os.path.basename(os.path.normpath(source_dir))
        print(f"\nDang xu ly dataset: '{dataset_name}'...")
        
        for split in ['train', 'valid', 'test']:
            src_image_dir = os.path.join(source_dir, split, 'images')
            src_label_dir = os.path.join(source_dir, split, 'labels')

            if not os.path.exists(src_image_dir):
                print(f"  - Bo qua tap '{split}' (khong tim thay thu muc images).")
                continue
            
            file_counter = 1
            
            sorted_filenames = sorted(os.listdir(src_image_dir))

            for filename in sorted_filenames:
                base_name, ext = os.path.splitext(filename)
                
                new_basename = f"{dataset_name}_{file_counter:05d}"
                new_filename = new_basename + ext

                # Đường dẫn nguồn
                src_img_path = os.path.join(src_image_dir, filename)
                src_label_path = os.path.join(src_label_dir, base_name + ".txt")
                dst_img_path = os.path.join(OUTPUT_DIR, split, 'images', new_filename)
                dst_label_path = os.path.join(OUTPUT_DIR, split, 'labels', new_basename + ".txt")
                
                # Sao chép ảnh
                shutil.copy2(src_img_path, dst_img_path)

                # Sao chép label nếu tồn tại
                if os.path.exists(src_label_path):
                    shutil.copy2(src_label_path, dst_label_path)
                
                # Tăng bộ đếm lên 1
                file_counter += 1
    
    print("\n--- HOAN TAT QUA TRINH GOP DATASET! ---")
    print(f"Du lieu da duoc gop thanh cong vao: {OUTPUT_DIR}")

if __name__ == '__main__':
    merge_datasets_with_renaming()