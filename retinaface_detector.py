"""
RetinaFace 얼굴 감지 모듈
YOLO-Face 대신 RetinaFace를 사용하여 더 정확한 얼굴 감지
"""
import cv2
import numpy as np
from pathlib import Path

class RetinaFaceDetector:
    """RetinaFace 기반 얼굴 감지기"""
    
    def __init__(self, model_path=None, conf_threshold=0.5, nms_threshold=0.4):
        """
        RetinaFace 초기화
        
        Args:
            model_path: RetinaFace 모델 경로 (None이면 자동 검색)
            conf_threshold: 감지 신뢰도 임계값 (0.0-1.0)
            nms_threshold: NMS(Non-Maximum Suppression) 임계값
        """
        self.conf_threshold = conf_threshold
        self.nms_threshold = nms_threshold
        
        print(f"[INFO] RetinaFace 초기화: 신뢰도={conf_threshold}, NMS={nms_threshold}")
        
        # 모델 경로 자동 검색
        if model_path is None:
            model_path = self._find_model()
        
        if model_path is None:
            print("[WARN] RetinaFace 모델을 찾을 수 없습니다")
            print("[INFO] 다운로드: models/README.md 참조")
            raise FileNotFoundError("RetinaFace 모델이 필요합니다")
        
        # 모델 로드 (OpenCV DNN 사용)
        try:
            print(f"[INFO] RetinaFace 모델 로드 중: {model_path}")
            self.model = cv2.dnn.readNetFromONNX(model_path)
            
            # GPU 가속 시도
            try:
                self.model.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
                self.model.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
                self.device = "CUDA"
                print("[INFO] RetinaFace GPU 가속 활성화")
            except:
                self.model.setPreferableBackend(cv2.dnn.DNN_BACKEND_DEFAULT)
                self.model.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
                self.device = "CPU"
                print("[INFO] RetinaFace CPU 모드 사용")
            
            print("[INFO] RetinaFace 모델 로드 완료")
        except Exception as e:
            raise RuntimeError(f"RetinaFace 모델 로드 실패: {e}")
    
    def _find_model(self):
        """models/ 폴더에서 RetinaFace 모델 찾기"""
        model_dir = Path("models")
        if not model_dir.exists():
            return None
        
        # 가능한 모델 파일명
        model_names = [
            'retinaface_resnet50.onnx',
            'retinaface_mobilenet.onnx',
            'retinaface.onnx',
        ]
        
        for name in model_names:
            path = model_dir / name
            if path.exists() and path.stat().st_size > 1000000:  # 1MB 이상
                print(f"[INFO] 발견된 모델: {path}")
                return str(path)
        
        return None
    
    def detect_faces(self, image, upsample_times=0):
        """
        이미지에서 얼굴 감지
        
        Args:
            image: RGB 이미지 (numpy array)
            upsample_times: 업샘플링 횟수 (0-2)
                0: 원본 크기
                1: 2배 확대
                2: 4배 확대
        
        Returns:
            face_locations: 얼굴 위치 리스트 [(top, right, bottom, left), ...]
                           face_recognition 형식과 호환
        """
        h, w = image.shape[:2]
        
        # 업샘플링 적용
        if upsample_times > 0:
            scale = 2 ** upsample_times
            image_upsampled = cv2.resize(image, (w * scale, h * scale))
        else:
            image_upsampled = image
            scale = 1
        
        # BGR 변환 (OpenCV DNN은 BGR 사용)
        image_bgr = cv2.cvtColor(image_upsampled, cv2.COLOR_RGB2BGR)
        
        # 입력 크기 조정 (RetinaFace는 640x640 권장)
        target_size = 640
        h_scaled, w_scaled = image_bgr.shape[:2]
        
        # 비율 유지하며 리사이즈
        if max(h_scaled, w_scaled) > target_size:
            if h_scaled > w_scaled:
                new_h = target_size
                new_w = int(w_scaled * target_size / h_scaled)
            else:
                new_w = target_size
                new_h = int(h_scaled * target_size / w_scaled)
            
            image_resized = cv2.resize(image_bgr, (new_w, new_h))
            resize_scale_x = w_scaled / new_w
            resize_scale_y = h_scaled / new_h
        else:
            image_resized = image_bgr
            resize_scale_x = 1.0
            resize_scale_y = 1.0
        
        # 입력 blob 생성
        blob = cv2.dnn.blobFromImage(
            image_resized,
            scalefactor=1.0,
            size=(image_resized.shape[1], image_resized.shape[0]),
            mean=(104.0, 117.0, 123.0),
            swapRB=False,
            crop=False
        )
        
        # 추론
        self.model.setInput(blob)
        outputs = self.model.forward()
        
        # 결과 파싱
        face_locations = []
        
        if len(outputs.shape) == 3:
            detections = outputs[0]
        else:
            detections = outputs
        
        for detection in detections:
            confidence = detection[2]
            
            if confidence > self.conf_threshold:
                # 좌표 추출 (정규화된 좌표)
                x1 = int(detection[3] * image_resized.shape[1] * resize_scale_x)
                y1 = int(detection[4] * image_resized.shape[0] * resize_scale_y)
                x2 = int(detection[5] * image_resized.shape[1] * resize_scale_x)
                y2 = int(detection[6] * image_resized.shape[0] * resize_scale_y)
                
                # 업샘플링 보정
                top = int(y1 / scale)
                right = int(x2 / scale)
                bottom = int(y2 / scale)
                left = int(x1 / scale)
                
                # 이미지 범위 내로 클리핑
                top = max(0, min(top, h))
                bottom = max(0, min(bottom, h))
                left = max(0, min(left, w))
                right = max(0, min(right, w))
                
                # 유효한 박스만 추가
                if bottom > top and right > left:
                    face_locations.append((top, right, bottom, left))
        
        return face_locations
    
    def get_device_info(self):
        """현재 사용 중인 디바이스 정보 반환"""
        return f"{self.device}"
    
    def set_confidence_threshold(self, threshold):
        """신뢰도 임계값 변경"""
        self.conf_threshold = threshold
        print(f"[INFO] RetinaFace 신뢰도 임계값 변경: {threshold}")


