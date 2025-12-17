import os
from collections import defaultdict

CLASS_NAMES = ['bus', 'car', 'motor', 'truck']

DATASET_ROOT_DIR = 'D:/DATASETS/vehicle06_china'

SPLITS = ['train', 'valid', 'test']
LABEL_FOLDER_NAME = 'labels' 

def count_yolo_classes_in_dir(labels_dir, class_names):

    class_counts = {name: 0 for name in class_names}
    num_classes = len(class_names)
    
    if not os.path.isdir(labels_dir):
        return class_counts, 0

    total_files_processed = 0
    
    for filename in os.listdir(labels_dir):
        if filename.endswith(".txt"):
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
                # Bỏ qua file lỗi và tiếp tục
                continue

    return class_counts, total_files_processed


print(f"Bắt đầu thống kê Class trong Dataset tại thư mục gốc: {DATASET_ROOT_DIR}\n")
all_results = {}
total_dataset_instances = 0

for split in SPLITS:
    # Xây dựng đường dẫn đầy đủ đến thư mục nhãn (labels)
    full_labels_dir = os.path.join(DATASET_ROOT_DIR, split, LABEL_FOLDER_NAME)
    
    print(f"Đang xử lý phần **{split.upper()}**...")
    print(f"   Đường dẫn nhãn: {full_labels_dir}")
    
    if not os.path.isdir(full_labels_dir):
        print(f"Lỗi: Không tìm thấy thư mục nhãn cho '{split}' tại đường dẫn trên. Bỏ qua.")
        continue

    # Gọi hàm đếm
    split_counts, files_processed = count_yolo_classes_in_dir(full_labels_dir, CLASS_NAMES)
    
    # Lưu kết quả
    all_results[split] = split_counts
    
    # Tính tổng số đối tượng trong phần này
    split_total = sum(split_counts.values())
    total_dataset_instances += split_total
    
    print(f" Hoàn thành: Đã xử lý {files_processed} file. Tổng đối tượng: {split_total}.\n")


# --- IN KẾT QUẢ TỔNG HỢP ---

print("-" * 70)
print("--- KẾT QUẢ THỐNG KÊ CHI TIẾT SỐ LƯỢNG CLASS THEO BỘ DỮ LIỆU ---")
print("-" * 70)

# In header bảng
header = f"{'SPLIT':<10}|"
for name in CLASS_NAMES:
    header += f"{name.upper():^10}|"
header += f"{'TỔNG':^10}"
print(header)
print("-" * 70)

# In dữ liệu cho từng split
for split in SPLITS:
    if split in all_results:
        counts = all_results[split]
        row = f"{split.upper():<10}|"
        
        split_total = sum(counts.values())
        
        for name in CLASS_NAMES:
            count = counts.get(name, 0)
            row += f"{count:^10}|"
        
        row += f"{split_total:^10}"
        print(row)
    else:
        # Trường hợp thư mục không tồn tại
        print(f"{split.upper():<10}|{'Không tìm thấy':^59}")

print("-" * 70)
print(f"TỔNG CỘNG ĐỐI TƯỢNG TOÀN DATASET: {total_dataset_instances}")
print("-" * 70)