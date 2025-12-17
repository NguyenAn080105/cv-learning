import os
import re

def reindex_yolo_labels(labels_dir, index_map):
    if not os.path.isdir(labels_dir):
        return 0, 0
        
    total_files_processed = 0
    total_annotations_updated = 0
    
    # Lặp qua tất cả các file trong thư mục labels
    for filename in os.listdir(labels_dir):
        if filename.endswith(".txt"):
            file_path = os.path.join(labels_dir, filename)
            
            try:
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                
                updated_lines = []
                file_updates_count = 0
                
                for line in lines:
                    # Tách chỉ mục class (số đầu tiên) và phần còn lại của dòng
                    parts = line.strip().split()
                    
                    if parts:
                        try:
                            old_index = int(parts[0])
                            
                            if old_index in index_map:
                                # Lấy chỉ mục mới từ bản đồ
                                new_index = index_map[old_index]
                                
                                # Tạo dòng mới với chỉ mục mới
                                new_line = str(new_index) + " " + " ".join(parts[1:]) + "\n"
                                
                                updated_lines.append(new_line)
                                file_updates_count += 1
                            else:
                                # Giữ nguyên dòng nếu class index không cần cập nhật
                                updated_lines.append(line)
                                
                        except ValueError:
                            updated_lines.append(line) # Giữ nguyên dòng lỗi
                    else:
                        updated_lines.append(line) # Giữ nguyên dòng trống

                # Nếu có bất kỳ sự thay đổi nào, ghi đè file
                if file_updates_count > 0:
                    with open(file_path, 'w') as f:
                        f.writelines(updated_lines)
                    total_files_processed += 1
                    total_annotations_updated += file_updates_count
                
            except Exception as e:
                print(f"Lỗi khi xử lý file '{filename}': {e}")

    return total_files_processed, total_annotations_updated

def process_dataset_splits(root_dir, original_classes, new_classes):

    index_map = {}
    for i, new_name in enumerate(new_classes):
        try:
            original_index = original_classes.index(new_name)
            index_map[i] = original_index
        except ValueError:
            print(f"Cảnh báo: Class '{new_name}' (index {i}) không tồn tại trong danh sách gốc. Bỏ qua.")
            
    if not index_map:
        print("Lỗi: Bản đồ ánh xạ trống. Vui lòng kiểm tra lại danh sách class.")
        return

    print("--- Bản đồ Ánh xạ Class Index ---")
    for old_idx, new_idx in index_map.items():
        print(f"'{new_classes[old_idx]}' | Index CŨ: {old_idx} -> Index MỚI: {new_idx}")
    print("---------------------------------")
    
    SPLITS = ['train', 'valid', 'test']
    LABEL_FOLDER_NAME = 'labels' 
    
    total_dataset_files = 0
    total_dataset_annotations = 0
    
    print(f"\nBắt đầu cập nhật nhãn trong thư mục gốc: {root_dir}")
    print("==================================================")

    for split in SPLITS:
        full_labels_dir = os.path.join(root_dir, split, LABEL_FOLDER_NAME)
        
        print(f"Đang xử lý phần **{split.upper()}**...")
        print(f"   Đường dẫn: {full_labels_dir}")
        
        if not os.path.isdir(full_labels_dir):
            print(f"Lỗi: Không tìm thấy thư mục nhãn cho '{split}'. Bỏ qua.")
            continue
            
        files_processed, annotations_updated = reindex_yolo_labels(full_labels_dir, index_map)
        
        print(f"Hoàn thành: Đã sửa {files_processed} file. Tổng đối tượng cập nhật: {annotations_updated}.\n")
        
        total_dataset_files += files_processed
        total_dataset_annotations += annotations_updated
        
    print("==================================================")
    print(f"HOÀN TẤT: Tổng cộng {total_dataset_files} file và {total_dataset_annotations} đối tượng đã được cập nhật index.")
    print("==================================================")

ORIGINAL_CLASS_NAMES = ['bus', 'car', 'motor', 'truck'] 
NEW_CLASS_NAMES = ['motor', 'car', 'bus', 'truck'] 
DATASET_ROOT_DIR = 'D:/DATASETS/motor01'

process_dataset_splits(DATASET_ROOT_DIR, ORIGINAL_CLASS_NAMES, NEW_CLASS_NAMES)