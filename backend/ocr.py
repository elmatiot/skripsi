import os
import json

def convert_coco_to_paddleocr(coco_json_path, image_dir, output_txt_path):
    """Mengonversi format COCO (Roboflow) ke format teks untuk PaddleOCR."""
    if not os.path.exists(coco_json_path):
        print(f"File {coco_json_path} tidak ditemukan.")
        return
    
    with open(coco_json_path, 'r', encoding='utf-8') as f:
        coco_data = json.load(f)
        
    images = {img['id']: img for img in coco_data['images']}
    categories = {cat['id']: cat['name'] for cat in coco_data['categories']}
    
    img_annotations = {img['id']: [] for img in coco_data['images']}
    for ann in coco_data['annotations']:
        img_annotations[ann['image_id']].append(ann)
        
    with open(output_txt_path, 'w', encoding='utf-8') as out_file:
        for img_id, img_info in images.items():
            filename = img_info['file_name']
            paddle_labels = []
            
            for ann in img_annotations.get(img_id, []):
                # Placeholder transcription dari category, karena coco bounding box biasa hanya nama kelas.
                # Idealnya OCR butuh teks aslinya, tapi script ini menyediakan base pipeline training.
                text = categories.get(ann['category_id'], "word")
                x, y, w, h = ann['bbox']
                points = [[x, y], [x+w, y], [x+w, y+h], [x, y+h]]
                paddle_labels.append({
                    "transcription": text,
                    "points": points
                })
            
            label_str = json.dumps(paddle_labels, ensure_ascii=False)
            out_file.write(f"{image_dir}/{filename}\t{label_str}\n")

def train_paddle_ocr():
    
    base_dir = "/home/ubuntu/skripsi"  # Root direktori workspace
    
    # Bikin anotasi
    print("1. Mengonversi dataset ke format PaddleOCR...")
    convert_coco_to_paddleocr(f"{base_dir}/train/_annotations.coco.json", "train", f"{base_dir}/train/rec_gt_train.txt")
    convert_coco_to_paddleocr(f"{base_dir}/valid/_annotations.coco.json", "valid", f"{base_dir}/valid/rec_gt_valid.txt")
    convert_coco_to_paddleocr(f"{base_dir}/test/_annotations.coco.json", "test", f"{base_dir}/test/rec_gt_test.txt")
    
    print("2. Men-download dan melakukan setup PaddleOCR repo jika belum ada...")
    if not os.path.exists("PaddleOCR"):
        os.system("git clone https://github.com/PaddlePaddle/PaddleOCR.git")
        os.system("cd PaddleOCR && python3 -m pip install -r requirements.txt")
        
    print("3. Memastikan paddlepaddle (GPU) terinstal...")
    # Packages sudah diinstal melalui virtual environment
    
    print("\n[INFO] Memulai proses training dengan evaluasi metriks...")
    
    # Argumen untuk training dan evaluasi
    train_args = (
        "-c configs/rec/PP-OCRv3/en_PP-OCRv3_mobile_rec.yml "
        f"-o Train.dataset.data_dir={base_dir}/train "
        f"Train.dataset.label_file_list=[{base_dir}/train/rec_gt_train.txt] "
        f"Eval.dataset.data_dir={base_dir}/valid "
        f"Eval.dataset.label_file_list=[{base_dir}/valid/rec_gt_valid.txt] "
        "Global.eval_batch_step=[0,20] " # Evaluasi setiap 20 step
        "Metric.name=RecMetric " # Akurasi evaluasi untuk text recognition
        "Global.save_model_dir=./output/rec_finetune"
    )
    
    # Memastikan training berjalan menggunakan python di virtual environment
    python_bin = f"{base_dir}/venv/bin/python" if os.path.exists(f"{base_dir}/venv/bin/python") else "python3"
    env_vars = f"LD_LIBRARY_PATH={base_dir}/venv/lib/python3.12/site-packages/nvidia/cudnn/lib:$LD_LIBRARY_PATH "
    train_cmd = f"{env_vars} cd PaddleOCR && {python_bin} tools/train.py {train_args}"
    print(f"Menjalankan command: {train_cmd}")
    os.system(train_cmd)

def sort_and_parse_ocr(ocr_result):
    """
    Parser (JSON Parser / Struktur Data):
    Menerima output mentah dari PaddleOCR, mengurutkan koordinat box
    dari atas ke bawah, kiri ke kanan, dan menggabungkannya ke bentuk ringkas.
    """
    if not ocr_result or not ocr_result[0]:
        return ""
        
    lines_info = []
    
    # 1. Ekstrak y_center, x_min, dan teks
    for res in ocr_result[0]:
        if not res: continue
        box = res[0]
        text = res[1][0]
        
        # Hitung center Y dari 4 titik bounding box
        y_center = sum([pt[1] for pt in box]) / 4
        x_min = min([pt[0] for pt in box])
        
        lines_info.append({'text': text, 'y': y_center, 'x': x_min})
        
    # 2. Urutkan berdasarkan tinggi (atas ke bawah)
    lines_info.sort(key=lambda item: item['y'])
    
    # 3. Kelompokkan item di baris yang sama (Toleransi Y pixel)
    grouped_lines = []
    current_group = []
    Y_TOLERANCE = 15  # Tergantung resolusi foto, 15px rata-rata setara 1 baris
    
    for item in lines_info:
        if not current_group:
            current_group.append(item)
        else:
            avg_y = sum([i['y'] for i in current_group]) / len(current_group)
            if abs(item['y'] - avg_y) < Y_TOLERANCE:
                current_group.append(item)
            else:
                # Selesai satu baris, urutkan dari kiri ke kanan berdasarkan x
                current_group.sort(key=lambda i: i['x'])
                grouped_lines.append("[ " + " | ".join([i['text'] for i in current_group]) + " ]")
                current_group = [item]
                
    # Tambahkan sisa yg ada
    if current_group:
        current_group.sort(key=lambda i: i['x'])
        grouped_lines.append("[ " + " | ".join([i['text'] for i in current_group]) + " ]")
        
    return "\n".join(grouped_lines)

if __name__ == "__main__":
    train_paddle_ocr()
