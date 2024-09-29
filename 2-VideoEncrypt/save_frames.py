# 1_save_frames.py
import os
import cv2

def save_frames(video_path, output_dir):
    # 영상 파일 불러오기
    cap = cv2.VideoCapture(video_path)

    # FPS 정보 얻기
    fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"원본 영상 FPS: {fps}")

    # FPS 정보를 텍스트 파일로 저장
    fps_path = os.path.join(output_dir, 'fps.txt')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    with open(fps_path, 'w') as f:
        f.write(str(fps))

    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # 프레임 저장
        frame_path = os.path.join(output_dir, f'frame_{frame_count:04d}.png')  # 숫자 부분을 4자리로 맞추어 정렬이 쉽게 함
        cv2.imwrite(frame_path, frame)
        frame_count += 1

    cap.release()
    cv2.destroyAllWindows()

    print(f"총 {frame_count}개의 프레임이 저장되었습니다.")

# 실행 예시
if __name__ == "__main__":
    video_path = os.path.join(os.path.dirname(__file__), 'sample_video.mp4')
    output_dir = os.path.join(os.path.dirname(__file__), 'frames')
    save_frames(video_path, output_dir)
