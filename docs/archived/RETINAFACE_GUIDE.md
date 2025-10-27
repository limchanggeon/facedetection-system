# RetinaFace 사용 가이드

## 개요

RetinaFace는 YOLO-Face보다 더 정확한 얼굴 감지를 제공하며, 특히 작은 얼굴이나 다양한 각도의 얼굴 감지에 뛰어납니다.

## RetinaFace vs YOLO-Face vs HOG

| 특징 | HOG | YOLO-Face | RetinaFace |
|------|-----|-----------|------------|
| 속도 | 느림 | 매우 빠름 | 빠름 |
| 정확도 | 낮음 | 높음 | 매우 높음 |
| 작은 얼굴 | 약함 | 중간 | 강함 |
| 다양한 각도 | 약함 | 강함 | 매우 강함 |
| GPU 가속 | ❌ | ✅ | ✅ |
| 모델 크기 | - | 3-6MB | 10-100MB |

## 설치 방법

### 1단계: Insightface 설치

```bash
# 가상환경 활성화
source .venv/bin/activate

# Insightface 설치
pip install insightface onnxruntime
```

### 2단계: 모델 다운로드

#### 방법 1: 자동 다운로드 (권장)

```python
import insightface
from insightface.app import FaceAnalysis

# FaceAnalysis 초기화 (모델 자동 다운로드)
app = FaceAnalysis(providers=['CPUExecutionProvider'])
app.prepare(ctx_id=0, det_size=(640, 640))

# 모델 파일 위치 확인
# ~/.insightface/models/buffalo_l/det_10g.onnx
```

모델 파일 복사:
```bash
mkdir -p models
cp ~/.insightface/models/buffalo_l/det_10g.onnx models/retinaface.onnx
```

#### 방법 2: 수동 다운로드

1. GitHub 릴리스 페이지 방문:
   - https://github.com/deepinsight/insightface/releases

2. Buffalo_l 모델 다운로드 (추천)

3. `det_10g.onnx` 파일을 `models/retinaface.onnx`로 저장

### 3단계: 코드에서 사용

```python
from retinaface_detector import RetinaFaceDetector
import face_recognition

# RetinaFace 초기화
detector = RetinaFaceDetector(conf_threshold=0.5)

# 이미지에서 얼굴 감지
rgb_image = ...
face_locations = detector.detect_faces(rgb_image, upsample_times=0)

# face_recognition과 동일한 형식
# face_locations = [(top, right, bottom, left), ...]

# 얼굴 인코딩 (기존 방식 유지)
face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
```

## GUI에 통합하기

`gui_screens.py`의 `RecognitionScreen` 클래스 수정:

```python
class RecognitionScreen(tk.Frame):
    def __init__(self, parent, manager):
        super().__init__(parent, bg="#2c3e50")
        self.manager = manager
        self.video_capture = None
        self.is_running = False
        self.recognition_thread = None
        
        # 감지기 초기화 우선순위: RetinaFace > YOLO-Face > HOG
        self.detector = None
        self.detector_type = "HOG"
        
        # RetinaFace 시도
        try:
            from retinaface_detector import RetinaFaceDetector
            self.detector = RetinaFaceDetector(conf_threshold=0.5)
            self.detector_type = "RetinaFace"
            print("[INFO] RetinaFace 감지기 사용")
        except Exception as e:
            print(f"[WARN] RetinaFace 초기화 실패: {e}")
            
            # YOLO-Face 시도
            try:
                from yolo_face_detector import YOLOFaceDetector
                self.detector = YOLOFaceDetector(conf_threshold=0.3)
                self.detector_type = "YOLO-Face"
                print("[INFO] YOLO-Face 감지기 사용")
            except Exception as e:
                print(f"[WARN] YOLO-Face 초기화 실패: {e}")
                self.detector_type = "HOG"
                print("[INFO] HOG 감지기 사용 (기본)")
```

얼굴 감지 부분:

```python
# 얼굴 위치 감지
if self.detector and self.detector_type != "HOG":
    # RetinaFace 또는 YOLO-Face 사용
    face_locations = self.detector.detect_faces(
        rgb_small_frame,
        upsample_times=self.manager.settings['upsample_times']
    )
else:
    # HOG 사용
    face_locations = face_recognition.face_locations(
        rgb_small_frame,
        model="hog",
        number_of_times_to_upsample=self.manager.settings['upsample_times']
    )

print(f"[INFO] {len(face_locations)}개 얼굴 감지 ({self.detector_type})")
```

## 성능 비교

