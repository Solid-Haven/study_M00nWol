import requests

url = "http://localhost:8000/masking/mask_video_frame/"
with open("test_frame.jpg", "rb") as frame_file:
    files = {"frame": frame_file}
    response = requests.post(url, files=files)

    if response.status_code == 200:
        print("Masking and upload successful:", response.json())
    else:
        print("Failed to process frame:", response.status_code)
