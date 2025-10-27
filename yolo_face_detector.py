"""
YOLO-Face 얼굴 감지 모듈
HOG 대신 YOLOv8/v5-face를 사용하여 더 빠르고 정확한 얼굴 감지
(ultralytics 라이브러리 사용)
"""
import torch
import cv2
import numpy as np
from pathlib import Path

# 🔔 ultralytics 라이브러리가 YOLOv8과 v5를 모두 처리
try:
    from ultralytics import YOLO
except ImportError:
    print("[ERROR] 'ultralytics' 라이브러리가 필요합니다. 'pip install ultralytics'로 설치하세요.")
    raise

class YOLOFaceDetector:
    """YOLOv8/v5-face 기반 얼굴 감지기 (ultralytics 사용)"""
    
    def __init__(self, model_path=None, device='auto', conf_threshold=0.3):
        """
        YOLO-Face 초기화
        
        Args:
            model_path: YOLO-Face 모델 경로 (None이면 자동 검색)
            device: 'auto', 'cpu', 'cuda', 'cuda:0' 등
            conf_threshold: 감지 신뢰도 임계값 (0.0-1.0)
        """
        self.conf_threshold = conf_threshold
        
        # 디바이스 설정
        if device == 'auto':
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        else:
            self.device = device
        
        print(f"[INFO] YOLO-Face 초기화: 디바이스={self.device}, 신뢰도={conf_threshold}")
        
        # 모델 경로 자동 검색
        if model_path is None:
            model_path = self._find_model()
        
        if model_path is None or not Path(model_path).exists():
            print("[WARN] YOLO-Face 모델을 찾을 수 없습니다")
            print("[INFO] 다운로드: https://github.com/deepcam-cn/yolov5-face/releases")
            print("[INFO] yolov5n-face.pt를 models/ 폴더에 저장하세요")
            raise FileNotFoundError("YOLO-Face 모델이 필요합니다. models/README.md를 참조하세요")
        
        # 🔔 수정: ultralytics YOLO로 모델 로드 (v5, v8 모두 호환)
        try:
            print(f"[INFO] YOLO-Face 모델 로드 중: {model_path}")
            self.model = YOLO(model_path)
            self.model.to(self.device)
            print(f"[INFO] ✅ YOLO-Face 모델 로드 완료 ({model_path.split('/')[-1]})")
        except Exception as e:
            raise RuntimeError(f"YOLO-Face 모델 로드 실패: {e}")
    
    def _find_model(self):
        """models/ 폴더에서 YOLO-Face 모델 찾기"""
        model_dir = Path("models")
        if not model_dir.exists():
            return None
        
        # 가능한 모델 파일명 (YOLOv8-Face 우선)
        model_names = [
            'yolov8n-face.pt',  # YOLOv8 nano (가장 빠름)
            'yolov8s-face.pt',  # YOLOv8 small
            'yolov8m-face.pt',  # YOLOv8 medium
            'yolov5n-face.pt',  # YOLOv5 nano (하위 호환)
            'yolov5s-face.pt',  # YOLOv5 small
            'yolov5m-face.pt',  # YOLOv5 medium
        ]
        
        for name in model_names:
            path = model_dir / name
            if path.exists() and path.stat().st_size > 1000000:  # 1MB 이상
                print(f"[INFO] 발견된 모델: {path}")
                return str(path)
        
        return None
    
    def detect_faces(self, image):
        """
        이미지에서 얼굴 감지
        
        Args:
            image: RGB 이미지 (numpy array)
        
        Returns:
            face_locations: 얼굴 위치 리스트 [(top, right, bottom, left), ...]
                           face_recognition 형식과 호환
        """
        # 🔔 수정: upsample_times 인자 및 로직 제거
        # (입력 이미지는 screen_manager에서 이미 스케일링됨)
        h, w = image.shape[:2]
        
        # YOLO 추론 (신뢰도 직접 전달)
        results = self.model(
            image, 
            conf=self.conf_threshold, 
            verbose=False,
            device=self.device
        )
        
        # 결과 파싱 (ultralytics v8 형식)
        boxes = results[0].boxes
        detections = boxes.xyxy.cpu().numpy()  # [x1, y1, x2, y2]
        
        face_locations = []
        for (x1, y1, x2, y2) in detections:
            # 좌표 변환: YOLO (x1, y1, x2, y2) → face_recognition (top, right, bottom, left)
            # 🔔 수정: scale 보정 제거
            top = int(y1)
            right = int(x2)
            bottom = int(y2)
            left = int(x1)
            
            # 이미지 범위 내로 클리핑
            top = max(0, min(top, h))
            bottom = max(0, min(bottom, h))
            left = max(0, min(left, w))
            right = max(0, min(right, w))
            
            face_locations.append((top, right, bottom, left))
        
        return face_locations
    
    def get_device_info(self):
        """현재 사용 중인 디바이스 정보 반환"""
        if self.device == 'cuda' or self.device.startswith('cuda:'):
            return f"GPU: {torch.cuda.get_device_name(0)}"
        return "CPU"
    
    def set_confidence_threshold(self, threshold):
        """신뢰도 임계값 변경"""
        self.conf_threshold = threshold
        # 🔔 수정: 모델의 conf 속성 대신 추론 시 conf 값 전달
        print(f"[INFO] YOLO 신뢰도 임계값 변경: {threshold}")