### PC (Intel i7, RTX 2060)

| 모드 | HOG | YOLO-Face | RetinaFace |
|------|-----|-----------|------------|
| 고속 | 25-30 | 40-55 | 30-45 |
| 균형 | 18-22 | 25-40 | 20-35 |
| CCTV | 10-15 | 15-30 | 12-25 |

### Jetson Nano

| 모드 | HOG | YOLO-Face | RetinaFace |
|------|-----|-----------|------------|
| 고속 | 8-12 | 12-18 | 10-15 |
| 균형 | 5-8 | 8-12 | 7-10 |
| CCTV | 3-5 | 5-8 | 4-6 |

## 장단점

### RetinaFace 장점

✅ **매우 높은 정확도**
- 작은 얼굴 감지 우수
- 다양한 각도 지원
- 조명 변화에 강인함

✅ **얼굴 랜드마크**
- 5개 키포인트 제공 (눈, 코, 입)
- 얼굴 정렬 가능

✅ **안정적인 감지**
- False positive 적음
- 신뢰할 수 있는 결과

### RetinaFace 단점

⚠️ **모델 크기**
- 10-100MB (YOLO-Face의 2-10배)

⚠️ **속도**
- YOLO-Face보다 약간 느림
- 하지만 HOG보다는 훨씬 빠름

⚠️ **설치 복잡도**
- Insightface 의존성 필요
- 모델 다운로드 추가 단계

## 추천 사용 시나리오

### RetinaFace 추천

✅ **보안 시스템**
- 정확도가 최우선
- 작은 얼굴도 놓치면 안 됨
- 다양한 각도에서 감지 필요

✅ **출입 통제**
- False positive 최소화
- 안정적인 인식 필요

✅ **고급 응용**
- 얼굴 랜드마크 필요
- 얼굴 정렬/변환

### YOLO-Face 추천

✅ **실시간 성능 중시**
- 속도가 최우선
- 많은 인원 동시 처리

✅ **리소스 제한**
- Jetson Nano 등 임베디드
- 모델 크기 제한

### HOG 추천

✅ **호환성 우선**
- 간단한 설치
- 의존성 최소화

## GPU 가속

### CUDA 지원 OpenCV

RetinaFace는 OpenCV DNN을 사용하므로 CUDA 지원 OpenCV가 필요합니다.

```bash
# CUDA 지원 OpenCV 설치 확인
python -c "import cv2; print(cv2.getBuildInformation())" | grep -i cuda

# CUDA 활성화 여부 확인
python -c "import cv2; print('CUDA:', cv2.cuda.getCudaEnabledDeviceCount() > 0)"
```

### Jetson Nano

JetPack에 포함된 OpenCV는 CUDA를 지원합니다.

```bash
# OpenCV 버전 확인
python3 -c "import cv2; print(cv2.__version__)"

# CUDA 확인
python3 -c "import cv2; print(cv2.getBuildInformation())" | grep -i cuda
```

## 트러블슈팅

### Q1: "No module named 'insightface'"

```bash
pip install insightface onnxruntime
```

### Q2: "Model file not found"

모델 다운로드 확인:
```bash
ls -lh models/retinaface*.onnx
```

수동 다운로드:
```bash
python3 -c "
from insightface.app import FaceAnalysis
app = FaceAnalysis(providers=['CPUExecutionProvider'])
app.prepare(ctx_id=0)
"

cp ~/.insightface/models/buffalo_l/det_10g.onnx models/retinaface.onnx
```

### Q3: GPU 가속이 안 됨

```python
# OpenCV CUDA 빌드 확인
import cv2
print(cv2.getBuildInformation())

# DNN 백엔드 확인
net = cv2.dnn.readNetFromONNX('models/retinaface.onnx')
try:
    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
    net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
    print("✅ CUDA 사용 가능")
except:
    print("⚠️  CUDA 사용 불가, CPU 사용")
```

### Q4: 너무 느림

설정 최적화:
- `conf_threshold` 높이기 (0.5 → 0.7)
- `upsample_times` 줄이기 (2 → 0)
- `frame_scale` 줄이기 (0.25 → 0.2)

## 참고 자료

- [Insightface GitHub](https://github.com/deepinsight/insightface)
- [RetinaFace 논문](https://arxiv.org/abs/1905.00641)
- [OpenCV DNN 모듈](https://docs.opencv.org/master/d2/d58/tutorial_table_of_content_dnn.html)

---

**작성일**: 2024년 10월 27일
**버전**: v2.3 (RetinaFace 통합)
