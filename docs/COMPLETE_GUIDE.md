# 🎯 얼굴 인식 시스템 완벽 가이드

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey.svg)](https://github.com/limchanggeon/facedetection-system)

**버전**: v2.3.3 (2024년 10월 27일)  
**GitHub**: https://github.com/limchanggeon/facedetection-system

---

## 📑 목차

1. [시작하기](#1-시작하기)
2. [설치 가이드](#2-설치-가이드)
3. [사용 방법](#3-사용-방법)
4. [얼굴 감지 엔진](#4-얼굴-감지-엔진)
5. [정확도 최적화](#5-정확도-최적화)
6. [플랫폼별 가이드](#6-플랫폼별-가이드)
7. [문제 해결](#7-문제-해결)
8. [고급 기능](#8-고급-기능)
9. [개발자 정보](#9-개발자-정보)

---

## 1. 시작하기

### 1.1 개요

SQLite 데이터베이스와 GUI를 갖춘 실시간 얼굴 인식 시스템입니다. 다양한 플랫폼(Windows, macOS, Linux, Jetson Nano)에서 작동하며, 3가지 얼굴 감지 엔진(RetinaFace, YOLO-Face, HOG)을 지원합니다.

### 1.2 주요 기능

- 🎥 **실시간 멀티 얼굴 인식**: 최대 10명 동시 인식
- 👥 **CCTV 스타일 탐지**: 원거리/근거리 얼굴 동시 탐지
- 🏆 **3가지 감지 엔진**: RetinaFace(정확도) / YOLO-Face(속도) / HOG(기본)
- 👤 **얼굴 등록 시스템**: GUI를 통한 간편한 등록
- 💾 **SQLite 데이터베이스**: 영구 저장 및 로그 관리
- 🎨 **직관적인 멀티스크린 GUI**: Tkinter 기반
- 🇰🇷 **완벽한 한글 지원**: 한글 이름 표시
- ⚙️ **실시간 설정 조절**: GUI에서 정확도/속도 조절
- 🚀 **Jetson 최적화**: NVIDIA Jetson 플랫폼 지원

### 1.3 시스템 요구사항

#### 기본 요구사항
- **Python**: 3.6 이상
- **카메라**: 웹캠 또는 CSI 카메라
- **OS**: Linux, macOS, Windows

#### 하드웨어 권장사양
- **CPU**: Intel i5 이상 또는 ARM (Jetson)
- **RAM**: 4GB 이상 (8GB 권장)
- **저장공간**: 1GB 이상

---

## 2. 설치 가이드

### 2.1 기본 설치 (모든 플랫폼)

#### Step 1: 저장소 클론

```bash
git clone https://github.com/limchanggeon/facedetection-system.git
cd facedetection-system
```

#### Step 2: 가상 환경 생성

```bash
# Linux/macOS
python3 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

#### Step 3: 패키지 설치

```bash
pip install -r requirements.txt
```

#### Step 4: 프로그램 실행

```bash
# 멀티 스크린 버전 (권장)
python face_recognition_app.py

# 단일 화면 버전
python face_recognition_gui.py
```

### 2.2 Windows 특별 설치

#### dlib 설치 문제 해결

**방법 1: Visual Studio Build Tools 설치**

1. [Visual Studio Build Tools](https://visualstudio.microsoft.com/downloads/) 다운로드
2. "C++를 사용한 데스크톱 개발" 선택
3. 설치 후 재부팅
4. `pip install dlib` 재시도

**방법 2: 사전 컴파일된 wheel 사용**

```bash
# Python 버전 확인
python --version

# 적절한 wheel 다운로드 (예: Python 3.9, 64bit)
# https://github.com/z-mahmud22/Dlib_Windows_Python3.x

# 설치
pip install dlib-19.24.0-cp39-cp39-win_amd64.whl
```

### 2.3 Jetson Nano 설치

#### CUDA 지원 dlib 설치

```bash
# CUDA 설치 확인
nvcc --version

# CMake 설치
sudo apt-get install cmake

# dlib CUDA 지원 빌드
git clone https://github.com/davisking/dlib.git
cd dlib
mkdir build
cd build
cmake .. -DDLIB_USE_CUDA=1 -DUSE_AVX_INSTRUCTIONS=1
cmake --build . --config Release
cd ..
python setup.py install --yes USE_AVX_INSTRUCTIONS --yes DLIB_USE_CUDA
```

#### 성능 최적화

```bash
# 최대 성능 모드 (10W)
sudo nvpmodel -m 0
sudo jetson_clocks

# Jetson 최적화 스크립트 실행
python jetson_optimize.py
```

---

## 3. 사용 방법

### 3.1 멀티 스크린 GUI (v2.0)

#### 화면 구성

```
🏠 로비 화면
├── 얼굴 인식 시작 → 🎥 인식 화면
├── 얼굴 등록 관리 → 👤 등록 화면
├── 데이터베이스 관리 → 💾 데이터베이스 화면
└── 환경 설정 → ⚙️ 설정 화면
```

### 3.2 기본 사용 흐름

#### 1단계: 환경 설정

```
환경 설정 버튼 클릭
├── 카메라 선택 (0: 내장, 1-2: USB)
├── 카메라 테스트
├── 얼굴 감지 엔진 선택
│   ├── 🤖 자동 선택 (권장)
│   ├── 🏆 RetinaFace (최고 정확도)
│   ├── ⚡ YOLO-Face (최고 속도)
│   └── 🔧 HOG (기본)
├── 성능 프리셋 선택
│   ├── ⚡ 고속 모드 (25-30 FPS)
│   ├── ⚖️ 균형 모드 (18-22 FPS)
│   └── 🎥 CCTV 모드 (10-15 FPS)
└── 설정 저장
```

#### 2단계: 얼굴 등록

```
얼굴 등록 관리 버튼 클릭
├── 새 얼굴 등록하기 클릭
├── 이름 입력 (예: "홍길동")
├── 학번 입력 (선택)
├── 학과 입력 (선택)
├── 학년 입력 (선택)
├── 카메라 보고 스페이스바 → 촬영
└── Enter → 저장 완료
```

#### 3단계: 얼굴 인식

```
얼굴 인식 시작 버튼 클릭
├── 시작 버튼 클릭
├── 카메라 화면 표시
├── 얼굴 감지 및 인식
│   ├── 🟢 녹색 박스: 등록된 사람 (이름 + 신뢰도)
│   └── 🔴 빨간 박스: 미등록 (Unknown)
└── 정지 버튼 → 종료
```

#### 4단계: 데이터베이스 관리

```
데이터베이스 관리 버튼 클릭
├── 등록된 얼굴 목록 확인
├── 선택한 얼굴 삭제
├── 인식 로그 보기 (최근 100개)
└── 통계 확인
```

---

## 4. 얼굴 감지 엔진

### 4.1 엔진 비교

| 특징 | RetinaFace 🏆 | YOLO-Face ⚡ | HOG 🔧 |
|------|---------------|--------------|---------|
| **정확도** | ★★★★★ | ★★★★☆ | ★★★☆☆ |
| **속도 (PC)** | ★★★★☆ | ★★★★★ | ★★☆☆☆ |
| **작은 얼굴** | ★★★★★ | ★★★★☆ | ★★☆☆☆ |
| **다양한 각도** | ★★★★★ | ★★★★☆ | ★★☆☆☆ |
| **GPU 가속** | ✅ | ✅ | ❌ |
| **설치 난이도** | 중간 | 중간 | 쉬움 |
| **모델 크기** | 16MB | 6MB | 없음 |

### 4.2 RetinaFace 설치

#### 자동 설치 (권장)

```bash
python download_retinaface.py
```

#### 수동 설치

```bash
# 1. 의존성 설치
pip install insightface onnxruntime

# 2. 프로그램 실행 (자동 다운로드)
python face_recognition_app.py
```

#### 확인

```bash
# 모델 파일 확인
ls -lh ~/.insightface/models/buffalo_l/

# 프로그램 로그 확인
# [INFO] ✅ RetinaFace 감지기 사용
```

### 4.3 YOLO-Face 설치

#### 모델 다운로드

```bash
# models 폴더로 이동
cd models

# YOLOv8-Face 다운로드 (권장)
wget https://github.com/derronqi/yolov8-face/releases/download/v0.0.0/yolov8n-face.pt

# 또는 브라우저에서:
# https://github.com/derronqi/yolov8-face/releases
```

#### 확인

```bash
ls -lh models/yolov8n-face.pt
# -rw-r--r-- 1 user user 6.1M Oct 27 11:46 yolov8n-face.pt
```

### 4.4 엔진 선택 가이드

#### 🏆 RetinaFace 추천 시나리오

```
✅ 보안/출입통제 시스템
✅ 작은 얼굴도 정확히 감지 필요
✅ 다양한 각도에서 촬영
✅ 정확도 최우선
✅ False Positive 최소화

예: 건물 출입구, CCTV 감시, 보안 검색
```

#### ⚡ YOLO-Face 추천 시나리오

```
✅ 실시간 이벤트/회의
✅ 많은 인원 동시 처리
✅ 빠른 속도 필요
✅ GPU 가속 활용
✅ 높은 FPS 요구

예: 컨퍼런스, 실시간 출석체크, 이벤트
```

#### 🔧 HOG 추천 시나리오

```
✅ 간단한 데모/테스트
✅ 빠른 설치 필요
✅ 의존성 최소화
✅ 기본 기능만 필요

예: 프로토타입, 학습용, 간단한 데모
```

---

## 5. 정확도 최적화

### 5.1 성능 프리셋

#### ⚡ 고속 모드 (기본)

```python
settings = {
    'tolerance': 0.45,        # 적당히 엄격
    'upsample_times': 0,      # 업샘플링 없음
    'frame_scale': 0.25,      # 1/4 크기 처리
    'process_interval': 2     # 2프레임마다 처리
}

# 성능
- FPS: 25-30 (PC), 12-18 (Jetson)
- 거리: 1-2m
- 인원: 3-5명
- 용도: 일반 웹캠, 빠른 응답
```

#### ⚖️ 균형 모드

```python
settings = {
    'tolerance': 0.40,        # 약간 엄격
    'upsample_times': 1,      # 2배 업샘플링
    'frame_scale': 0.25,      # 1/4 크기 처리
    'process_interval': 2     # 2프레임마다 처리
}

# 성능
- FPS: 18-22 (PC), 8-12 (Jetson)
- 거리: 2-4m
- 인원: 5-7명
- 용도: 회의실, 중거리
```

#### 🎥 CCTV 모드

```python
settings = {
    'tolerance': 0.35,        # 매우 엄격
    'upsample_times': 2,      # 4배 업샘플링
    'frame_scale': 0.5,       # 1/2 크기 처리
    'process_interval': 3     # 3프레임마다 처리
}

# 성능
- FPS: 10-15 (PC), 5-8 (Jetson)
- 거리: 1-7m
- 인원: 7-10명
- 용도: 보안, 감시, 원거리
```

### 5.2 수동 튜닝

#### Tolerance (매칭 엄격도)

```python
# 값이 낮을수록 엄격함

tolerance = 0.30  # 매우 엄격 - False Positive 최소
                  # 단점: False Negative 증가

tolerance = 0.40  # 균형 (권장)
                  # 대부분의 상황에 적합

tolerance = 0.50  # 관대
                  # 단점: False Positive 증가
                  # 장점: False Negative 감소

tolerance = 0.60  # 매우 관대 (비권장)
                  # 오탐지 가능성 높음
```

#### Upsample Times (원거리 감도)

```python
upsample_times = 0  # 원본 크기
                    # 장점: 빠름 (2x)
                    # 단점: 작은 얼굴 놓칠 수 있음
                    # 용도: 가까운 거리 (1-2m)

upsample_times = 1  # 2배 확대
                    # 균형 (권장)
                    # 용도: 중거리 (2-4m)

upsample_times = 2  # 4배 확대
                    # 장점: 작은 얼굴, 원거리 감지
                    # 단점: 느림 (1/2 속도)
                    # 용도: CCTV, 원거리 (4-7m)
```

### 5.3 문제별 해결책

#### 오탐지 (False Positive)

```
문제: 다른 사람을 A로 인식

해결책:
1. Tolerance 낮추기 (0.45 → 0.35)
2. 더 많은 얼굴 각도 등록
3. 조명 개선
4. RetinaFace 사용 (더 정확함)
```

#### 미인식 (False Negative)

```
문제: 등록된 사람을 Unknown으로 표시

해결책:
1. Tolerance 높이기 (0.35 → 0.45)
2. Upsample 증가 (0 → 1)
3. 얼굴 재등록 (다양한 각도)
4. 카메라-얼굴 거리 조정
```

#### 느린 속도 (Low FPS)

```
문제: FPS가 10 미만

해결책:
1. 고속 모드 선택
2. Upsample 줄이기 (2 → 0)
3. Frame Scale 줄이기 (0.5 → 0.25)
4. Process Interval 증가 (2 → 3)
5. YOLO-Face 사용 (더 빠름)
```

---

## 6. 플랫폼별 가이드

### 6.1 Windows

#### 6.1.1 Visual Studio Build Tools 설치

```
1. https://visualstudio.microsoft.com/downloads/ 접속
2. "Visual Studio 2022용 Build Tools" 다운로드
3. 설치 프로그램 실행
4. "C++를 사용한 데스크톱 개발" 체크
5. 설치 (약 6-8GB)
6. 재부팅
```

#### 6.1.2 한글 폰트 설정

```python
# gui_screens.py에서 폰트 경로 수정

# Windows 기본 폰트
self.font = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", 30)
self.font_small = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", 20)

# 또는
self.font = ImageFont.truetype("C:/Windows/Fonts/gulim.ttc", 30)
```

#### 6.1.3 카메라 권한

```
설정 → 개인 정보 → 카메라
└── 앱이 카메라에 액세스하도록 허용 → 켜기
```

### 6.2 macOS

#### 6.2.1 Homebrew 설치

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### 6.2.2 CMake 설치

```bash
brew install cmake
```

#### 6.2.3 카메라 권한

```
시스템 환경설정 → 보안 및 개인 정보 보호 → 카메라
└── Terminal.app 또는 Python 체크
```

### 6.3 Jetson Nano

#### 6.3.1 초기 설정

```bash
# 1. Jetson 최적화 스크립트 실행
python jetson_optimize.py

# 2. DISPLAY 환경 변수 설정
export DISPLAY=:0

# 3. 성능 모드 설정
sudo nvpmodel -m 0  # 10W 모드
sudo jetson_clocks    # 클럭 최대화
```

#### 6.3.2 카메라 설정

##### USB 웹캠

```bash
# 카메라 장치 확인
ls /dev/video*

# 해상도 확인
v4l2-ctl --list-formats-ext -d /dev/video0

# 프로그램 실행
python face_recognition_app.py
# 환경 설정 → 카메라 선택
```

##### CSI 카메라

```python
# gui_screens.py 수정

# GStreamer 파이프라인 사용
gst_pipeline = (
    'nvarguscamerasrc ! '
    'video/x-raw(memory:NVMM), width=1280, height=720, format=NV12, framerate=30/1 ! '
    'nvvidconv flip-method=0 ! '
    'video/x-raw, width=640, height=480, format=BGRx ! '
    'videoconvert ! '
    'video/x-raw, format=BGR ! appsink'
)

self.video_capture = cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)
```

#### 6.3.3 성능 최적화

```bash
# Swap 메모리 추가 (4GB)
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 영구 설정
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

#### 6.3.4 문제 해결

##### GUI가 안 나옴

```bash
# 1. DISPLAY 확인
echo $DISPLAY
# 출력 없으면:
export DISPLAY=:0

# 2. X 서버 실행 확인
ps aux | grep X

# 3. 권한 부여
xhost +local:

# 4. .bashrc에 추가
echo 'export DISPLAY=:0' >> ~/.bashrc
```

##### 카메라 해상도 낮음

```bash
# 1. 카메라 지원 해상도 확인
v4l2-ctl --list-formats-ext

# 2. 강제 설정 (gui_screens.py)
self.video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
self.video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
```

##### 화면이 끊김

```bash
# 1. 고속 모드 선택
# 환경 설정 → 고속 모드 (⚡)

# 2. 성능 모드 확인
sudo nvpmodel -m 0
sudo jetson_clocks

# 3. 온도 확인
sudo tegrastats
# 80°C 이상이면 냉각 추가
```

---

## 7. 문제 해결

### 7.1 일반적인 문제

#### 7.1.1 웹캠이 열리지 않음

```python
# 카메라 인덱스 변경
# 환경 설정 → 카메라 선택 → 0, 1, 2 시도

# 또는 코드에서 직접 변경
self.video_capture = cv2.VideoCapture(0)  # 0, 1, 2 시도
```

#### 7.1.2 한글이 표시되지 않음

```python
# 플랫폼별 폰트 경로 확인

# macOS
"/System/Library/Fonts/AppleSDGothicNeo.ttc"
"/Library/Fonts/Arial Unicode.ttf"

# Linux
"/usr/share/fonts/truetype/nanum/NanumGothic.ttf"
"/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# Windows
"C:/Windows/Fonts/malgun.ttf"
"C:/Windows/Fonts/gulim.ttc"
```

#### 7.1.3 ModuleNotFoundError

```bash
# 가상환경 확인
which python
# 출력: /path/to/.venv/bin/python

# 가상환경 활성화
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate      # Windows

# 패키지 재설치
pip install -r requirements.txt
```

#### 7.1.4 dlib 설치 실패

**Linux/macOS:**
```bash
# CMake 설치
sudo apt-get install cmake  # Ubuntu
brew install cmake          # macOS

# dlib 설치
pip install dlib
```

**Windows:**
```bash
# Visual Studio Build Tools 설치 (위 참조)
# 또는 wheel 파일 사용
pip install dlib-19.24.0-cp39-cp39-win_amd64.whl
```

### 7.2 성능 문제

#### 7.2.1 낮은 FPS

```
문제: FPS가 5-10

진단:
1. 콘솔에서 FPS 확인
   [INFO] 현재 FPS: 8.5

해결:
1. 고속 모드 선택 (⚡)
2. Upsample = 0
3. Frame Scale = 0.25
4. YOLO-Face 사용

예상 개선: 8 FPS → 25-30 FPS
```

#### 7.2.2 메모리 부족 (Jetson)

```bash
# 1. Swap 확인
free -h
#        total    used    free
# Swap:   4.0G    2.0G    2.0G

# 2. Swap 추가 (위 참조)

# 3. 프로세스 모니터링
htop

# 4. 설정 최적화
# Frame Scale = 0.25
# Process Interval = 3
```

### 7.3 인식 문제

#### 7.3.1 얼굴이 감지되지 않음

```
원인:
- 조명 부족
- 카메라-얼굴 거리 너무 멀거나 가까움
- 얼굴 각도 극단적

해결:
1. 조명 개선
2. 거리 조정 (1-2m 권장)
3. Upsample 증가 (0 → 1 → 2)
4. RetinaFace 사용 (더 민감함)
```

#### 7.3.2 등록된 사람을 못 알아봄

```
원인:
- Tolerance 너무 낮음
- 등록 시와 현재 조명 차이
- 얼굴 각도 차이

해결:
1. Tolerance 증가 (0.35 → 0.45)
2. 다양한 각도로 재등록
3. 조명 일관성 유지
4. 얼굴 정면 촬영
```

---

## 8. 고급 기능

### 8.1 데이터베이스 구조

#### 8.1.1 테이블 스키마

```sql
-- registered_faces 테이블
CREATE TABLE registered_faces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    student_id TEXT UNIQUE,
    department TEXT,
    grade TEXT,
    encoding BLOB NOT NULL,
    registered_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- recognition_logs 테이블
CREATE TABLE recognition_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    student_id TEXT,
    is_registered INTEGER DEFAULT 0,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 8.1.2 데이터베이스 백업

```bash
# SQLite 데이터베이스 백업
cp face_recognition.db face_recognition_backup_$(date +%Y%m%d).db

# 또는
sqlite3 face_recognition.db ".backup face_recognition_backup.db"
```

#### 8.1.3 데이터베이스 마이그레이션

```bash
# 기존 DB에 새 컬럼 추가
python migrate_database.py
```

### 8.2 커스터마이징

#### 8.2.1 GUI 색상 변경

```python
# gui_screens.py

# 배경색
self.config(bg="#2c3e50")  # 어두운 파랑

# 버튼 색상
button_color = "#27ae60"  # 녹색
button_hover = "#229954"  # 진한 녹색

# 텍스트 색상
text_color = "#ecf0f1"  # 밝은 회색
```

#### 8.2.2 바운딩 박스 스타일

```python
# gui_screens.py - draw_boxes()

# 등록된 사람 (녹색)
color = (0, 255, 0)
thickness = 3

# 미등록 (빨간색)
color = (0, 0, 255)
thickness = 2

# 선 스타일
cv2.rectangle(image, (left, top), (right, bottom), color, thickness)

# 점선 스타일
for i in range(left, right, 10):
    cv2.line(image, (i, top), (i+5, top), color, thickness)
```

#### 8.2.3 로그 레벨 조절

```python
# face_recognition_app.py

import logging

# 로그 레벨 설정
logging.basicConfig(level=logging.INFO)
# DEBUG: 모든 상세 정보
# INFO: 일반 정보 (기본)
# WARNING: 경고만
# ERROR: 오류만
```

### 8.3 API 통합 (예시)

#### 8.3.1 REST API 서버

```python
# api_server.py (예시)

from flask import Flask, request, jsonify
from database import Database

app = Flask(__name__)
db = Database()

@app.route('/api/faces', methods=['GET'])
def get_faces():
    faces = db.get_all_faces()
    return jsonify({
        'count': len(faces['names']),
        'faces': [
            {'name': name, 'student_id': sid}
            for name, sid in zip(faces['names'], faces['student_ids'])
        ]
    })

@app.route('/api/logs', methods=['GET'])
def get_logs():
    logs = db.get_recognition_logs(limit=100)
    return jsonify({'logs': logs})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

#### 8.3.2 웹훅 통합

```python
# gui_screens.py - log_recognition()

import requests

def send_webhook(name, student_id):
    webhook_url = "https://your-server.com/webhook"
    data = {
        'name': name,
        'student_id': student_id,
        'timestamp': time.time()
    }
    try:
        requests.post(webhook_url, json=data, timeout=5)
    except:
        pass  # 실패해도 계속 진행

# 인식 로그에 추가
self.manager.db.log_recognition(name, student_id, True)
send_webhook(name, student_id)  # 웹훅 전송
```

---

## 9. 개발자 정보

### 9.1 프로젝트 구조

```
facedetection-system/
├── face_recognition_app.py    # 메인 애플리케이션 (멀티스크린)
├── face_recognition_gui.py    # 단일 화면 버전
├── gui_screens.py              # GUI 화면 클래스
├── database.py                 # SQLite 데이터베이스 관리
├── retinaface_detector.py      # RetinaFace 감지기
├── yolo_face_detector.py       # YOLO-Face 감지기
├── jetson_optimize.py          # Jetson 최적화 도구
├── download_retinaface.py      # RetinaFace 다운로드 헬퍼
├── migrate_database.py         # DB 마이그레이션
├── requirements.txt            # Python 패키지 목록
├── face_recognition.db         # SQLite 데이터베이스
├── models/                     # 얼굴 감지 모델
│   ├── yolov8n-face.pt        # YOLO-Face 모델
│   └── README.md              # 모델 다운로드 가이드
└── docs/                       # 문서
    ├── COMPLETE_GUIDE.md      # 이 문서
    ├── CHANGELOG.md           # 변경 이력
    └── TECHNICAL_REPORT.md    # 기술 보고서
```

### 9.2 기술 스택

- **Python**: 3.6+
- **face_recognition**: 얼굴 인코딩 및 비교
- **insightface**: RetinaFace 구현
- **ultralytics**: YOLO-Face 구현
- **OpenCV**: 비디오 처리 및 이미지 조작
- **Tkinter**: GUI 프레임워크
- **PIL/Pillow**: 이미지 처리 및 한글 렌더링
- **SQLite3**: 데이터베이스
- **NumPy**: 수치 연산

### 9.3 라이센스

MIT License - 자유롭게 사용, 수정, 배포 가능

### 9.4 기여

GitHub에서 Issue와 Pull Request를 환영합니다!

**GitHub**: https://github.com/limchanggeon/facedetection-system

### 9.5 문의

- **개발자**: limchanggeon
- **이메일**: [GitHub 프로필 참조]
- **버그 리포트**: [GitHub Issues](https://github.com/limchanggeon/facedetection-system/issues)

---

## 10. 부록

### 10.1 단축키

| 키 | 기능 |
|----|------|
| **스페이스바** | 얼굴 등록 시 촬영 |
| **Enter** | 등록 완료 |
| **ESC** | 등록 취소 |

### 10.2 성능 벤치마크

#### PC (Intel i7, 16GB RAM, RTX 2060)

| 모드 | HOG | YOLO-Face | RetinaFace |
|------|-----|-----------|------------|
| 고속 | 25-30 | 40-55 | 30-45 |
| 균형 | 18-22 | 25-40 | 20-35 |
| CCTV | 10-15 | 15-30 | 12-25 |

#### Jetson Nano (4GB)

| 모드 | HOG | YOLO-Face | RetinaFace |
|------|-----|-----------|------------|
| 고속 | 8-12 | 12-18 | 10-15 |
| 균형 | 5-8 | 8-12 | 7-10 |
| CCTV | 3-5 | 5-8 | 4-6 |

### 10.3 FAQ

**Q1: GPU가 없어도 작동하나요?**
```
A: 네! CPU만으로도 작동합니다. HOG 모드를 사용하면 됩니다.
   GPU가 있으면 YOLO-Face나 RetinaFace로 더 빠른 성능을 얻을 수 있습니다.
```

**Q2: 몇 명까지 동시 인식 가능한가요?**
```
A: 
- PC: 최대 10명 (CCTV 모드)
- Jetson Nano: 5-7명 (균형 모드)
- 실시간 요구: 3-5명 (고속 모드)
```

**Q3: 마스크를 쓴 얼굴도 인식하나요?**
```
A: 부분적으로 가능하지만 정확도가 떨어집니다.
   마스크를 쓴 상태로 등록하면 인식률이 향상됩니다.
```

**Q4: 상용 프로젝트에 사용할 수 있나요?**
```
A: MIT 라이센스이므로 상업적 사용 가능합니다.
   단, face_recognition 라이브러리의 라이센스도 확인하세요.
```

**Q5: 클라우드 서버에 배포할 수 있나요?**
```
A: 네! GUI를 비활성화하고 API 서버로 전환하면 됩니다.
   Flask/FastAPI와 통합 가능합니다.
```

### 10.4 업데이트 이력

최신 변경사항은 `CHANGELOG.md`를 참조하세요.

**최신 버전**: v2.3.3 (2024-10-27)
- RetinaFace 바운딩 박스 수정
- insightface 직접 사용으로 전환
- 감지기 선택 UI 추가

---

**마지막 업데이트**: 2024년 10월 27일  
**문서 버전**: 2.3.3  
**작성자**: limchanggeon

🎉 **행복한 코딩 되세요!**
