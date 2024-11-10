## save_frames_with_face_blur
import os
import cv2
import numpy as np

def save_frames_with_face_blur(video_path, output_dir, model_path, config_path):

    # DNN 모델 로드
    net = cv2.dnn.readNetFromCaffe(config_path, model_path)
    
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

        # 프레임 크기 정보
        (h, w) = frame.shape[:2]

        # DNN을 위한 입력 Blob 생성
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))
        net.setInput(blob)
        detections = net.forward()

        # 얼굴 탐지 
        for i in range(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]

            # 신뢰도 임계값 설정
            if confidence > 0.5:
                box = detections[0,0,i,3:7] * np.array([w,h,w,h])
                (startX, startY, endX, endY) = box.astype("int")

                # 얼굴 영역에 블러 처리
                face_region = frame[startY:endY, startX:endX]
                blurred_face = cv2.GaussianBlur(face_region, (99, 99), 30)  # 블러 처리
                frame[startY:endY, startX:endX] = blurred_face  # 원본에 블러 처리된 영역 적용
        
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

    # DNN 얼굴 인식 모델 경로
    model_path = os.path.join(current_dir, 'res10_300x300_ssd_iter_140000.caffemodel')
    config_path = os.path.join(current_dir, 'deploy.prototxt.txt')

    save_frames_with_face_blur(video_path, output_dir, model_path, config_path)