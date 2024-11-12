# masking/views.py

from django.http import JsonResponse
from .masker import apply_mask
import cv2
import numpy as np
import boto3

def mask_video_frame(request):
    if request.method == 'POST' and request.FILES['frame']:
        try:
            frame_file = request.FILES['frame'].read()
            np_frame = np.frombuffer(frame_file, np.uint8)
            frame = cv2.imdecode(np_frame, cv2.IMREAD_COLOR)

            # AI 마스킹 함수 호출
            masked_frame = apply_mask(frame)

            # EC2 내 test 폴더에 마스킹된 프레임 저장
            frame_count = request.POST.get('frame_count', '0')  # 프레임 번호를 받아서 파일 이름에 추가
            output_path = f"/home/ec2-user/test/masked_frame_{frame_count}.jpg"
            cv2.imwrite(output_path, masked_frame)

            return JsonResponse({'status': 'success', 'saved_path': output_path})
    
        except Exception as e:
            return JsonResponse({'status': 'failed', 'error': str(e)}, status=500)
        
    return JsonResponse({'status': 'failed', 'error': 'No frame found or wrong method'}, status=400)
