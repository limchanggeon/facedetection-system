# 🎯 실시간 얼굴 인식 시스템

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey.svg)](https://github.com/limchanggeon/facedetection-system)

SQLite 데이터베이스와 GUI를 갖춘 실시간 얼굴 인식 시스템입니다. NVIDIA Jetson 플랫폼에 최적화되어 있습니다.

## ✨ 주요 기능

- 🎥 **실시간 얼굴 인식**: 웹캠을 통한 실시간 얼굴 인식 및 추적
- 👤 **얼굴 등록 시스템**: GUI를 통한 간편한 얼굴 등록
- 💾 **SQLite 데이터베이스**: 얼굴 정보 및 인식 로그 영구 저장
- 🎨 **직관적인 GUI**: Tkinter 기반의 사용하기 쉬운 인터페이스
- 🔍 **바운딩 박스 표시**:
  - 🟢 **녹색 박스**: 등록된 사람 (이름 표시)
  - 🔴 **빨간 박스**: 미등록 (Unknown 표시)
- 🇰🇷 **한글 지원**: 완벽한 한글 이름 표시
- 📊 **인식 로그**: 모든 인식 내역 자동 저장
- ⚡ **부드러운 추적**: 선형 보간을 통한 자연스러운 바운딩 박스 이동
- 🚀 **Jetson 최적화**: NVIDIA Jetson 플랫폼에서 효율적 실행

## 📋 시스템 요구사항

### 기본 요구사항
- **Python**: 3.6 이상
- **카메라**: 웹캠 또는 CSI 카메라
- **OS**: Linux, macOS, Windows

### Jetson 환경
- **모델**: Jetson Nano, Xavier NX, AGX Orin 등
- **JetPack**: 4.6 이상
- **메모리**: 최소 4GB RAM (8GB 권장)

## 🚀 빠른 시작

### 1. 저장소 클론

```bash
git clone https://github.com/limchanggeon/facedetection-system.git
cd facedetection-system
```

### 2. 가상 환경 생성 (권장)

```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\\Scripts\\activate  # Windows
```

### 3. 패키지 설치

```bash
pip install -r requirements.txt
```

### 4. 프로그램 실행

```bash
python3 face_recognition_gui.py
```

## 📖 사용 방법

### 1️⃣ 얼굴 등록

1. **"새 얼굴 등록"** 버튼 클릭
2. 이름 입력 (예: "홍길동")
3. 카메라를 보고 **스페이스바**를 눌러 촬영
4. ESC로 취소 가능

### 2️⃣ 얼굴 인식 시작

1. **"얼굴 인식 시작"** 버튼 클릭
2. 웹캠으로 실시간 인식
   - 🟢 **녹색 박스** + 이름: 등록된 사람
   - 🔴 **빨간 박스** + "Unknown": 미등록

### 3️⃣ 얼굴 관리

- 목록에서 이름 선택 → **"선택한 얼굴 삭제"** 버튼 클릭
- 통계에서 등록된 얼굴 수 확인

### 4️⃣ 정지

- **"정지"** 버튼으로 인식 중지

## 📂 프로젝트 구조

```
facedetection-system/
├── face_recognition_gui.py   # GUI 메인 프로그램
├── database.py                # SQLite 데이터베이스 관리
├── requirements.txt           # Python 패키지 목록
├── README.md                  # 프로젝트 설명서
├── JETSON_TUTORIAL.md        # Jetson 환경 튜토리얼
├── LICENSE                    # MIT 라이센스
├── .gitignore                # Git 무시 파일
└── face_recognition.db       # SQLite 데이터베이스 (자동 생성)
```

## 💾 데이터베이스 구조

### `registered_faces` 테이블
- `id`: 고유 ID (Primary Key)
- `name`: 등록된 사람 이름
- `encoding`: 얼굴 인코딩 데이터 (BLOB)
- `registered_date`: 등록 날짜 (TIMESTAMP)

### `recognition_logs` 테이블
- `id`: 고유 ID (Primary Key)
- `name`: 인식된 이름 (Unknown 포함)
- `is_registered`: 등록 여부 (1: 등록됨, 0: 미등록)
- `timestamp`: 인식 시간 (TIMESTAMP)

## ⚙️ 설정 및 최적화

### 인식 정확도 조정

`face_recognition_gui.py`에서:

```python
# tolerance 값 조정 (0.4~0.6, 낮을수록 엄격)
tolerance=0.5
```

### 처리 속도 조정

```python
# 프레임 간격 조정 (3~10, 높을수록 빠르지만 부드러움 감소)
process_every_n_frames = 3
```

### 바운딩 박스 부드러움

```python
# smoothing_factor (0.1~0.5, 낮을수록 부드럽지만 느림)
smoothing_factor = 0.3
```

## 🎮 플랫폼별 환경 설정

### NVIDIA Jetson
Jetson 플랫폼에서 실행하려면 **[JETSON_TUTORIAL.md](JETSON_TUTORIAL.md)**를 참조하세요.

주요 내용:
- CUDA 지원 dlib 설치
- CSI 카메라 설정
- 성능 최적화
- 문제 해결

### Windows (Intel i5 등)
Windows 환경에서 실행하려면 **[WINDOWS_TUTORIAL.md](WINDOWS_TUTORIAL.md)**를 참조하세요.

주요 내용:
- Visual Studio Build Tools 설치
- dlib 설치 가이드
- 카메라 설정
- 한글 폰트 설정
- 성능 최적화

## 📊 성능

### 일반 PC (Intel i5, 16GB RAM)
- **FPS**: 20-25
- **해상도**: 1056x594
- **모델**: HOG

### Jetson Nano (4GB)
- **FPS**: 10-15
- **해상도**: 1056x594
- **모델**: HOG

### Jetson Xavier NX
- **FPS**: 20-25
- **해상도**: 1056x594
- **모델**: HOG

### Windows PC (Intel i7, 16GB RAM)
- **FPS**: 20-25
- **해상도**: 1056x594
- **모델**: HOG

## 🛠️ 기술 스택

- **Python**: 3.6+
- **face_recognition**: 얼굴 인식 라이브러리
- **OpenCV**: 비디오 처리
- **Tkinter**: GUI 프레임워크
- **PIL/Pillow**: 이미지 처리 및 한글 렌더링
- **SQLite3**: 데이터베이스
- **NumPy**: 수치 연산

## 🐛 문제 해결

### 웹캠이 열리지 않음

```python
# 카메라 인덱스 변경 (0, 1, 2 시도)
self.video_capture = cv2.VideoCapture(0)
```

### 한글이 표시되지 않음

폰트 경로 확인 및 수정:

```python
# macOS
self.font = ImageFont.truetype("/System/Library/Fonts/AppleSDGothicNeo.ttc", 30)

# Linux
self.font = ImageFont.truetype("/usr/share/fonts/truetype/nanum/NanumGothic.ttf", 30)

# Windows
self.font = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", 30)
```

### 메모리 부족 (Jetson)

[JETSON_TUTORIAL.md](JETSON_TUTORIAL.md)의 "메모리 부족 오류" 섹션 참조

## 📝 라이센스

이 프로젝트는 MIT 라이센스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🤝 기여

기여는 언제나 환영합니다!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📧 연락처

Lim Changgeon - [@limchanggeon](https://github.com/limchanggeon)

Project Link: [https://github.com/limchanggeon/facedetection-system](https://github.com/limchanggeon/facedetection-system)

## 🙏 감사의 말

- [face_recognition](https://github.com/ageitgey/face_recognition) - 강력한 얼굴 인식 라이브러리
- [dlib](http://dlib.net/) - 머신러닝 도구킷
- [OpenCV](https://opencv.org/) - 컴퓨터 비전 라이브러리

---

⭐ 이 프로젝트가 도움이 되었다면 Star를 눌러주세요!
