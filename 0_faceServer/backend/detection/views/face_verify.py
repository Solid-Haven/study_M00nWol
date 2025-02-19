import os
import json
import cv2
import numpy as np
import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from insightface.app import FaceAnalysis

# ArcFace 모델 로드
app = FaceAnalysis(name="buffalo_l")
app.prepare(ctx_id=-1)  # CPU 사용

# YOLO 모델 로드
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
YOLO_WEIGHTS = os.path.join(BASE_DIR, "model", "yolov4-tiny.weights")
YOLO_CFG = os.path.join(BASE_DIR, "model", "yolov4-tiny.cfg")

# 임베딩 저장 경로
EMBEDDING_DIR = os.path.join(BASE_DIR, "embeddings")
DETECTED_DIR = os.path.join(BASE_DIR, "detected")
os.makedirs(EMBEDDING_DIR, exist_ok=True)  # 폴더 생성
os.makedirs(DETECTED_DIR, exist_ok=True)  # 폴더 생성

@csrf_exempt
def verify_face(request):
    """ 업로드된 얼굴을 등록된 얼굴과 비교하여 인증 및 얼굴 저장 """
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "잘못된 요청입니다."}, status=405)

    if "face_image" not in request.FILES or "user_id" not in request.POST:
        return JsonResponse({"status": "error", "message": "사용자 ID 또는 이미지 데이터가 누락되었습니다."}, status=400)

    user_id = request.POST["user_id"].strip()
    embedding_path = os.path.join(EMBEDDING_DIR, f"{user_id}_embedding.json")

    if not os.path.exists(embedding_path):
        return JsonResponse({"status": "error", "message": "해당 ID의 얼굴 데이터가 존재하지 않습니다."}, status=404)

    # ✅ 저장된 임베딩 불러오기
    with open(embedding_path, "r") as f:
        stored_embedding = np.array(json.load(f))

    # ✅ 업로드된 얼굴 이미지 처리
    image_file = request.FILES["face_image"]
    image_bytes = image_file.read()
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if image is None:
        print("❌ 이미지 디코딩 실패!")
        return JsonResponse({"status": "error", "message": "이미지를 읽을 수 없습니다."}, status=400)

    # ✅ YOLO를 이용한 얼굴 검출
    faces = detect_face(image)
    if len(faces) == 0:
        print("❌ 얼굴 감지 실패! YOLO가 얼굴을 찾지 못함.")
        return JsonResponse({"status": "error", "message": "얼굴을 감지하지 못했습니다."}, status=400)

    print(f"✅ 감지된 얼굴 개수: {len(faces)}")

    highest_similarity = -1
    best_match = None
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    for i, (x, y, w, h) in enumerate(faces):
        # 🚀 좌표 보정 (음수 및 이미지 경계 초과 방지)
        x = max(0, x)
        y = max(0, y)
        w = min(w, image.shape[1] - x)
        h = min(h, image.shape[0] - y)

        # 🚀 얼굴 크기 검증
        if w < 20 or h < 20:
            print(f"❌ 얼굴 크롭 실패! (index {i}) 감지된 크기가 너무 작음. (w={w}, h={h})")
            continue

        face_crop = image[y:y+h, x:x+w]

        if face_crop.size == 0:
            print(f"❌ 얼굴 크롭 실패! (index {i}) YOLO의 좌표가 잘못됨.")
            continue

        face_crop = cv2.resize(face_crop, (112, 112))
        face_crop = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)

        # ✅ 감지된 얼굴을 파일로 저장
        save_path = os.path.join(DETECTED_DIR, f"{now}_{i}.jpg")
        cv2.imwrite(save_path, face_crop)
        print(f"📸 얼굴 저장 완료: {save_path}")

        # ✅ ArcFace로 임베딩 추출
        face_data = app.get(np.asarray(face_crop))
        if len(face_data) == 0:
            print(f"❌ ArcFace가 얼굴을 인식하지 못함! (index {i})")
            continue

        uploaded_embedding = np.array(face_data[0].normed_embedding)

        # ✅ 코사인 유사도 계산
        similarity = np.dot(uploaded_embedding, stored_embedding)

        print(f"🧐 얼굴 비교 (index {i}) - 유사도: {similarity:.4f}")

        # 가장 높은 유사도 기록
        if similarity > highest_similarity:
            highest_similarity = similarity
            best_match = similarity

        # ✅ 얼굴 박스 그리기
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv2.putText(image, f"{similarity:.3f}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # ✅ 감지된 얼굴이 그려진 이미지 저장
    debug_image_path = os.path.join(DETECTED_DIR, f"{now}_detected.jpg")
    cv2.imwrite(debug_image_path, image)
    print(f"🖼 감지된 얼굴 박스 저장 완료: {debug_image_path}")

    # ✅ 가장 높은 유사도를 기준으로 인증 성공 여부 결정
    if best_match is not None and best_match > 0.5:
        return JsonResponse({
            "status": "success",
            "message": "인증 성공! 동일한 얼굴입니다.",
            "similarity": float(best_match),
            "saved_faces": debug_image_path
        })

    return JsonResponse({
        "status": "fail",
        "message": "인증 실패! 일치하는 얼굴을 찾을 수 없습니다.",
        "similarity": float(highest_similarity) if best_match is not None else 0,
        "saved_faces": debug_image_path
    })


def detect_face(image):
    """ YOLO를 이용한 얼굴 검출 및 중복 제거 (NMS 적용) """
    YOLO_NET = cv2.dnn.readNetFromDarknet(YOLO_CFG, YOLO_WEIGHTS)
    YOLO_NET.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
    YOLO_NET.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

    height, width = image.shape[:2]
    blob = cv2.dnn.blobFromImage(image, 1/255.0, (416, 416), swapRB=True, crop=False)
    YOLO_NET.setInput(blob)
    outputs = YOLO_NET.forward(YOLO_NET.getUnconnectedOutLayersNames())

    boxes = []
    confidences = []
    
    for output in outputs:
        for detection in output:
            scores = detection[5:]  # 클래스 신뢰도 값들
            confidence = max(scores)  # 가장 높은 신뢰도 선택
            if confidence > 0.6:  # 신뢰도 임계값 설정
                center_x, center_y, w, h = (detection[:4] * np.array([width, height, width, height])).astype("int")
                x, y = int(center_x - w / 2), int(center_y - h / 2)
                
                # 박스와 신뢰도 추가
                boxes.append([x, y, w, h])
                confidences.append(float(confidence))

    # ✅ NMS 적용하여 중복된 박스 제거
    indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

    final_faces = []
    if len(indices) > 0:
        for i in indices.flatten():
            final_faces.append(boxes[i])

    return final_faces