import os
import hashlib
from save_frames_with_face_blur import save_frames_with_face_blur
from encrypt_frames import encrypt_all_frames
from decrypt_frames import decrypt_all_frames
from rebuild_video import frames_to_video

# AES 암호화에 사용할 키 설정 (32바이트 = 256비트)
key = hashlib.sha256(b'secret_key').digest()

def main():
    # 현재 디렉토리 설정
    current_dir = os.path.dirname(__file__)

    # 1. 비디오에서 프레임 추출
    video_path = os.path.join(current_dir, 'sample_video.mp4')
    frames_dir = os.path.join(current_dir, 'frames')
    face_cascade_path = os.path.join(current_dir, 'haarcascade_frontalface_default.xml')  # 얼굴 탐지 XML 파일 경로
    print("1단계: 비디오에서 프레임을 추출합니다...")
    save_frames_with_face_blur(video_path, frames_dir,face_cascade_path)

    # 2. 프레임을 암호화
    encrypted_frames_dir = os.path.join(current_dir, 'encrypted_frames')
    print("2단계: 프레임을 암호화합니다...")
    encrypt_all_frames(frames_dir, encrypted_frames_dir, key)

    # 3. 암호화된 프레임을 복호화
    decrypted_frames_dir = os.path.join(current_dir, 'decrypted_frames')
    print("3단계: 암호화된 프레임을 복호화합니다...")
    decrypt_all_frames(encrypted_frames_dir, decrypted_frames_dir, key)

    # 4. 복호화된 프레임을 영상으로 재구성
    output_video_path = os.path.join(current_dir, 'reconstructed_video.mp4')
    print("4단계: 복호화된 프레임을 영상으로 재구성합니다...")
    frames_to_video(decrypted_frames_dir, output_video_path)

    print("모든 단계가 완료되었습니다.")

if __name__ == "__main__":
    main()
