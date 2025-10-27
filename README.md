# 🎯 얼굴 인식 시스템 v2.3.3

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey.svg)](https://github.com/limchanggeon/facedetection-system)

SQLite 데이터베이스와 멀티 스크린 GUI를 갖춘 실시간 얼굴 인식 시스템입니다.

---

## ✨ 주요 기능

- 🎥 **실시간 멀티 얼굴 인식**: 최대 10명 동시 인식
- 👥 **CCTV 스타일 탐지**: 원거리/근거리 얼굴 동시 탐지
- 🏆 **3가지 감지 엔진**: RetinaFace(정확도) / YOLO-Face(속도) / HOG(기본)
- 👤 **얼굴 등록 시스템**: GUI를 통한 간편한 등록
- 💾 **SQLite 데이터베이스**: 영구 저장 및 로그 관리
- 🎨 **직관적인 멀티스크린 GUI**: Tkinter 기반
- 🇰🇷 **완벽한 한글 지원**: 한글 이름 표시
- ⚙️ **실시간 설정 조절**: GUI에서 정확도/속도 조절
- 🚀 **Jetson 최적화**: NVIDIA Jetson Nano 지원

---

## 🚀 빠른 시작

### 1. 설치

```bash
# 저장소 클론
git clone https://github.com/limchanggeon/facedetection-system.git
cd facedetection-system

# 가상 환경 생성 및 활성화
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# 패키지 설치
pip install -r requirements.txt
```

### 2. 실행

```bash
# 멀티 스크린 GUI (권장)
python face_recognition_app.py

# 단일 화면 GUI (레거시)
python face_recognition_gui.py
```

### 3. 기본 사용법

```
1️⃣ 환경 설정 → 카메라 선택 및 감지 엔진 설정
2️⃣ 얼굴 등록 관리 → 새 얼굴 등록
3️⃣ 얼굴 인식 시작 → 실시간 인식
4️⃣ 데이터베이스 관리 → 등록된 얼굴 확인 및 로그 보기
```

---

## 📖 상세 문서

### 📘 완벽 가이드
**[📗 전체 튜토리얼 보기](docs/COMPLETE_GUIDE.md)** ⬅️ **여기를 클릭하세요!**

통합 가이드에는 다음 내용이 포함되어 있습니다:

- 🔧 **설치 가이드**: Windows/macOS/Linux/Jetson Nano
- 🎨 **사용 방법**: 멀티 스크린 GUI 완벽 가이드
- 🤖 **얼굴 감지 엔진**: RetinaFace/YOLO-Face/HOG 설치 및 비교
- 🎯 **정확도 최적화**: 성능 튜닝 및 문제 해결
- 🖥️ **플랫폼별 가이드**: 각 OS별 상세 설명
- 🔍 **문제 해결**: 일반적인 문제 및 해결책
- 💡 **고급 기능**: API 통합, 커스터마이징

### 📄 기타 문서

- **[CHANGELOG.md](docs/CHANGELOG.md)**: 버전 히스토리 및 변경 이력
- **[TECHNICAL_REPORT.md](docs/TECHNICAL_REPORT.md)**: 기술 보고서
- **[models/README.md](models/README.md)**: 모델 다운로드 가이드

---

## 🏆 얼굴 감지 엔진 비교

| 특징 | RetinaFace 🏆 | YOLO-Face ⚡ | HOG 🔧 |
|------|---------------|--------------|---------|
| **정확도** | ★★★★★ | ★★★★☆ | ★★★☆☆ |
| **속도** | ★★★★☆ | ★★★★★ | ★★☆☆☆ |
| **작은 얼굴** | ★★★★★ | ★★★★☆ | ★★☆☆☆ |
| **다양한 각도** | ★★★★★ | ★★★★☆ | ★★☆☆☆ |
| **GPU 가속** | ✅ | ✅ | ❌ |
| **모델 크기** | 16MB | 6MB | 없음 |

### 빠른 설치

```bash
# RetinaFace (자동 다운로드)
python download_retinaface.py

# YOLO-Face (수동 다운로드)
cd models
wget https://github.com/derronqi/yolov8-face/releases/download/v0.0.0/yolov8n-face.pt

# HOG (설치 불필요 - 기본 포함)
```

---

## 📋 시스템 요구사항

### 기본 요구사항
- **Python**: 3.6 이상
- **카메라**: 웹캠 또는 CSI 카메라
- **OS**: Linux, macOS, Windows

### 하드웨어 권장사양
- **CPU**: Intel i5 이상 또는 ARM (Jetson)
- **RAM**: 4GB 이상 (8GB 권장)
- **저장공간**: 1GB 이상

---

## 📦 주요 패키지

```
face-recognition    # 얼굴 인코딩 및 비교
insightface         # RetinaFace 구현
ultralytics         # YOLO-Face 구현
opencv-python       # 비디오 처리
Pillow              # 이미지 처리 및 한글 렌더링
```

전체 목록은 `requirements.txt` 참조

---

## 🎯 프로젝트 구조

```
facedetection-system/
├── face_recognition_app.py    # 메인 애플리케이션 (멀티스크린)
├── face_recognition_gui.py    # 단일 화면 버전
├── gui_screens.py              # GUI 화면 클래스
├── database.py                 # SQLite 데이터베이스 관리
├── retinaface_detector.py      # RetinaFace 감지기
├── yolo_face_detector.py       # YOLO-Face 감지기
├── jetson_optimize.py          # Jetson 최적화 도구
├── requirements.txt            # Python 패키지 목록
├── face_recognition.db         # SQLite 데이터베이스
├── models/                     # 얼굴 감지 모델
│   ├── yolov8n-face.pt        # YOLO-Face 모델
│   └── README.md              # 모델 다운로드 가이드
└── docs/                       # 문서
    ├── COMPLETE_GUIDE.md      # 📗 통합 튜토리얼 (추천!)
    ├── CHANGELOG.md           # 변경 이력
    └── TECHNICAL_REPORT.md    # 기술 보고서
```

---

## 🔧 주요 기능

### 1️⃣ 실시간 얼굴 인식
- 최대 10명 동시 인식
- 🟢 녹색 박스: 등록된 사람 (이름 + 신뢰도)
- 🔴 빨간 박스: 미등록 (Unknown)

### 2️⃣ 얼굴 등록
- GUI를 통한 간편한 등록
- 학생 정보 입력 (이름, 학번, 학과, 학년)
- 다양한 각도 등록 가능

### 3️⃣ 데이터베이스 관리
- SQLite 기반 영구 저장
- 등록된 얼굴 조회 및 삭제
- 인식 로그 확인 (최근 100개)

### 4️⃣ 환경 설정
- 카메라 선택 및 테스트
- 얼굴 감지 엔진 선택 (RetinaFace/YOLO/HOG)
- 성능 프리셋 (고속/균형/CCTV 모드)
- 정확도 수동 조절 (Tolerance, Upsample)

---

## 🚀 성능 벤치마크

### PC (Intel i7, 16GB RAM, RTX 2060)

| 모드 | FPS | 거리 | 인원 |
|------|-----|------|------|
| ⚡ 고속 | 25-30 | 1-2m | 3-5명 |
| ⚖️ 균형 | 18-22 | 2-4m | 5-7명 |
| 🎥 CCTV | 10-15 | 1-7m | 7-10명 |

### Jetson Nano (4GB)

| 모드 | FPS | 거리 | 인원 |
|------|-----|------|------|
| ⚡ 고속 | 8-12 | 1-2m | 3-5명 |
| ⚖️ 균형 | 5-8 | 2-4m | 5-7명 |
| 🎥 CCTV | 3-5 | 1-7m | 7-10명 |

---

## ❓ FAQ

**Q1: GPU가 없어도 작동하나요?**
```
A: 네! CPU만으로도 작동합니다. HOG 모드를 사용하면 됩니다.
```

**Q2: 몇 명까지 동시 인식 가능한가요?**
```
A: PC는 최대 10명, Jetson Nano는 5-7명 정도입니다.
```

**Q3: 마스크를 쓴 얼굴도 인식하나요?**
```
A: 부분적으로 가능하지만 정확도가 떨어집니다.
   마스크 착용 상태로 등록하면 인식률이 향상됩니다.
```

**Q4: 상용 프로젝트에 사용할 수 있나요?**
```
A: MIT 라이센스이므로 상업적 사용 가능합니다.
```

더 많은 질문은 [📗 완벽 가이드](docs/COMPLETE_GUIDE.md)를 참조하세요!

---

## 🐛 문제 해결

일반적인 문제와 해결책은 [📗 완벽 가이드 - 문제 해결](docs/COMPLETE_GUIDE.md#7-문제-해결) 섹션을 참조하세요.

### 빠른 링크
- [웹캠이 열리지 않음](docs/COMPLETE_GUIDE.md#711-웹캠이-열리지-않음)
- [한글이 표시되지 않음](docs/COMPLETE_GUIDE.md#712-한글이-표시되지-않음)
- [dlib 설치 실패](docs/COMPLETE_GUIDE.md#714-dlib-설치-실패)
- [Jetson GUI 문제](docs/COMPLETE_GUIDE.md#734-문제-해결)

---

## 📜 라이센스

MIT License - 자유롭게 사용, 수정, 배포 가능

---

## 🤝 기여

GitHub에서 Issue와 Pull Request를 환영합니다!

---

## 📧 문의

- **개발자**: limchanggeon
- **GitHub**: https://github.com/limchanggeon/facedetection-system
- **Issues**: https://github.com/limchanggeon/facedetection-system/issues

---

## 🎉 시작하기

1. **[저장소 클론](#1-설치)**하고 패키지를 설치하세요
2. **`python face_recognition_app.py`** 실행
3. **[📗 완벽 가이드](docs/COMPLETE_GUIDE.md)**에서 자세한 사용법을 확인하세요

**행복한 코딩 되세요! 🚀**

---

**버전**: v2.3.3 | **마지막 업데이트**: 2024-10-27
