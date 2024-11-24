import cv2
import mediapipe as mp
import json
import os

# 데이터셋 폴더 경로 설정
dataset_folder = "dataset/raw"  # 원본 샘플 이미지가 있는 폴더
json_folder = "dataset/json"    # JSON 파일을 저장할 폴더
image_folder = "dataset/image"  # 결과 이미지를 저장할 폴더

# 결과 저장 폴더 생성
for folder in [json_folder, image_folder]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# Mediapipe 초기화
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True)

# 랜드마크 이름 정의
landmark_names = {
    0: "Nose",
    1: "Left Eye (Inner)",
    2: "Left Eye",
    3: "Left Eye (Outer)",
    4: "Right Eye (Inner)",
    5: "Right Eye",
    6: "Right Eye (Outer)",
    7: "Left Ear",
    8: "Right Ear",
    9: "Mouth (Left)",
    10: "Mouth (Right)",
    11: "Left Shoulder",
    12: "Right Shoulder",
    13: "Left Elbow",
    14: "Right Elbow",
    15: "Left Wrist",
    16: "Right Wrist",
    17: "Left Pinky",
    18: "Right Pinky",
    19: "Left Index",
    20: "Right Index",
    21: "Left Thumb",
    22: "Right Thumb",
    23: "Left Hip",
    24: "Right Hip",
    25: "Left Knee",
    26: "Right Knee",
    27: "Left Ankle",
    28: "Right Ankle",
    29: "Left Heel",
    30: "Right Heel",
    31: "Left Foot Index",
    32: "Right Foot Index"
}

# 폴더 내 모든 이미지 파일 처리
for index, image_file in enumerate(sorted(os.listdir(dataset_folder))):  # 정렬 후 순차 처리
    if not image_file.lower().endswith(('.png', '.jpg', '.jpeg')):
        continue  # 이미지 파일만 처리

    # 순번 추가
    nth_label = f"{index + 1:04d}"  # 4자리 형식 (001, 002, ...)
    json_output_path = os.path.join(json_folder, f"image_{nth_label}.json")
    image_output_path = os.path.join(image_folder, f"image_{nth_label}.jpg")

    # 이미지 경로 설정
    image_path = os.path.join(dataset_folder, image_file)
    
    # 이미지 로드
    image = cv2.imread(image_path)
    if image is None:
        print(f"이미지를 불러오지 못했습니다: {image_path}")
        continue
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # 신체 랜드마크 감지
    results = pose.process(image_rgb)

    # JSON 데이터 생성
    landmark_data = []
    important_landmarks = []

    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark

        # 기존 랜드마크 데이터 저장
        for idx, lm in enumerate(landmarks):
            landmark_data.append({
                "id": idx,
                "name": landmark_names[idx],
                "x": lm.x,
                "y": lm.y,
                "z": lm.z,
                "visibility": lm.visibility
            })

        # 중요 부위 계산
        left_shoulder = landmarks[11]
        right_shoulder = landmarks[12]
        left_hip = landmarks[23]
        right_hip = landmarks[24]
        left_knee = landmarks[25]
        right_knee = landmarks[26]

        # 가슴 (Chest)
        chest_x = (left_shoulder.x + right_shoulder.x) / 2
        chest_y = (left_shoulder.y + right_shoulder.y) / 2
        important_landmarks.append({"id": 33, "name": "Chest", "x": chest_x, "y": chest_y})

        # 배꼽 (Navel)
        navel_x = (chest_x + left_hip.x + right_hip.x) / 3
        navel_y = (chest_y + left_hip.y + right_hip.y) / 3
        important_landmarks.append({"id": 34, "name": "Navel", "x": navel_x, "y": navel_y})

        # 성기 (Genital)
        genital_x = (left_hip.x + right_hip.x + left_knee.x + right_knee.x) / 4
        genital_y = (left_hip.y + right_hip.y + left_knee.y + right_knee.y) / 4
        important_landmarks.append({"id": 35, "name": "Genital", "x": genital_x, "y": genital_y})

        # 복부 (Abdomen)
        abdomen_x = (navel_x + left_hip.x + right_hip.x) / 3
        abdomen_y = (navel_y + left_hip.y + right_hip.y) / 3
        important_landmarks.append({"id": 36, "name": "Abdomen", "x": abdomen_x, "y": abdomen_y})

        # 등 (Center Back)
        back_x = (left_shoulder.x + right_shoulder.x + left_hip.x + right_hip.x) / 4
        back_y = (left_shoulder.y + right_shoulder.y + left_hip.y + right_hip.y) / 4
        important_landmarks.append({"id": 37, "name": "Center Back", "x": back_x, "y": back_y})

        # 허벅지 중심 (Thigh Center)
        thigh_x = (left_hip.x + right_hip.x + left_knee.x + right_knee.x) / 4
        thigh_y = (left_hip.y + right_hip.y + left_knee.y + right_knee.y) / 4
        important_landmarks.append({"id": 38, "name": "Thigh Center", "x": thigh_x, "y": thigh_y})

    # JSON 데이터 저장
    output_data = {
        "pose_landmarks": landmark_data,
        "important_landmarks": important_landmarks
    }
    with open(json_output_path, "w") as json_file:
        json.dump(output_data, json_file, indent=4)

    # 랜드마크 그리기
    for landmark in landmark_data:
        x = int(landmark["x"] * image.shape[1])
        y = int(landmark["y"] * image.shape[0])
        name = landmark["name"]
        cv2.circle(image, (x, y), 5, (0, 255, 0), -1)  # 초록색 원
        cv2.putText(image, name, (x + 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

    for important in important_landmarks:
        x = int(important["x"] * image.shape[1])
        y = int(important["y"] * image.shape[0])
        name = important["name"]
        cv2.circle(image, (x, y), 8, (255, 0, 0), -1)  # 파란색 원
        cv2.putText(image, name, (x + 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    # 결과 이미지 저장
    cv2.imwrite(image_output_path, image)
    print(f"{nth_label}번째 처리 완료: {image_file}, JSON 저장: {json_output_path}, 이미지 저장: {image_output_path}")

pose.close()
print("모든 이미지 처리 완료.")
