import cv2
import numpy as np
import json
from keras_facenet import FaceNet
from scipy.spatial.distance import cosine
import os

# FaceNet 모델 로드
embedder = FaceNet()

# JSON 파일에서 등록된 얼굴 데이터 로드
def load_registered_faces(json_path):
    if not os.path.exists(json_path):
        print(f"등록된 얼굴 데이터를 찾을 수 없습니다: {json_path}")
        return None
    with open(json_path, 'r') as f:
        return json.load(f)
    
# 프레임에서 얼굴 마스킹 (다수의 얼굴 지원)
def mask_faces_in_frame(image_path, registered_data, similarity_threshold=0.8, output_path="masked_image.jpg"):
    image = cv2.imread(image_path)
    if image is None:
        print(f"이미지를 로드할 수 없습니다: {image_path}")
        return

    faces = embedder.extract(image, threshold=0.95)  # 이미지에서 얼굴 검출
    if not faces:
        print("이미지에서 얼굴을 찾을 수 없습니다.")
        return

    for face in faces:
        current_embedding = face['embedding']  # 검출된 얼굴의 임베딩
        for registered_embedding in registered_data:
            similarity = 1 - cosine(np.array(registered_embedding), np.array(current_embedding))
            if similarity > similarity_threshold:  # 유사도 기준을 초과하면 마스킹
                (x, y, w, h) = face['box']  # 얼굴 영역 좌표
                face_region = image[y:y + h, x:x + w]
                face_region = cv2.GaussianBlur(face_region, (99, 99), 30)  # 가우시안 블러
                image[y:y + h, x:x + w] = face_region
                break  # 한 번 일치하면 해당 얼굴은 마스킹 완료

    # 결과 이미지 저장
    cv2.imwrite(output_path, image)
    print(f"마스킹된 이미지가 저장되었습니다: {output_path}")


def main():
    # json 파일 경로 설정
    json_path = 'data/json/sample.json'

    # 등록된 얼굴 데이터 로드
    registered_data = load_registered_faces(json_path)
    if registered_data is None:
        return
    
    # 처리할 이미지 경로
    image_path = 'data/frame/sample.jpg'   # 처리할 이미지 경로 설정
    output_path = 'data/result/masked_sample.jpg'   # 결과 이미지 저장 경로

    mask_faces_in_frame(image_path, registered_data, output_path=output_path)


if __name__ == "__main__":
    main()