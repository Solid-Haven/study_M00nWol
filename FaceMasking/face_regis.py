import cv2
import json
import os
from keras_facenet import FaceNet

# FaceNet 모델 로드
embedder = FaceNet()

# 얼굴 등록
def register_face_from_image(image_path, output_json_dir, marked_image_dir):
    # 이미지 파일 이름 추출
    image_name = os.path.splitext(os.path.basename(image_path))[0]  # 파일명(확장자 제외)
    output_json_path = f"{output_json_dir}/{image_name}.json"  # JSON 파일 경로
    marked_image_path = f"{marked_image_dir}/marked_{image_name}.jpg"  # 마스크된 이미지 경로

    # 이미지 로드
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

        # 등록 데이터 형식에 맞게 수정
        registered_data = {
            "user_id": 3,  # 여기에서 user_id를 설정
            "embedding": embedding.tolist()
        }

        # 얼굴 영역 표시
        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
        print(f"얼굴 등록 완료 - 좌표: x={x}, y={y}, w={w}, h={h}")

        break  # 첫 번째 얼굴만 등록하고 종료

    if not registered_data:
        print("등록된 얼굴 데이터가 없습니다.")
        return
    
    # JSON 파일로 저장
    os.makedirs(output_json_dir, exist_ok=True)
    with open(output_json_path, 'w') as f:
        json.dump(registered_data, f, indent=4)
    print(f"등록된 얼굴 데이터가 저장되었습니다: {output_json_path}")

    # 얼굴이 표시된 이미지 저장
    os.makedirs(marked_image_dir, exist_ok=True)
    cv2.imwrite(marked_image_path, image)
    print(f"얼굴이 표시된 이미지가 저장되었습니다: {marked_image_path}")

def main():
    # 입력 이미지 경로 설정
    image_path = "face/before_regis/face1.jpg"  # 얼굴 등록용 이미지 경로
    output_json_dir = "face/json"  # 저장될 JSON 디렉토리
    marked_image_dir = "face/after_regis"  # 마스크 처리된 이미지 저장 디렉토리

    # 얼굴 등록 수행
    register_face_from_image(image_path, output_json_dir, marked_image_dir)

if __name__ == "__main__":
    main()
