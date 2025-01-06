import cv2
import os

def make_video(frames_dir, fps_file, output_video_path):
    # 프레임 디렉토리 확인
    if not os.path.exists(frames_dir):
        print(f"프레임 디렉토리를 찾을 수 없습니다: {frames_dir}")
        return

    # FPS 파일 읽기
    if not os.path.exists(fps_file):
        print(f"FPS 파일을 찾을 수 없습니다: {fps_file}")
        return
    
    with open(fps_file, 'r') as f:
        try:
            fps = float(f.read().strip())
        except ValueError:
            print(f"FPS 파일에서 유효한 값을 읽을 수 없습니다: {fps_file}")
            return

    # 프레임 파일 목록 정렬
    frame_files = sorted([f for f in os.listdir(frames_dir) if f.endswith((".png", ".jpg"))])
    if not frame_files:
        print(f"프레임 파일이 디렉토리에 없습니다: {frames_dir}")
        return

    # 첫 번째 프레임으로 영상 크기 설정
    first_frame_path = os.path.join(frames_dir, frame_files[0])
    frame = cv2.imread(first_frame_path)
    if frame is None:
        print(f"첫 번째 프레임을 읽을 수 없습니다: {first_frame_path}")
        return

    height, width, _ = frame.shape

    # 비디오 작성자 초기화
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # MP4 코덱
    video_writer = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

    # 모든 프레임을 비디오에 추가
    for frame_file in frame_files:
        frame_path = os.path.join(frames_dir, frame_file)
        frame = cv2.imread(frame_path)
        if frame is None:
            print(f"프레임을 읽을 수 없습니다: {frame_path}")
            continue
        video_writer.write(frame)

    video_writer.release()
    print(f"비디오가 생성되었습니다: {output_video_path}")

def main():
    # after 디렉토리 설정
    frame_dir = "after/frame/2024-12-14"  # 비디오 이름에 따라 변경 가능
    fps_file = "after/ftp/2024-12-14.txt"  # FPS 파일 경로
    output_video = "after/video/masked_2024-12-14.mp4"  # 출력 비디오 경로

    make_video(frame_dir, fps_file, output_video)

if __name__ == "__main__":
    main()
