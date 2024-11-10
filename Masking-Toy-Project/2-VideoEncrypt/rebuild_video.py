## 4_rebuild_video.py

import os
import cv2
import re

def natural_sort_key(s):
    """ 숫자 순서로 파일명 정렬하기 위한 함수 """
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]

def frames_to_video(input_dir, output_video_path):
    # FPS 정보 읽기
    fps_path = os.path.join(input_dir, 'fps.txt')
    with open(fps_path, 'r') as f:
        fps = float(f.read())

    # 프레임을 불러오기
    frame_files = sorted([f for f in os.listdir(input_dir) if f.endswith('.png')], key=natural_sort_key)

    # 첫 번째 프레임을 불러와서 영상의 크기 설정
    first_frame = cv2.imread(os.path.join(input_dir, frame_files[0]))
    height, width, layers = first_frame.shape

    # 동영상 파일로 저장할 준비
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 코덱 설정 (mp4)
    video = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

    # 프레임을 순서대로 불러와서 동영상 파일로 저장
    for frame_file in frame_files:
        frame_path = os.path.join(input_dir, frame_file)
        frame = cv2.imread(frame_path)
        video.write(frame)

    video.release()
    print(f"영상이 '{output_video_path}'로 저장되었습니다.")

# 실행
if __name__ == "__main__":
    # 현재 디렉토리와 프레임 폴더 설정
    input_dir = os.path.join(os.path.dirname(__file__), 'decrypted_frames')
    output_video_path = os.path.join(os.path.dirname(__file__), 'reconstructed_video.mp4')

    # 복호화된 프레임을 다시 영상으로 합치기
    frames_to_video(input_dir, output_video_path)
