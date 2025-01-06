import cv2
import os
import subprocess

# FFmpeg 실행 파일 경로 설정 (FFmpeg의 절대 경로를 지정하세요)
FFMPEG_PATH = "C:/ffmpeg/bin/ffprobe.exe"  # FFmpeg의 ffprobe 실행 파일 경로

def get_exact_fps(video_path):
    """
    FFmpeg를 사용하여 비디오의 정확한 FPS를 추출.
    """
    try:
        result = subprocess.run(
            [FFMPEG_PATH, "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate", "-of", "default=noprint_wrappers=1:nokey=1", video_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        fps_str = result.stdout.strip()
        # FPS 계산 (분수 형태를 소수로 변환)
        numerator, denominator = map(int, fps_str.split('/'))
        return numerator / denominator
    except Exception as e:
        print(f"FFmpeg를 사용하여 FPS를 추출하는 데 실패했습니다: {e}")
        return None

def save_frames(video_path, frames_dir, fps_dir):
    # 비디오 파일 이름 추출
    video_name = video_path.split('/')[-1].split('.')[0]  # 파일명 추출 (확장자 제거)

    # 프레임 저장 폴더 생성
    video_frames_dir = f"{frames_dir}/{video_name}"  # 프레임 저장 디렉토리
    fps_file_output_path = f"{fps_dir}/{video_name}.txt"  # FPS 저장 경로

    # 디렉토리 생성
    if not os.path.exists(video_frames_dir):
        os.makedirs(video_frames_dir)
    if not os.path.exists(fps_dir):
        os.makedirs(fps_dir)

    # 정확한 FPS 가져오기
    exact_fps = get_exact_fps(video_path)
    if exact_fps is not None:
        print(f"정확한 FPS: {exact_fps:.6f}")
    else:
        print("정확한 FPS를 가져오지 못했습니다. OpenCV에서 FPS 값을 사용합니다.")

    # OpenCV로 비디오 파일 읽기
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    if exact_fps is None:
        exact_fps = fps

    # FPS 정보 저장
    with open(fps_file_output_path, 'w') as f:
        f.write(f"{exact_fps:.6f}")  # 파일에도 소수점 6자리로 저장

    frame_count = 0

    # 비디오의 각 프레임 저장
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_file_path = f"{video_frames_dir}/frame_{frame_count:04d}.png"  # 4자리 숫자로 정렬
        cv2.imwrite(frame_file_path, frame)
        frame_count += 1

    cap.release()
    cv2.destroyAllWindows()

    print(f"총 {frame_count}개의 프레임이 {video_frames_dir}에 저장되었습니다.")
    print(f"FPS 정보는 {fps_file_output_path}에 저장되었습니다.")

# 실행 예시
if __name__ == "__main__":
    video_path = 'before/video/2024-12-14.mp4'  # 처리할 비디오 경로
    frames_dir = 'before/frame'  # 프레임 저장 기본 경로
    fps_dir = 'after/ftp'  # FPS 정보 저장 기본 경로

    save_frames(video_path, frames_dir, fps_dir)
