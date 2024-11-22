import cv2
import json

# 경로 설정
image_path = "sample1.jpg"
json_path = "pose_landmarks.json"
output_image_path = "output_with_landmarks.jpg"

# JSON 데이터 로드
with open(json_path, "r") as json_file:
    data = json.load(json_file)

# 이미지 로드
image = cv2.imread(image_path)

# 랜드마크 그리기
for landmark in data["pose_landmarks"]:
    x = int(landmark["x"] * image.shape[1])
    y = int(landmark["y"] * image.shape[0])
    visibility = landmark["visibility"]
    name = landmark["name"]

    
    cv2.circle(image, (x, y), 5, (0, 255, 0), -1)  # 초록색 원
    cv2.putText(image, name, (x + 20, y - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)


for important in data.get("important_landmarks", []):  # 중요 부위가 있으면 표시
    x = int(important["x"] * image.shape[1])
    y = int(important["y"] * image.shape[0])
    name = important["name"]

    # 중요 부위는 파란색 원과 이름 텍스트로 표시
    cv2.circle(image, (x, y), 8, (255, 0, 0), -1)  # 파란색 원
    cv2.putText(image, name, (x + 20, y - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

# 결과 이미지 저장
cv2.imwrite(output_image_path, image)
print(f"결과 이미지가 저장되었습니다: {output_image_path}")