def download_retinaface_model():
    """
    RetinaFace 모델 다운로드 가이드
    """
    import os
    
    model_dir = Path("models")
    model_dir.mkdir(exist_ok=True)
    
    print("""
╔════════════════════════════════════════════════════════════════╗
║               RetinaFace 모델 다운로드 가이드                  ║
╚════════════════════════════════════════════════════════════════╝

RetinaFace ONNX 모델을 다운로드하세요:

방법 1: 직접 변환 (권장)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Insightface RetinaFace 설치:
   pip install insightface onnxruntime

2. Python 스크립트로 모델 다운로드:
   
   import insightface
   from insightface.app import FaceAnalysis
   
   app = FaceAnalysis(providers=['CPUExecutionProvider'])
   app.prepare(ctx_id=0, det_size=(640, 640))
   
   # 모델이 자동으로 ~/.insightface/models/에 다운로드됨
   # buffalo_l/det_10g.onnx 를 models/retinaface.onnx로 복사

3. 모델 파일 복사:
   cp ~/.insightface/models/buffalo_l/det_10g.onnx models/retinaface.onnx

방법 2: 사전 학습 모델 다운로드
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. GitHub에서 다운로드:
   https://github.com/deepinsight/insightface/tree/master/model_zoo

2. RetinaFace-R50 또는 RetinaFace-MobileNet 선택

3. ONNX 모델을 models/ 폴더에 저장:
   - retinaface_resnet50.onnx (정확도 높음, 느림)
   - retinaface_mobilenet.onnx (빠름, 정확도 중간)

방법 3: 간단한 다운로드 스크립트
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

아래 스크립트 실행:

python3 << 'PYEOF'
import urllib.request
import os

model_dir = "models"
os.makedirs(model_dir, exist_ok=True)

# Insightface Buffalo 모델 (추천)
url = "https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_l.zip"
print(f"다운로드 중: {url}")

# 또는 직접 ONNX 파일 URL 사용
# url = "직접 ONNX 파일 URL"

print("수동으로 다운로드하세요:")
print(f"1. {url} 방문")
print(f"2. det_10g.onnx를 {model_dir}/retinaface.onnx로 저장")
PYEOF

참고
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

- RetinaFace는 YOLOv8보다 작은 얼굴 감지에 유리
- GPU 가속 권장 (CUDA 또는 OpenCV with CUDA)
- 모델 크기: 약 10-100MB

    """)
    
    return None


if __name__ == "__main__":
    # 테스트 코드
    print("=== RetinaFace 테스트 ===")
    
    try:
        # RetinaFaceDetector 초기화
        detector = RetinaFaceDetector(conf_threshold=0.5)
        
        print(f"\n디바이스: {detector.get_device_info()}")
        
        # 더미 이미지 테스트
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        face_locations = detector.detect_faces(test_image, upsample_times=0)
        
        print(f"✅ 감지된 얼굴: {len(face_locations)}개")
        print("✅ RetinaFace가 정상적으로 작동합니다!")
        
    except FileNotFoundError:
        print("\n⚠️  RetinaFace 모델이 없습니다")
        download_retinaface_model()
    except Exception as e:
        print(f"\n❌ 오류: {e}")
        import traceback
        traceback.print_exc()
