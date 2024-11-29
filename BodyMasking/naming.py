import os

def rename_images(folder_path, prefix="sample_"):
    # 폴더에 있는 파일 목록 가져오기
    files = os.listdir(folder_path)
    
    # 파일 목록을 순회하며 이름 변경
    for i, filename in enumerate(files):
        # 기존 파일 경로와 확장자 분리
        old_file_path = os.path.join(folder_path, filename)
        _, ext = os.path.splitext(filename)  # 확장자 추출

        # 확장자가 없는 경우(폴더 등) 건너뛰기
        if not ext:
            continue

        # 새 파일 이름 생성
        new_filename = f"{prefix}{i + 1:04d}{ext}"
        new_file_path = os.path.join(folder_path, new_filename)

        # 이름 변경
        os.rename(old_file_path, new_file_path)
        print(f"Renamed: {filename} -> {new_filename}")

# 이미지가 저장된 폴더 경로를 입력하세요.
folder_path = "dataset/raw"
rename_images(folder_path)
