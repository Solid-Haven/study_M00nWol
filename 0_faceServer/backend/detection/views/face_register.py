import os
import json
import cv2
import numpy as np
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from insightface.app import FaceAnalysis

# ArcFace 모델 로드
app = FaceAnalysis(name="buffalo_l")
app.prepare(ctx_id=-1)  # CPU 사용 (GPU는 ctx_id=0)

# YOLO 모델 로드
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
YOLO_WEIGHTS = os.path.join(BASE_DIR, "model", "yolov4-tiny.weights")
YOLO_CFG = os.path.join(BASE_DIR, "model", "yolov4-tiny.cfg")

YOLO_NET = cv2.dnn.readNetFromDarknet(YOLO_CFG, YOLO_WEIGHTS)
YOLO_NET.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
YOLO_NET.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

# 저장 경로 설정
EMBEDDING_DIR = os.path.join(BASE_DIR, "embeddings")
os.makedirs(EMBEDDING_DIR, exist_ok=True)

MAX_CAPTURE = 5  # 🚀 5장의 사진으로 평균 임베딩 생성


@csrf_exempt
def register_face(request):
    """ 사용자의 얼굴을 5장 촬영하여 평균 임베딩을 저장하는 API """
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "잘못된 요청입니다."}, status=405)

    user_id = request.POST.get("user_id", "unknown")
    images = request.FILES.getlist("face_images")

    if not images:
        return JsonResponse({"status": "error", "message": "이미지가 감지되지 않았습니다."}, status=400)

    embeddings_list = []

    for index, image_file in enumerate(images):
        image_bytes = image_file.read()
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # YOLO 얼굴 감지
        faces = detect_face(image)
        if len(faces) == 0:
            print(f"❌ {index + 1}/{len(images)}: 얼굴 감지 실패")
            continue  # 얼굴이 감지되지 않으면 스킵

        # ArcFace 임베딩 추출 (첫 번째 얼굴만)
        x, y, w, h = faces[0]
        face_crop = image[y:y+h, x:x+w]  
        face_crop = cv2.resize(face_crop, (112, 112))
        face_crop = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)

        face_data = app.get(np.asarray(face_crop))
        if len(face_data) > 0:
            embeddings_list.append(face_data[0].normed_embedding)
            print(f"✅ {index + 1}/{len(images)}: 얼굴 임베딩 저장됨 ({len(embeddings_list)}/{MAX_CAPTURE})")

        if len(embeddings_list) >= MAX_CAPTURE:
            break  # 5개 임베딩만 사용

    if len(embeddings_list) == 0:
        return JsonResponse({"status": "error", "message": "얼굴을 감지하지 못했습니다."}, status=400)

    # 평균 임베딩 생성 및 저장
    avg_embedding = np.mean(embeddings_list, axis=0).tolist()
    embedding_path = os.path.join(EMBEDDING_DIR, f"{user_id}_embedding.json")

    with open(embedding_path, "w") as f:
        json.dump(avg_embedding, f, indent=4)

    return JsonResponse({
        "message": "얼굴 등록이 완료되었습니다!",
        "embedding_path": embedding_path,
        "embedding_count": len(embeddings_list)  # ✅ 진행 상황 응답에 포함
    })


def detect_face(image):
    """ YOLO를 이용한 얼굴 검출 및 bounding box 반환 """
    height, width = image.shape[:2]
    blob = cv2.dnn.blobFromImage(image, 1/255.0, (416, 416), swapRB=True, crop=False)
    YOLO_NET.setInput(blob)
    outputs = YOLO_NET.forward(YOLO_NET.getUnconnectedOutLayersNames())

    faces = []
    for output in outputs:
        for detection in output:
            confidence = detection[5]
            if confidence > 0.5:
                center_x, center_y, w, h = (detection[:4] * np.array([width, height, width, height])).astype("int")
                x, y = int(center_x - w / 2), int(center_y - h / 2)
                faces.append((x, y, w, h))

    return faces
