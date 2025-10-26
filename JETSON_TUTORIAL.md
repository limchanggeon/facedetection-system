# 🚀 Jetson 환경에서 실행하기

이 가이드는 NVIDIA Jetson (Nano, Xavier NX, AGX Orin 등)에서 얼굴 인식 시스템을 설치하고 실행하는 방법을 설명합니다.

## 📋 목차
1. [시스템 요구사항](#시스템-요구사항)
2. [설치 과정](#설치-과정)
3. [실행 방법](#실행-방법)
4. [성능 최적화](#성능-최적화)
5. [문제 해결](#문제-해결)

---

## 📌 시스템 요구사항

### 하드웨어
- **Jetson 모델**: Nano, Xavier NX, AGX Orin 등
- **카메라**: USB 웹캠 또는 CSI 카메라
- **메모리**: 최소 4GB RAM (8GB 권장)
- **저장공간**: 최소 5GB 여유 공간

### 소프트웨어
- **JetPack**: 4.6 이상 (Ubuntu 18.04/20.04 base)
- **Python**: 3.6 이상
- **CUDA**: JetPack에 포함됨

---

## 🔧 설치 과정

### 1. 시스템 업데이트

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### 2. 필수 패키지 설치

```bash
# 시스템 패키지
sudo apt-get install -y \
    python3-pip \
    python3-dev \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libgtk-3-dev \
    libatlas-base-dev \
    gfortran

# pip 업그레이드
python3 -m pip install --upgrade pip
```

### 3. 프로젝트 클론

```bash
cd ~
git clone https://github.com/limchanggeon/facedetection-system.git
cd facedetection-system
```

### 4. 가상 환경 생성 (선택사항이지만 권장)

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 5. Python 패키지 설치

#### Option A: 일반 설치 (CPU 기반)

```bash
pip install -r requirements.txt
```

#### Option B: CUDA 가속 설치 (권장)

dlib을 CUDA 지원으로 컴파일:

```bash
# dlib 소스 다운로드
git clone https://github.com/davisking/dlib.git
cd dlib

# CUDA 지원 빌드
mkdir build
cd build
cmake .. -DDLIB_USE_CUDA=1 -DUSE_AVX_INSTRUCTIONS=1
cmake --build . --config Release
cd ..

# dlib 설치
python setup.py install

# 나머지 패키지 설치
cd ..
pip install face_recognition opencv-python Pillow
```

### 6. 한글 폰트 확인

```bash
# 한글 폰트 설치 (Ubuntu 18.04/20.04)
sudo apt-get install -y fonts-nanum fonts-nanum-coding

# 폰트 캐시 업데이트
fc-cache -fv
```

---

## 🎮 실행 방법

### 기본 실행

```bash
# 가상환경 활성화 (사용 시)
source .venv/bin/activate

# 프로그램 실행
python3 face_recognition_gui.py
```

### GUI 없이 실행 (SSH 접속 시)

X11 포워딩 설정:

```bash
# 로컬에서 Jetson에 SSH 연결
ssh -X user@jetson-ip-address

# 프로그램 실행
python3 face_recognition_gui.py
```

### 자동 시작 설정

시스템 부팅 시 자동 실행:

```bash
# 실행 스크립트 생성
nano ~/start_face_recognition.sh
```

다음 내용 입력:

```bash
#!/bin/bash
cd ~/facedetection-system
source .venv/bin/activate
python3 face_recognition_gui.py
```

실행 권한 부여:

```bash
chmod +x ~/start_face_recognition.sh
```

자동 시작 설정 (crontab):

```bash
crontab -e
```

다음 라인 추가:

```
@reboot sleep 30 && ~/start_face_recognition.sh
```

---

## ⚡ 성능 최적화

### 1. Jetson 성능 모드 설정

```bash
# 최대 성능 모드
sudo nvpmodel -m 0
sudo jetson_clocks
```

### 2. 카메라 최적화

**CSI 카메라 사용 시** (더 빠름):

`face_recognition_gui.py`의 `start_recognition` 함수 수정:

```python
# 기존
self.video_capture = cv2.VideoCapture(0)

# CSI 카메라용
gstreamer_pipeline = (
    "nvarguscamerasrc ! "
    "video/x-raw(memory:NVMM), width=1280, height=720, format=NV12, framerate=30/1 ! "
    "nvvidconv flip-method=0 ! "
    "video/x-raw, width=1280, height=720, format=BGRx ! "
    "videoconvert ! "
    "video/x-raw, format=BGR ! appsink"
)
self.video_capture = cv2.VideoCapture(gstreamer_pipeline, cv2.CAP_GSTREAMER)
```

### 3. 처리 프레임 간격 조정

`face_recognition_gui.py`에서:

```python
# 더 높은 성능을 위해 프레임 간격 증가
process_every_n_frames = 5  # 기본값 3에서 5로 증가
```

### 4. 해상도 조정

낮은 해상도로 처리 속도 향상:

```python
# 얼굴 인식 처리 시
small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
# fx, fy를 0.2로 줄여서 더 빠르게 처리 가능
```

---

## 🔍 카메라 장치 확인

### USB 카메라 확인

```bash
# 연결된 카메라 목록
ls -l /dev/video*

# 카메라 정보 확인
v4l2-ctl --list-devices
```

### 카메라 테스트

```bash
# 간단한 테스트
python3 -c "import cv2; cap = cv2.VideoCapture(0); print('카메라 상태:', cap.isOpened()); cap.release()"
```

---

## 🐛 문제 해결

### 1. 메모리 부족 오류

**증상**: "Out of memory" 오류

**해결책**:

```bash
# 스왑 메모리 증가 (Jetson Nano)
sudo systemctl disable nvzramconfig
sudo fallocate -l 4G /mnt/4GB.swap
sudo chmod 600 /mnt/4GB.swap
sudo mkswap /mnt/4GB.swap
sudo swapon /mnt/4GB.swap

# /etc/fstab에 추가하여 영구 적용
echo "/mnt/4GB.swap swap swap defaults 0 0" | sudo tee -a /etc/fstab
```

### 2. GUI 표시 안됨

**증상**: GUI 창이 열리지 않음

**해결책**:

```bash
# DISPLAY 환경 변수 설정
export DISPLAY=:0

# 또는 xhost 권한 설정
xhost +local:
```

### 3. 카메라 접근 권한 오류

**증상**: "Permission denied" 오류

**해결책**:

```bash
# 사용자를 video 그룹에 추가
sudo usermod -a -G video $USER

# 로그아웃 후 다시 로그인
```

### 4. dlib 설치 실패

**증상**: dlib 컴파일 오류

**해결책**:

```bash
# 메모리 부족 시 스왑 메모리 증가 (위 참조)
# 컴파일 시 단일 스레드 사용
cd dlib/build
cmake --build . --config Release -- -j1
```

### 5. 느린 얼굴 인식

**해결책**:

1. **프레임 간격 증가** (위 최적화 섹션 참조)
2. **해상도 감소**
3. **HOG 모델 사용** (기본값, CNN보다 빠름)
4. **CUDA 지원 dlib 사용**

---

## 📊 성능 벤치마크

### Jetson Nano (4GB)
- **FPS**: 10-15 (HOG 모델)
- **FPS**: 3-5 (CNN 모델)
- **해상도**: 1056x594

### Jetson Xavier NX
- **FPS**: 20-25 (HOG 모델)
- **FPS**: 10-15 (CNN 모델)
- **해상도**: 1056x594

### Jetson AGX Orin
- **FPS**: 30+ (HOG 모델)
- **FPS**: 20-25 (CNN 모델)
- **해상도**: 1920x1080 가능

---

## 💡 추가 팁

### 1. 원격 접속 시 VNC 사용

```bash
# VNC 서버 설치
sudo apt-get install -y vino

# VNC 설정
gsettings set org.gnome.Vino require-encryption false
```

### 2. 시스템 모니터링

```bash
# Jetson 상태 확인
sudo tegrastats

# 실시간 모니터링
watch -n 1 tegrastats
```

### 3. 로그 확인

```bash
# 실행 로그 저장
python3 face_recognition_gui.py 2>&1 | tee face_recognition.log
```

---

## 📚 추가 자료

- [NVIDIA Jetson 공식 문서](https://developer.nvidia.com/embedded/learn/get-started-jetson-nano-devkit)
- [JetPack SDK](https://developer.nvidia.com/embedded/jetpack)
- [face_recognition 라이브러리](https://github.com/ageitgey/face_recognition)
- [OpenCV 최적화 가이드](https://docs.opencv.org/master/d5/dc4/tutorial_video_input_psnr_ssim.html)

---

## 🆘 지원

문제가 발생하면:
1. [Issues](https://github.com/limchanggeon/facedetection-system/issues)에 보고
2. 로그 파일 첨부
3. Jetson 모델 및 JetPack 버전 명시

---

## 📝 라이센스

MIT License - 자세한 내용은 [LICENSE](LICENSE) 파일 참조
