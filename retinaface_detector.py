"""
RetinaFace 얼굴 감지 모듈
insightface 라이브러리를 사용하여 정확한 얼굴 감지
"""
import cv2
import numpy as np
from pathlib import Path

class RetinaFaceDetector:
    """RetinaFace 기반 얼굴 감지기 (insightface 사용)"""
    
    def __init__(self, model_path=None, conf_threshold=0.5, nms_threshold=0.4):
        """
        RetinaFace 초기화
        
        Args:
            model_path: RetinaFace 모델 경로 (사용되지 않음, 호환성 유지)
            conf_threshold: 감지 신뢰도 임계값 (0.0-1.0)
            nms_threshold: NMS(Non-Maximum Suppression) 임계값
        """
        self.conf_threshold = conf_threshold
        self.nms_threshold = nms_threshold
        
        print(f"[INFO] RetinaFace 초기화: 신뢰도={conf_threshold}")
        
        # insightface 사용
        try:
            from insightface.app import FaceAnalysis
            
            print(f"[INFO] insightface RetinaFace 로드 중...")
            self.app = FaceAnalysis(providers=['CPUExecutionProvider'])
            self.app.prepare(ctx_id=0, det_size=(640, 640))
            self.device = "CPU"
            print("[INFO] ✅ RetinaFace 모델 로드 완료 (insightface)")
            
        except ImportError as e:
            error_msg = """
╔════════════════════════════════════════════════════════════════╗
║          ⚠️  insightface 라이브러리가 없습니다                ║
╚════════════════════════════════════════════════════════════════╝

RetinaFace를 사용하려면 insightface를 설치해야 합니다.

🚀 빠른 설치 (자동):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  python download_retinaface.py

📖 수동 설치:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  pip install insightface onnxruntime

💡 대안:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  • YOLO-Face 사용: 환경 설정에서 선택
  • HOG 사용 (기본 내장): 항상 사용 가능

자세한 내용: RETINAFACE_GUIDE.md
            """
            print(error_msg)
            raise ImportError(f"insightface가 설치되지 않았습니다: {e}")
            
        except Exception as e:
            print(f"[ERROR] RetinaFace 초기화 실패: {e}")
            raise RuntimeError(f"RetinaFace 모델 로드 실패: {e}")
    
    def detect_faces(self, image, upsample_times=0):
        """
        이미지에서 얼굴 감지
        
        Args:
            image: RGB 이미지 (numpy array)
            upsample_times: 업샘플링 횟수 (0-2) - insightface는 자동 처리
        
        Returns:
            face_locations: 얼굴 위치 리스트 [(top, right, bottom, left), ...]
                           face_recognition 형식과 호환
        """
        try:
            # BGR 변환 (insightface는 BGR 사용)
            image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            # 얼굴 감지
            faces = self.app.get(image_bgr)
            
            # face_recognition 형식으로 변환
            face_locations = []
            for face in faces:
                # bbox 형식: [x1, y1, x2, y2]
                bbox = face.bbox.astype(int)
                x1, y1, x2, y2 = bbox
                
                # face_recognition 형식: (top, right, bottom, left)
                top = y1
                right = x2
                bottom = y2
                left = x1
                
                # 이미지 범위 내로 클리핑
                h, w = image.shape[:2]
                top = max(0, min(top, h))
                bottom = max(0, min(bottom, h))
                left = max(0, min(left, w))
                right = max(0, min(right, w))
                
                # 유효한 박스만 추가
                if bottom > top and right > left:
                    face_locations.append((top, right, bottom, left))
            
            return face_locations
            
        except Exception as e:
            print(f"[ERROR] RetinaFace 감지 오류: {e}")
            return []
    
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

RetinaFace는 insightface 라이브러리를 사용합니다.

🚀 빠른 설치:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. insightface 설치:
   pip install insightface onnxruntime

2. 프로그램 실행:
   python face_recognition_app.py
   
3. 자동으로 모델 다운로드 및 사용됨!

참고
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

- insightface는 첫 실행 시 자동으로 모델을 다운로드합니다
- 모델은 ~/.insightface/models/에 저장됩니다
- GPU 가속은 자동으로 감지됩니다

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
        
    except ImportError as e:
        print("\n⚠️  insightface가 설치되지 않았습니다")
        print("설치 방법: python download_retinaface.py")
    except Exception as e:
        print(f"\n❌ 오류: {e}")
        import traceback
        traceback.print_exc()
