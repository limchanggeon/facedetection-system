# Jetson Nano 문제 해결 가이드

## 목차
1. [GUI가 안 나오는 문제](#gui가-안-나오는-문제)
2. [웹캠 해상도가 낮아지는 문제](#웹캠-해상도가-낮아지는-문제)
3. [화면이 끊기는 문제](#화면이-끊기는-문제)
4. [성능 최적화](#성능-최적화)
5. [자주 묻는 질문](#자주-묻는-질문)

---

## GUI가 안 나오는 문제

### 증상
- 프로그램 실행해도 창이 안 뜸
- `cannot connect to X server` 오류
- GUI 관련 에러 메시지

### 원인
DISPLAY 환경변수가 설정되지 않았거나 X 서버에 접근 권한이 없음

### 해결 방법

#### 방법 1: DISPLAY 환경변수 설정 (권장)
```bash
export DISPLAY=:0
python3 face_recognition_app.py
```

#### 방법 2: 자동 실행 스크립트 사용
```bash
# 최적화 스크립트 실행 (최초 1회)
python3 jetson_optimize.py

# 이후 실행
./run_jetson.sh
```

#### 방법 3: SSH 접속 시
```bash
# X11 포워딩 활성화
ssh -X user@jetson-ip

# 또는 로컬 DISPLAY 사용
export DISPLAY=:0
xhost +local:
python3 face_recognition_app.py
```

#### 방법 4: .bashrc에 추가 (영구 설정)
```bash
echo 'export DISPLAY=:0' >> ~/.bashrc
source ~/.bashrc
```

---

## 웹캠 해상도가 낮아지는 문제

### 증상
- 웹캠 화질이 흐릿함
- 해상도가 320x240으로 고정됨
- 얼굴 인식 거리가 짧음

### 원인
- OpenCV 기본 설정이 낮은 해상도 사용
- USB 대역폭 제한
- 카메라 드라이버 문제

### 해결 방법

#### 방법 1: 카메라 해상도 강제 설정
`gui_screens.py`의 `RecognitionScreen`에서:

```python
def start_recognition(self):
    # 카메라 열기
    camera_index = self.manager.settings['camera_index']
    self.video_capture = cv2.VideoCapture(camera_index)
    
    # 해상도 강제 설정 추가
    self.video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    self.video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    self.video_capture.set(cv2.CAP_PROP_FPS, 30)
    
    # 실제 설정된 해상도 확인
    w = int(self.video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(self.video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"[INFO] 카메라 해상도: {w}x{h}")
```

#### 방법 2: GStreamer 파이프라인 사용 (고급)
```python
# Jetson 최적화 GStreamer 파이프라인
gst_pipeline = (
    f"v4l2src device=/dev/video{camera_index} ! "
    "video/x-raw, width=640, height=480, framerate=30/1 ! "
    "videoconvert ! appsink"
)
self.video_capture = cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)
```

#### 방법 3: 카메라 테스트
```bash
# 카메라 지원 해상도 확인
v4l2-ctl --device=/dev/video0 --list-formats-ext

# 테스트 스크립트 실행
python3 test_camera_jetson.py 0
```

#### 방법 4: USB 대역폭 확인
```bash
# USB 장치 확인
lsusb -t

# USB 3.0 포트 사용 권장
# 파란색 USB 포트 = USB 3.0
# 검은색/흰색 = USB 2.0
```

---

## 화면이 끊기는 문제

### 증상
- FPS가 5-10 이하로 떨어짐
- 화면이 버벅거림
- 프레임 드롭 발생

### 원인
1. Jetson Nano의 제한된 성능 (4GB RAM, 128 CUDA 코어)
2. 높은 해상도 처리
3. 많은 얼굴 동시 처리
4. 전력 모드가 5W로 설정됨

### 해결 방법

#### 1단계: 전력 모드 최대화 (필수!)
```bash
# 10W 최대 성능 모드
sudo nvpmodel -m 0

# 클럭 최대화
sudo jetson_clocks

# 현재 상태 확인
sudo nvpmodel -q
```

#### 2단계: 스왑 메모리 확대
```bash
# 4GB 스왑 파일 생성
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 영구 설정
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# 확인
free -h
```

#### 3단계: 프로그램 설정 최적화

**GUI 설정에서 "고속 모드" 선택:**
- Tolerance: 0.45
- Upsample: 0 (중요!)
- Frame Scale: 0.25 (중요!)

**또는 수동 설정:**
```python
# gui_screens.py의 기본값 수정
self.settings = {
    'camera_index': 0,
    'tolerance': 0.45,
    'distance_threshold': 0.50,
    'upsample_times': 0,      # 0으로 설정!
    'frame_scale': 0.25,       # 0.25로 설정!
    'show_confidence': True
}

# 프레임 처리 간격 늘리기
process_every_n_frames = 3  # 2 → 3으로 변경
```

#### 4단계: YOLO-Face 최적화
```python
# yolov8n-face.pt 사용 (가장 가벼움)
# models/ 폴더에 yolov8n-face.pt 배치

# CUDA 사용 확인
python3 << EOF
import torch
print(f"CUDA 사용 가능: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
EOF
```

#### 5단계: 해상도 및 FPS 제한
```python
# 카메라 설정 최적화
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)   # 640x480 권장
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 15)            # 15-20 FPS 권장
```

---

## 성능 최적화

### Jetson Nano 권장 설정

| 항목 | 권장값 | 설명 |
|------|--------|------|
| 전력 모드 | 10W (Mode 0) | sudo nvpmodel -m 0 |
| 클럭 | 최대 | sudo jetson_clocks |
| 스왑 | 4GB | 메모리 부족 방지 |
| 카메라 해상도 | 640x480 | 480p 권장 |
| 카메라 FPS | 15-20 | 30fps는 과부하 |
| Upsample | 0 | 가장 빠름 |
| Frame Scale | 0.25 | 1/4 크기 처리 |
| 프레임 간격 | 3-5 | 매 3-5 프레임마다 인식 |
| 동시 인원 | 3-5명 | 너무 많으면 느려짐 |
| YOLO 모델 | yolov8n-face | 가장 가벼운 모델 |

### 성능 모니터링

```bash
# GPU/CPU/메모리 실시간 모니터링
sudo tegrastats

# 시스템 리소스
htop

# 온도 확인
cat /sys/devices/virtual/thermal/thermal_zone*/temp
```

### 예상 성능

| 모드 | 예상 FPS | 동시 인원 | 거리 |
|------|----------|----------|------|
| 고속 (권장) | 12-18 | 3-5명 | 1-2m |
| 균형 | 8-12 | 5-7명 | 2-3m |
| CCTV | 5-8 | 7-10명 | 1-5m |

---

## 자주 묻는 질문

### Q1: "CUDA out of memory" 오류
**A:** 
```bash
# 메모리 정리
sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches'

# 스왑 메모리 확대 (위 참조)
# Frame Scale 더 낮추기 (0.25 → 0.2)
```

### Q2: 프로그램이 느려요
**A:**
1. 전력 모드 확인: `sudo nvpmodel -q`
2. 설정에서 "고속 모드" 선택
3. Upsample = 0, Frame Scale = 0.25
4. 프레임 간격 늘리기 (3-5)

### Q3: 카메라가 안 잡혀요
**A:**
```bash
# 카메라 장치 확인
ls -l /dev/video*

# 권한 확인
sudo usermod -a -G video $USER

# 재부팅
sudo reboot
```

### Q4: X11 forwarding이 느려요
**A:**
```bash
# 로컬 DISPLAY 사용 (더 빠름)
export DISPLAY=:0

# SSH X11은 느리므로 VNC 권장
# VNC 서버 설치:
sudo apt-get install x11vnc
x11vnc -display :0
```

### Q5: YOLO가 HOG보다 느려요
**A:**
- PyTorch가 CUDA를 사용하는지 확인
- JetPack 버전 확인 (4.6 이상 권장)
- TensorRT로 변환 고려 (고급)

### Q6: 온도가 너무 높아요
**A:**
```bash
# 온도 확인
cat /sys/devices/virtual/thermal/thermal_zone*/temp

# 팬 속도 확인 (Jetson Nano 2GB/4GB)
# 방열판 설치 권장
# USB 팬 추가 권장
```

---

## 추가 리소스

- [NVIDIA Jetson Nano 개발자 가이드](https://developer.nvidia.com/embedded/learn/get-started-jetson-nano-devkit)
- [Jetson Zoo (최적화된 라이브러리)](https://elinux.org/Jetson_Zoo)
- [프로젝트 GitHub](https://github.com/limchanggeon/facedetection-system)

---

**작성일**: 2024년 10월 27일  
**버전**: v2.2 (Jetson Nano 최적화)
