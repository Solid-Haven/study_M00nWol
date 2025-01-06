import os
from face_recog import process_frame

def process_all_frames(frames_dir, json_dir, output_dir, similarity_threshold=0.6):
    """
    디렉토리 내 모든 프레임을 처리하는 함수.
    """
    for frame_file in os.listdir(frames_dir):
        if not frame_file.endswith((".jpg", ".png")):
            continue
        image_path = os.path.join(frames_dir, frame_file)
        frame_name = os.path.splitext(frame_file)[0]  # 파일명 추출

        # 결과 이미지 경로 설정
        output_path = os.path.join(output_dir, f"masked_{frame_name}.jpg")

        # 프레임 처리 수행
        process_frame(image_path, json_dir, output_path, similarity_threshold)

def main():
    # 경로 설정
    frames_dir = "before/frame/2024-12-14"  # 처리할 프레임들이 저장된 디렉토리
    json_dir = "face/json"  # 등록된 얼굴 데이터(JSON)가 저장된 디렉토리
    output_dir = "after/frame/2024-12-14"  # 결과 이미지가 저장될 디렉토리

    # 출력 디렉토리 생성
    os.makedirs(output_dir, exist_ok=True)

    # 모든 프레임 처리
    process_all_frames(frames_dir, json_dir, output_dir)

if __name__ == "__main__":
    main()
