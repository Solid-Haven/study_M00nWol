# masking/masker.py
import torch
import cv2

# torch.hub.load를 통해 YOLO 모델 불러오기
model = torch.hub.load('ultralytics/yolov5', 'yolov5s')

def apply_mask(frame):
    results = model(frame)
    for det in results.xyxy[0]:
        x1, y1, x2, y2, conf, cls = map(int, det)
        frame = cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), -1)  # 간단히 사각형 마스킹
    return frame