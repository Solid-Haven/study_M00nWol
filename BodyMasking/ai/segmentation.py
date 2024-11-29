import cv2
import numpy as np
import os
import json
import re

# 신체/의상 구분 함수들
def detect_skin(image):
    """피부 탐지를 위해 HSV 또는 밝기 기반으로 신체 마스크 생성."""
    if len(image.shape) == 3:  # 컬러 이미지인 경우
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower_bound = np.array([0, 40, 60], dtype=np.uint8)  # HSV 피부 범위
        upper_bound = np.array([20, 150, 255], dtype=np.uint8)
        skin_mask = cv2.inRange(hsv_image, lower_bound, upper_bound)
    else:  # 흑백 이미지인 경우
        lower_bound = 100
        upper_bound = 200
        skin_mask = cv2.inRange(image, lower_bound, upper_bound)
    return skin_mask

def refine_skin_mask_with_landmarks(mask, landmarks, image_shape, radius=50):
    """랜드마크를 사용하여 신체 마스크를 정제."""
    refined_mask = np.zeros_like(mask, dtype=np.uint8)
    for lm in landmarks:
        x = int(lm['x'] * image_shape[1])
        y = int(lm['y'] * image_shape[0])
        cv2.circle(refined_mask, (x, y), radius, 255, -1)  # 랜드마크 주변 원형 영역 포함
    refined_mask = cv2.bitwise_and(mask, refined_mask)  # 기존 마스크와 결합
    return refined_mask

def segment_body_clothing(image, landmarks):
    """신체와 의상을 분리."""
    skin_mask = detect_skin(image)  # 피부 탐지
    refined_mask = refine_skin_mask_with_landmarks(skin_mask, landmarks, image.shape)  # 랜드마크로 보정
    body_segment = cv2.bitwise_and(image, image, mask=refined_mask)  # 신체만 남김
    return refined_mask, body_segment

# 분석 함수들
def calculate_exposure_ratio(mask, landmarks, image_shape):
    """랜드마크 기반으로 중심 부위의 노출 비율 계산."""
    center_exposure = {}
    h, w = image_shape[:2]

    for lm in landmarks:
        x, y = int(lm['x'] * w), int(lm['y'] * h)
        roi = mask[max(0, y-30):min(h, y+30), max(0, x-30):min(w, x+30)]  # 30px 반경 영역
        center_exposure[lm['name']] = np.sum(roi == 255) / (roi.size)  # 흰색 비율 계산

    return center_exposure

def calculate_body_clothing_ratio(mask):
    """신체와 의상의 픽셀 비율 계산."""
    body_pixels = np.sum(mask == 255)  # 흰색 픽셀 수
    total_pixels = mask.size  # 전체 픽셀 수
    body_ratio = body_pixels / total_pixels
    return body_ratio


def calculate_overall_exposure(mask):
    """전체 신체 노출 비율 계산."""
    total_pixels = mask.size
    exposed_pixels = np.sum(mask == 255)
    return exposed_pixels / total_pixels  # 전체 영역 대비 노출 비율

def analyze_sensitivity(center_exposure):
    """민감 부위 노출 분석."""
    sensitive_areas = ['Chest', 'Navel', 'Genital']
    sensitivity_scores = {area: center_exposure.get(area, 0) for area in sensitive_areas}
    return sensitivity_scores

# JSON 파일 매칭
def find_matching_json(image_name, json_folder):
    """이미지 파일명과 매칭되는 JSON 파일 찾기."""
    image_id = re.search(r'\d+', image_name).group()  # sample_0001 -> 0001
    for json_file in os.listdir(json_folder):
        if image_id in json_file and json_file.endswith('.json'):
            return os.path.join(json_folder, json_file)
    return None  # 매칭되는 JSON 파일이 없으면 None 반환

def load_body_coordinates(json_path):
    """JSON 파일에서 신체 좌표 로드."""
    with open(json_path, "r") as f:
        data = json.load(f)
    return data.get("pose_landmarks", [])

# 메인 함수
def process_images_and_json(input_folder, json_folder, output_folder):
    """이미지와 JSON 데이터를 기반으로 신체/의상 분리."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for file_name in os.listdir(input_folder):
        if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
            # 이미지 및 JSON 경로 설정
            image_path = os.path.join(input_folder, file_name)
            json_path = find_matching_json(file_name, json_folder)

            if not json_path:
                print(f"No matching JSON for {file_name}")
                continue

            # 이미지 및 JSON 로드
            image = cv2.imread(image_path)
            if image is None:
                print(f"Failed to load image: {image_path}")
                continue

            landmarks = load_body_coordinates(json_path)

            # 신체와 의상 분리
            refined_mask, body_segment = segment_body_clothing(image, landmarks)

            # 노출 및 비율 계산
            center_exposure = calculate_exposure_ratio(refined_mask, landmarks, image.shape)
            body_ratio = calculate_body_clothing_ratio(refined_mask)

            # 결과 출력
            print(f"\nProcessed {file_name}:")
            print(f" - Center Exposure Ratios: {center_exposure}")
            print(f" - Body-to-Clothing Ratio: {body_ratio}")

            # 결과 저장
            base_name = os.path.splitext(file_name)[0]
            mask_output_path = os.path.join(output_folder, f"segmentation_{base_name}_mask.png")
            segmented_output_path = os.path.join(output_folder, f"segmentation_{base_name}_segmented.png")
            # 전체 노출 비율
            overall_exposure = calculate_overall_exposure(refined_mask)
            # 민감 부위 노출
            sensitivity_scores = analyze_sensitivity(center_exposure)
            
            print(f"Overall Exposure Ratio: {overall_exposure:.2f}")
            print(f"Sensitivity Scores: {sensitivity_scores}")
            cv2.imwrite(mask_output_path, refined_mask)
            cv2.imwrite(segmented_output_path, body_segment)
            print(f" - Saved mask to {mask_output_path}")
            print(f" - Saved segmented image to {segmented_output_path}")

# 실행
if __name__ == "__main__":
    input_folder = "../dataset/raw"  # 이미지 폴더
    json_folder = "../dataset/json"  # JSON 폴더
    output_folder = "../result/segmentation"  # 결과 저장 폴더
    process_images_and_json(input_folder, json_folder, output_folder)
    
