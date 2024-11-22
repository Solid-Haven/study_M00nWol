# masking/masker.py

import cv2
import torch

# 샘플 모델 로드 (예: YOLOv5)
model = torch.hub.load('ultralytics/yolov5', 'yolov5s')

def apply_mask(frame):
    results = model(frame)
    for det in results.xyxy[0]:  # 탐지된 객체 좌표 가져오기
        x1, y1, x2, y2, conf, cls = map(int, det)
        frame = cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), -1)  # 마스킹 적용
    return frame