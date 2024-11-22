import cv2
import mediapipe as mp
import json

# 이미지 경로
image_path = "sample1.jpg"
output_json_path = "pose_landmarks.json"

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

# Mediapipe 초기화
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True)

# 이미지 로드
image = cv2.imread(image_path)
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
    left_shoulder = landmarks[11]  # 왼쪽 어깨
    right_shoulder = landmarks[12]  # 오른쪽 어깨
    left_hip = landmarks[23]  # 왼쪽 엉덩이
    right_hip = landmarks[24]  # 오른쪽 엉덩이
    left_knee = landmarks[25]  # 왼쪽 무릎
    right_knee = landmarks[26]  # 오른쪽 무릎

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
with open(output_json_path, "w") as json_file:
    json.dump(output_data, json_file, indent=4)

pose.close()
print(f"JSON 파일이 저장되었습니다: {output_json_path}")