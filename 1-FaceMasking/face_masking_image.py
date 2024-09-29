import cv2
import os

# 현재 스크립트와 동일한 디렉토리 내의 이미지 경로 설정
image_path = os.path.join(os.path.dirname(__file__), 'sample.jpg')

# 이미지 로드 및 표시
image = cv2.imread(image_path)

## 얼굴 인식 모델 로드 (Haar Cascades)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

## 그레이스케일로 변환 (얼굴 인식에 유리)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

## 얼굴 감지 
faces = face_cascade.detectMultiScale(gray, 1.3, 5)

## 감지된 얼굴에 블러링 적용
for (x, y, w, h) in faces:
    face_region = image[y:y+h, x:x+w]
    blurred_face = cv2.GaussianBlur(face_region, (99,99), 30)
    image[y:y+h, x:x+w] = blurred_face

## 결과 출력
cv2.imshow('Face Masking', image)
cv2.waitKey(0)
cv2.destroyAllWindows()