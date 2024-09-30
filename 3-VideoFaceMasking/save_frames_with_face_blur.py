import os
import cv2

def save_frames_with_face_blur(video_path, output_dir, face_cascade_path):
    # 얼굴 탐지를 위한 HaarCasCade 로드
    face_cascade = cv2.CascadeClassifier(face_cascade_path)

    # 영상 파일 불러오기
    cap = cv2.VideoCapture(video_path)

    # FPS 정보 얻기
    fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"원본 영상 FPS: {fps}")

    # FPS 정보를 텍스트 파일로 저장
    fps_path = os.path.join(output_dir, 'fps.txt')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(fps_path, 'w') as f:
        f.write(str(fps))

    frame_count=0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # 얼굴 탐지 
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)    # 얼굴 탐지를 위해 그레이스케일로 변환
        faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30,30))

        # 얼굴 영역에 블러 처리
        for (x, y, w, h) in faces:
            face_region = frame[y:y+h, x:x+w]
            blurred_face = cv2.GaussianBlur(face_region, (99,99), 30) # 블러 처리
            frame[y:y+h, x:x+w] = blurred_face # 원본 프레임에 블러 처리된 영역 적용
        
        # 프레임 저장
        frame_path = os.path.join(output_dir, f'frame_{frame_count:04d}.png')   # 숫자 부분을 4자리로 맞추어 정렬이 쉽게 함
        cv2.imwrite(frame_path, frame)
        frame_count += 1

    cap.release()
    cv2.destroyAllWindows()

    print(f"총 {frame_count}개의 프레임이 저장되었습니다.")

# 실행
if __name__ == "__main__":
    current_dir = os.getcwd()   # 현재 작업 디렉토리
    video_path = os.path.join(current_dir, 'sample_video.mp4')
    output_dir = os.path.join(current_dir, 'frames')
    face_cascade_path = os.path.join(current_dir, 'haarcascade_frontalface_default.xml')  # Haar Cascade 파일 경로
    save_frames_with_face_blur(video_path, output_dir, face_cascade_path)