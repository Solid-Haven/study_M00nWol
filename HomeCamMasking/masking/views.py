# masking/views.py

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .masker import apply_mask
import cv2
import numpy as np
import os
from django.conf import settings
from datetime import datetime

@csrf_exempt
def mask_video_frame(request):
    if request.method == 'POST' and request.FILES.get('frame'):
        frame_file = request.FILES['frame'].read()
        np_frame = np.frombuffer(frame_file, np.uint8)
        frame = cv2.imdecode(np_frame, cv2.IMREAD_COLOR)

        # 마스킹 처리
        masked_frame = apply_mask(frame)

        # 서버에 저장할 파일 경로 생성
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        file_name = f"masked_{timestamp}.jpg"
        save_path = os.path.join(settings.MEDIA_ROOT, file_name)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        # 마스킹된 프레임을 파일로 저장
        cv2.imwrite(save_path, masked_frame)

        # 파일의 상대 경로 URL을 클라이언트에게 반환
        file_url = f"{settings.MEDIA_URL}{file_name}"
        return JsonResponse({'status': 'success', 'file_url': file_url})

    return JsonResponse({'status': 'failed'}, status=400)
