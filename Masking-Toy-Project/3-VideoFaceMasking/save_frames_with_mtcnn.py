import os
import cv2
from mtcnn import MTCNN

def save_frames_with_mtcnn(video_path, output_dir):
    # MTCNN 탐지기 초기화
    detector = MTCNN()

    # 영상 파일 불러오기
    cap = cv2.VideoCapture(video_path)

    # FPS 정보 얻기
    fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"원본 영상 FPS: {fps}")
    