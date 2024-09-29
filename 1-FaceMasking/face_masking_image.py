import os
import cv2


## 영상 파일 경로 설정
video_path = os.path.join(os.path.dirname(__file__), 'sample_video.mp4')

## 영상 파일 불러오기
cap = cv2.VideoCapture(video_path)

## 프레임을 저장할 디렉토리 생성
output_dir = os.path.join(os.path.dirname(__file__), 'frames')
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

frame_count = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    ## 프레임 저장
    frame_path = os.path.join(output_dir, f'frame_{frame_count}.png')
    cv2.imwrite(frame_path, frame)
    frame_count += 1

cap.release()
cv2.destroyAllWindows()


print(f"총 {frame_count}개의 프레임이 저장되었습니다.")