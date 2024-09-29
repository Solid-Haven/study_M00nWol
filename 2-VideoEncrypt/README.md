## STEP 2 
- 영상 암복호화하기

### HOW
- 영상 프레임 단위로 저장 : save_frames
- 프레임 암호화 : encrypt_frames
- 프레임 복호화 : decrypt_frames
- 복호화된 프레임으로 영상 재빌딩 : rebuild_video

### 주의
- FPS라는 프레임 속도(?)를 모든 파일이 공유해야함
- 프레임 저장시 순서대로 되도록 유의
- 이 두 개 안 지키면 뒤죽박죽, 빠르거나 느린 영상으로 재빌딩됨