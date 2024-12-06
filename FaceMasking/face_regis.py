import cv2
import json
import os
from keras_facenet import FaceNet

# FaceNet 모델 로드
embedder = FaceNet()

# 얼굴 등록
def register_face_from_image(image_path, output_json_path, marked_image_path):
    image = cv2.imread(image_path)
    
    if image is None:
        print(f"이미지를 로드할 수 없습니다: {image_path}")
        return
    

    # 얼굴 임베딩 추출
    faces = embedder.extract(image, threshold=0.95)
    if not faces:
        print("이미지에서 얼굴을 찾을 수 없습니다.")
        return
    
    registered_data = []
    for face in faces:
        embedding = face['embedding']
        (x, y, w, h) = face['box']
        registered_data.append(embedding.tolist())

        # 얼굴 영역 표시 (선택사항)
        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
        print(f"얼굴 등록 완료 - 좌표: x={x}, y={y}, w={w}, h={h}")

        break  # 첫 번째 얼굴만 등록하고 종료

    if not registered_data:
        print("등록된 얼굴 데이터가 없습니다.")
        return
    
    # JSON 파일로 저장
    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
    with open(output_json_path, 'w') as f:
        json.dump(registered_data, f)
    print(f"등록된 얼굴 데이터가 저장되었습니다: {output_json_path}")

    # 얼굴이 표시된 이미지 저장 (선택사항)
    cv2.imwrite(marked_image_path, image)
    print(f"얼굴이 표시된 이미지가 저장되었습니다: {marked_image_path}")



def main():
    # 입력 이미지 경로 설정
    image_path = "data/face/face1.jpg"  # 얼굴 등록용 이미지 경로
    output_json_path = "data/json/sample.json"  # 저장될 JSON 파일 경로
    marked_image_path = "data/after_regis/masked_face1.jpg"

    # 얼굴 등록 수행
    register_face_from_image(image_path, output_json_path, marked_image_path)

if __name__ == "__main__":
    main()