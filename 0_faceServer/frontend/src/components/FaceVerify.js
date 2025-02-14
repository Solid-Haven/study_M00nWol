import React, { useState } from "react";

const FaceVerify = () => {
    const [selectedFile, setSelectedFile] = useState(null);
    const [userId, setUserId] = useState("");
    const [message, setMessage] = useState("");

    // 파일 선택 핸들러
    const handleFileChange = (event) => {
        setSelectedFile(event.target.files[0]);
    };

    // 얼굴 인증 요청
    const handleFaceVerify = async () => {
        if (!selectedFile || !userId.trim()) {
            alert("사용자 ID와 사진을 입력해주세요.");
            return;
        }

        const formData = new FormData();
        formData.append("face_image", selectedFile);
        formData.append("user_id", userId.trim());  // 사용자 ID 추가

        try {
            const response = await fetch(`${process.env.REACT_APP_API_BASE_URL}/face-verify/`, {
                method: "POST",
                body: formData,
            });

            const data = await response.json();

            if (response.ok) {
                setMessage(`✅ 결과: ${data.message} (유사도: ${data.similarity.toFixed(3)})`);
            } else {
                setMessage(`❌ 오류: ${data.message}`);
            }
        } catch (error) {
            console.error("API 호출 오류:", error);
            setMessage("서버와 연결할 수 없습니다.");
        }
    };

    return (
        <div>
            <h1>얼굴 인증</h1>
            <input 
                type="text" 
                placeholder="사용자 ID 입력" 
                value={userId} 
                onChange={(e) => setUserId(e.target.value)} 
            />
            <input type="file" accept="image/*" onChange={handleFileChange} />
            <button onClick={handleFaceVerify}>얼굴 인증</button>
            {message && <p>{message}</p>}
        </div>
    );
};

export default FaceVerify;