def download_yolo_face_model():
    """
    YOLOv8-face 모델 다운로드 및 설치
    최초 실행 시 한 번만 실행
    """
    import os
    import urllib.request
    
    model_dir = Path("models")
    model_dir.mkdir(exist_ok=True)
    
    # YOLOv8-face 모델 옵션
    model_options = [
        {
            'name': 'yolov8n-face.pt',  # 가장 작고 빠른 모델 (권장)
            'url': 'https://github.com/derronqi/yolov8-face/releases/download/v0.0.0/yolov8n-face.pt'
        },
        {
            'name': 'yolov8s-face.pt',
            'url': 'https://github.com/derronqi/yolov8-face/releases/download/v0.0.0/yolov8s-face.pt'
        },
        {
            'name': 'yolov8m-face.pt',
            'url': 'https://github.com/derronqi/yolov8-face/releases/download/v0.0.0/yolov8m-face.pt'
        }
    ]
    
    # 이미 다운로드된 모델 확인
    for option in model_options:
        model_path = model_dir / option['name']
        if model_path.exists() and model_path.stat().st_size > 1000000:
            print(f"[INFO] 기존 모델 사용: {model_path}")
            return str(model_path)
    
    # curl로 다운로드 시도
    print("[INFO] YOLOv8-Face 모델 다운로드 중...")
    for option in model_options[:1]:  # 가장 작은 모델만 시도
        model_path = model_dir / option['name']
        url = option['url']
        
        try:
            print(f"[INFO] 다운로드: {url}")
            import subprocess
            result = subprocess.run(
                ['curl', '-L', '-o', str(model_path), url],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0 and model_path.exists() and model_path.stat().st_size > 1000000:
                print(f"[INFO] 다운로드 완료: {model_path} ({model_path.stat().st_size / 1024 / 1024:.1f}MB)")
                return str(model_path)
            else:
                print(f"[WARN] 다운로드 실패")
                if model_path.exists():
                    model_path.unlink()
        except Exception as e:
            print(f"[WARN] 오류: {e}")
            continue
    
    print("[ERROR] 자동 다운로드 실패")
    print("[INFO] 수동 다운로드 방법:")
    print("  1. 브라우저에서 https://github.com/derronqi/yolov8-face/releases 방문")
    print("  2. yolov8n-face.pt (3MB, 권장) 다운로드")
    print(f"  3. models/ 폴더에 저장")
    
    return None


if __name__ == "__main__":
    # 테스트 코드
    print("=== YOLO-Face 테스트 ===")
    
    # 모델 다운로드 (최초 1회)
    model_path = download_yolo_face_model()
    
    # 감지기 초기화
    if model_path:
        detector = YOLOFaceDetector(model_path=model_path)
    else:
        detector = YOLOFaceDetector()
    
    print(f"디바이스: {detector.get_device_info()}")
    
    # 웹캠 테스트
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("[ERROR] 웹캠을 열 수 없습니다")
        exit(1)
    
    print("웹캠 테스트 시작 (ESC로 종료)")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # BGR → RGB 변환
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 얼굴 감지
        # 🔔 수정: upsample_times 인자 제거
        face_locations = detector.detect_faces(rgb_frame)
        
        # 결과 시각화
        for (top, right, bottom, left) in face_locations:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, "Face", (left, top - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # FPS 표시
        cv2.putText(frame, f"Faces: {len(face_locations)}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        cv2.imshow('YOLO-Face Test', frame)
        
        if cv2.waitKey(1) & 0xFF == 27:  # ESC
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("테스트 완료")
