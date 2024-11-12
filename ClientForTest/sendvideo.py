import cv2
import requests
import time

# 서버 URL 설정
# 서버 URL 설정
url = "http://3.38.106.115:8000/mask_video_frame/"

# 테스트용 동영상 파일 경로 설정
video_path = "test_video.mp4"
cap = cv2.VideoCapture(video_path)
frame_count = 0  # 프레임 번호 초기화

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # 프레임을 JPEG로 인코딩
    _, frame_encoded = cv2.imencode('.jpg', frame)
    frame_bytes = frame_encoded.tobytes()

    # 서버에 프레임 전송
    try:
        files = {'frame': ('frame.jpg', frame_bytes, 'image/jpeg')}
        data = {'frame_count': str(frame_count)}  # 프레임 번호 전송
        response = requests.post(url, files=files, data=data)

        if response.status_code == 200:
            print("Masking and upload successful:", response.json())
        else:
            print("Failed to process frame:", response.json())
    except Exception as e:
        print("Error sending frame:", str(e))

    frame_count += 1  # 프레임 번호 증가
    time.sleep(0.1)  # 프레임 전송 간격 (필요시 조정 가능)

cap.release()
