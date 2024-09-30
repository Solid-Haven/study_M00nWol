import os
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import shutil

# AES 복호화에 사용할 키 설정(암호화할 때 사용한 키와 동일해야 함)
key = hashlib.sha256(b'secret_key').digest()

def decrypt_frame(encrypted_data, key):
    # IV를 첫 16바이트에서 추출
    iv = encrypted_data[:AES.block_size]
    encrypted_data = encrypted_data[AES.block_size:]

    # AES CBC 모드로 복호화
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
    return decrypted_data

def decrypt_all_frames(input_dir, output_dir, key):
    # 복호화된 프레임을 저장할 디렉토리 생성
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 암호화된 파일 목록을 숫자 순서로 정렬
    encrypted_files = sorted([f for f in os.listdir(input_dir) if f.endswith('.enc')])
    frame_count = 0

    for encrypted_file in encrypted_files:
        encrypted_path = os.path.join(input_dir, encrypted_file)

        # 암호화된 데이터 읽기
        with open(encrypted_path, 'rb') as f:
            encrypted_data = f.read()

        # 데이터 복호화
        decrypted_data = decrypt_frame(encrypted_data, key)

        # 복호화된 프레임을 다시 PNG로 저장
        frame_path = os.path.join(output_dir, f'decrypted_{frame_count:04d}.png')
        with open(frame_path, 'wb') as f:
            f.write(decrypted_data)

        frame_count += 1
    
    print(f"총 {frame_count}개의 프레임이 복호화되었습니다.")

    # FPS 파일 복사
    fps_file_path = os.path.join(input_dir, 'fps.txt')
    if os.path.exists(fps_file_path):
        output_fps_path = os.path.join(output_dir, 'fps.txt')
        shutil.copy(fps_file_path, output_fps_path)
        print(f"FPS 파일이 '{output_fps_path}'로 복사되었습니다.")
    else:
        print("FPS 파일을 찾을 수 없습니다.")

# 실행
if __name__ == "__main__":
    current_dir = os.getcwd()
    input_dir = os.path.join(current_dir, 'encrypted_frames')
    output_dir = os.path.join(current_dir, 'decrypted_frames')
    decrypt_all_frames(input_dir, output_dir, key)