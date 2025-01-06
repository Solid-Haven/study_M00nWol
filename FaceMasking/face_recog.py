import cv2
import numpy as np
import json
from keras_facenet import FaceNet
from scipy.spatial.distance import cosine
import os

# FaceNet 모델 로드
embedder = FaceNet()

def normalize_embedding(embedding):
    return embedding / np.linalg.norm(embedding)

def load_registered_faces(json_folder):
    """
    JSON 폴더에서 등록된 얼굴 데이터 로드
    """
    if not os.path.exists(json_folder):
        print(f"등록된 JSON 폴더를 찾을 수 없습니다: {json_folder}")
        return []

    registered_data = []
    for file_name in os.listdir(json_folder):
        if file_name.endswith('.json'):  # JSON 파일만 처리
            json_path = os.path.join(json_folder, file_name)
            try:
                with open(json_path, 'r') as f:
                    data = json.load(f)
                embedding = data.get('embedding', None)
                if embedding:
                    registered_data.append(normalize_embedding(np.array(embedding).flatten()))
                else:
                    print(f"{file_name}: 'embedding' 키가 없습니다.")
            except json.JSONDecodeError as e:
                print(f"{file_name}: JSON 파일 파싱 중 오류 발생: {e}")
    return registered_data

def mask_faces(image, registered_data, similarity_threshold):
    """
    이미지 내 얼굴을 등록된 데이터와 비교해 마스킹.
    """
    try:
        faces = embedder.extract(image, threshold=0.95) if registered_data else []
        if not faces:
            print("이미지에서 얼굴을 찾을 수 없거나 JSON 데이터가 없습니다.")
            return image
    except Exception as e:
        print(f"얼굴 검출 중 오류가 발생했습니다: {e}")
        return image

    # 얼굴 마스킹 수행
    for face in faces:
        current_embedding = normalize_embedding(np.array(face['embedding']).flatten())
        for registered_embedding in registered_data:
            similarity = 1 - cosine(registered_embedding, current_embedding)
            if similarity > similarity_threshold:  # 유사도 기준 초과
                (x, y, w, h) = face['box']
                face_region = image[y:y + h, x:x + w]
                face_region = cv2.GaussianBlur(face_region, (99, 99), 30)  # 가우시안 블러
                image[y:y + h, x:x + w] = face_region
                break  # 한 번 일치하면 해당 얼굴 마스킹 완료
    return image

def process_frame(image_path, json_dir, output_path, similarity_threshold):
    """
    한 프레임을 JSON 데이터와 비교하고, 마스킹한 이미지를 저장.
    """
    # 이미지 로드
    image = cv2.imread(image_path)
    if image is None:
        print(f"이미지를 로드할 수 없습니다: {image_path}")
        return

    # JSON 데이터 로드
    registered_data = load_registered_faces(json_dir)
    if not registered_data:
        print("등록된 얼굴 데이터가 없습니다. 원본 이미지를 저장합니다.")
        cv2.imwrite(output_path, image)
        return

    # 얼굴 마스킹 수행
    masked_image = mask_faces(image, registered_data, similarity_threshold)

    # 결과 이미지 저장
    cv2.imwrite(output_path, masked_image)
    print(f"이미지가 저장되었습니다: {output_path}")
