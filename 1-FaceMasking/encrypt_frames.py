import os
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

# AES 암호화에 사용할 키 설정 (32바이트 = 256비트)
key = hashlib.sha256(b'secret_key').digest()

def encrypt_frame(frame_data, key):
    cipher = AES.new(key, AES.MODE_CBC)
    encrypted_data = cipher.encrypt(pad(frame_data, AES.block_size))
    return cipher.iv + encrypted_data  # IV(초기화 벡터) + 암호화된 데이터 반환

def encrypt_all_frames(input_dir, output_dir, key):
    # 암호화된 프레임을 저장할 디렉토리 생성
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    frame_files = sorted([f for f in os.listdir(input_dir) if f.endswith('.png')])
    frame_count = 0

    for frame_file in frame_files:
        frame_path = os.path.join(input_dir, frame_file)

        # 프레임 데이터 읽기
        with open(frame_path, 'rb') as f:
            frame_data = f.read()

        # 프레임 데이터 암호화
        encrypted_frame = encrypt_frame(frame_data, key)

        # 암호화된 프레임을 파일로 저장
        encrypted_frame_path = os.path.join(output_dir, f'encrypted_{frame_file}.enc')
        with open(encrypted_frame_path, 'wb') as f:
            f.write(encrypted_frame)

        frame_count += 1

    print(f"총 {frame_count}개의 프레임이 암호화되었습니다.")

# 실행 예시
if __name__ == "__main__":
    input_dir = os.path.join(os.path.dirname(__file__), 'frames')
    output_dir = os.path.join(os.path.dirname(__file__), 'encrypted_frames')
    encrypt_all_frames(input_dir, output_dir, key)
