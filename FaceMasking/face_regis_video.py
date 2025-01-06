from keras_facenet import FaceNet  # Keras-Facenet 사용
import cv2
import numpy as np
from mtcnn import MTCNN
import json
import time
import os

# Facenet 모델 로드
embedder = FaceNet()

# 얼굴 임베딩 추출 함수
def get_face_embedding(face_pixels):
    face_pixels = cv2.resize(face_pixels, (160, 160))  # Facenet 입력 크기
    face_pixels = face_pixels.astype('float32')
    face_pixels = np.expand_dims(face_pixels, axis=0)  # 배치 차원 추가
    embedding = embedder.embeddings(face_pixels)
    return embedding[0]

# 웹캠에서 얼굴 임베딩 추출
def extract_embedding_from_webcam(output_json_path, detection_threshold=10, timeout=10, user_id=2):
    detector = MTCNN()  # 얼굴 탐지기
    video_capture = cv2.VideoCapture(0)
    embedding_data = None  # 저장할 단일 데이터
    face_detected_count = 0  # 얼굴 감지 횟수
    start_time = time.time()

    print("Facenet을 이용한 얼굴 임베딩 추출 중입니다. ESC를 눌러 수동 종료할 수 있습니다.")

    while True:
        ret, frame = video_capture.read()
        if not ret:
            print("웹캠 연결 실패")
            break

        # 얼굴 탐지
        results = detector.detect_faces(frame)
        if results:
            for result in results:
                x, y, width, height = result['box']
                x, y = max(0, x), max(0, y)  # 좌표가 음수일 경우 0으로 처리
                face = frame[y:y+height, x:x+width]  # 얼굴 영역 자르기

                # 임베딩 추출
                embedding = get_face_embedding(face)
                face_detected_count += 1  # 얼굴 감지 횟수 증가
                print(f"얼굴이 감지되었습니다. 현재 감지 횟수: {face_detected_count}/{detection_threshold}")

                # 얼굴 감지 시 화면에 표시
                cv2.rectangle(frame, (x, y), (x+width, y+height), (0, 255, 0), 2)

                if face_detected_count >= detection_threshold:
                    # 10번 감지되면 저장
                    embedding_data = {
                        "user_id": user_id,  # user_id는 함수 호출 시 전달된 값 사용
                        "embedding": embedding.tolist()
                    }
                    print(f"얼굴이 {detection_threshold}번 감지되었습니다. 저장 후 종료합니다.")
                    video_capture.release()
                    cv2.destroyAllWindows()
                    break  # 내부 for 루프 탈출
        if embedding_data is not None:
            break  # while 루프 탈출

        # ESC 키로 수동 종료
        cv2.imshow("Face Detection", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            print("사용자 요청으로 종료합니다.")
            break

        # 타임아웃 조건
        if time.time() - start_time > timeout:
            print("시간 초과로 종료합니다.")
            break

    # JSON 파일 저장
    output_dir = "face/json"
    os.makedirs(output_dir, exist_ok=True)  # 디렉토리 생성

    # 저장 경로 설정
    output_json_path = os.path.join(output_dir, "face4.json")

    # JSON 파일 저장
    if embedding_data:
        with open(output_json_path, "w") as json_file:
            json.dump(embedding_data, json_file, indent=4)
            print(f"임베딩이 {output_json_path}에 저장되었습니다.")
    else:
        print("얼굴이 감지되지 않아 저장할 데이터가 없습니다.")

    video_capture.release()
    cv2.destroyAllWindows()

# 실행
extract_embedding_from_webcam("face4.json", detection_threshold=10, timeout=10, user_id=2)


