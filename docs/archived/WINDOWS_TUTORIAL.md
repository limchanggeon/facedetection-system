# 🪟 Windows 환경에서 실행하기

이 가이드는 Windows 10/11 (Intel i5 이상)에서 얼굴 인식 시스템을 설치하고 실행하는 방법을 설명합니다.

## 📋 목차
1. [시스템 요구사항](#시스템-요구사항)
2. [설치 과정](#설치-과정)
3. [실행 방법](#실행-방법)
4. [성능 최적화](#성능-최적화)
5. [문제 해결](#문제-해결)

---

## 📌 시스템 요구사항

### 하드웨어
- **CPU**: Intel i5 이상 (Intel i7 권장)
- **RAM**: 최소 8GB (16GB 권장)
- **카메라**: 내장 웹캠 또는 USB 웹캠
- **저장공간**: 최소 5GB 여유 공간

### 소프트웨어
- **OS**: Windows 10/11 (64-bit)
- **Python**: 3.7 ~ 3.11 (3.9 권장)
- **Visual Studio**: Build Tools 또는 Community Edition

---

## 🔧 설치 과정

### 1. Python 설치

#### Option A: Python.org에서 설치 (권장)

1. [Python 공식 웹사이트](https://www.python.org/downloads/) 방문
2. **Python 3.9.x** 다운로드 (안정적인 버전)
3. 설치 시 **"Add Python to PATH"** 체크 ✅
4. "Install Now" 클릭

설치 확인:
```cmd
python --version
pip --version
```

#### Option B: Microsoft Store에서 설치

```powershell
# Microsoft Store에서 "Python 3.9" 검색 후 설치
```

### 2. Visual Studio Build Tools 설치

dlib 컴파일을 위해 필요합니다.

#### Option A: Visual Studio Community (권장)

1. [Visual Studio 다운로드](https://visualstudio.microsoft.com/downloads/)
2. **Visual Studio Community** 다운로드
3. 설치 시 **"C++를 사용한 데스크톱 개발"** 워크로드 선택 ✅
4. 설치 완료 후 재부팅

#### Option B: Build Tools만 설치

1. [Build Tools 다운로드](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
2. **"C++ 빌드 도구"** 선택
3. 설치 완료 후 재부팅

### 3. CMake 설치

```powershell
# Chocolatey 사용 (선택사항)
choco install cmake

# 또는 수동 설치
# https://cmake.org/download/ 에서 Windows x64 Installer 다운로드
```

수동 설치 시 **"Add CMake to PATH"** 체크 ✅

### 4. 프로젝트 클론

```cmd
cd %USERPROFILE%\Desktop
git clone https://github.com/limchanggeon/facedetection-system.git
cd facedetection-system
```

### 5. 가상 환경 생성 (권장)

```cmd
python -m venv .venv
.venv\Scripts\activate
```

### 6. Python 패키지 설치

#### 빠른 설치 (대부분의 경우)

```cmd
pip install --upgrade pip
pip install -r requirements.txt
```

#### dlib 설치 문제 시

**Step 1**: dlib 미리 컴파일된 버전 설치 시도

```cmd
pip install dlib-binary
```

**Step 2**: 위 방법 실패 시 소스에서 컴파일

```cmd
pip install cmake
pip install dlib
```

**Step 3**: 여전히 실패 시 미리 빌드된 wheel 사용

1. [dlib wheel 다운로드](https://github.com/z-mahmud22/Dlib_Windows_Python3.x)
2. Python 버전과 일치하는 파일 다운로드 (예: `dlib-19.24.0-cp39-cp39-win_amd64.whl`)
3. 설치:

```cmd
pip install dlib-19.24.0-cp39-cp39-win_amd64.whl
```

#### 나머지 패키지 설치

```cmd
pip install face_recognition opencv-python Pillow
```

### 7. 한글 폰트 확인

Windows는 기본적으로 한글 폰트가 설치되어 있습니다:
- `C:\Windows\Fonts\malgun.ttf` (맑은 고딕)
- `C:\Windows\Fonts\gulim.ttc` (굴림)

---

## 🎮 실행 방법

### 기본 실행

```cmd
# 가상환경 활성화 (사용 시)
.venv\Scripts\activate

# 프로그램 실행
python face_recognition_gui.py
```

### PowerShell에서 실행

```powershell
# 가상환경 활성화
.\.venv\Scripts\Activate.ps1

# 실행 정책 오류 시
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 프로그램 실행
python face_recognition_gui.py
```

### 바로가기 생성

**실행 배치 파일 생성** (`run.bat`):

```batch
@echo off
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python face_recognition_gui.py
pause
```

파일 저장 후 더블클릭으로 실행 가능합니다.

### Windows 작업 스케줄러로 자동 시작

1. **작업 스케줄러** 열기 (Win + R → `taskschd.msc`)
2. **"기본 작업 만들기"** 클릭
3. 이름: "Face Recognition System"
4. 트리거: "컴퓨터를 시작할 때"
5. 작업: "프로그램 시작"
6. 프로그램: `C:\Users\YourName\Desktop\facedetection-system\run.bat`

---

## ⚡ 성능 최적화

### 1. 고성능 전원 모드 설정

```
설정 → 시스템 → 전원 및 배터리 → 전원 모드 → "최고 성능"
```

### 2. 백그라운드 앱 비활성화

```
설정 → 개인 정보 및 보안 → 백그라운드 앱 → 불필요한 앱 끄기
```

### 3. 프로세서 우선순위 설정

프로그램 실행 중:
1. **작업 관리자** 열기 (Ctrl + Shift + Esc)
2. **세부 정보** 탭 → `python.exe` 찾기
3. 마우스 오른쪽 클릭 → **우선순위 설정** → "높음"

### 4. 프레임 처리 최적화

`face_recognition_gui.py`에서 성능에 맞게 조정:

```python
# Intel i5 (낮은 성능)
process_every_n_frames = 5

# Intel i7 (중간 성능)
process_every_n_frames = 3

# Intel i9 또는 GPU (높은 성능)
process_every_n_frames = 2
```

### 5. NumPy 최적화

Intel MKL 최적화 버전 설치:

```cmd
pip uninstall numpy
pip install numpy-mkl
```

---

## 🔍 카메라 설정

### 카메라 인덱스 확인

여러 카메라가 있는 경우:

```python
# 테스트 스크립트 (test_camera.py)
import cv2

for i in range(5):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"카메라 {i}: 사용 가능")
        ret, frame = cap.read()
        if ret:
            print(f"  해상도: {frame.shape[1]}x{frame.shape[0]}")
        cap.release()
    else:
        print(f"카메라 {i}: 사용 불가")
```

실행:
```cmd
python test_camera.py
```

### 카메라 변경

`face_recognition_gui.py`에서:

```python
# 기본 카메라 (0)
self.video_capture = cv2.VideoCapture(0)

# 외장 USB 카메라 (1)
self.video_capture = cv2.VideoCapture(1)
```

### 카메라 해상도 설정

```python
self.video_capture = cv2.VideoCapture(0)
self.video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
self.video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
```

---

## 🐛 문제 해결

### 1. "Python이 인식되지 않습니다" 오류

**증상**: `'python'은(는) 내부 또는 외부 명령, 실행할 수 있는 프로그램, 또는 배치 파일이 아닙니다.`

**해결책**:

```cmd
# Python 경로 확인
where python

# PATH에 추가 (관리자 권한으로 CMD 실행)
setx PATH "%PATH%;C:\Users\YourName\AppData\Local\Programs\Python\Python39"
setx PATH "%PATH%;C:\Users\YourName\AppData\Local\Programs\Python\Python39\Scripts"

# 또는 시스템 환경 변수에서 수동 추가
제어판 → 시스템 → 고급 시스템 설정 → 환경 변수 → Path 편집
```

### 2. dlib 설치 실패

**증상**: `error: Microsoft Visual C++ 14.0 is required`

**해결책**:

1. **Visual Studio Build Tools 재설치**
2. **미리 빌드된 wheel 사용** (위 설치 섹션 참조)
3. **Anaconda 사용**:

```cmd
conda install -c conda-forge dlib
```

### 3. "vcruntime140.dll이 없습니다" 오류

**해결책**:

[Visual C++ 재배포 패키지](https://support.microsoft.com/ko-kr/help/2977003/the-latest-supported-visual-c-downloads) 설치

### 4. 카메라 접근 권한 오류

**해결책**:

```
설정 → 개인 정보 및 보안 → 카메라 → "앱이 카메라에 액세스하도록 허용" 켜기
```

### 5. 한글 폰트 깨짐

**증상**: 한글이 □□□로 표시됨

**해결책**:

`face_recognition_gui.py`의 폰트 경로 확인:

```python
# Windows 기본 폰트
try:
    self.font = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", 30)
    self.font_small = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", 20)
except:
    # 대체 폰트
    self.font = ImageFont.truetype("C:/Windows/Fonts/gulim.ttc", 30)
    self.font_small = ImageFont.truetype("C:/Windows/Fonts/gulim.ttc", 20)
```

### 6. GUI 창이 느리게 반응

**해결책**:

1. **Windows 애니메이션 효과 끄기**:
   ```
   설정 → 접근성 → 시각 효과 → 애니메이션 효과 끄기
   ```

2. **하드웨어 가속 활성화**:
   ```python
   # face_recognition_gui.py 시작 부분에 추가
   import os
   os.environ['TK_SILENCE_DEPRECATION'] = '1'
   ```

### 7. 메모리 부족 오류

**해결책**:

1. **가상 메모리 늘리기**:
   ```
   제어판 → 시스템 → 고급 시스템 설정 → 성능 설정 → 고급 → 가상 메모리 변경
   ```

2. **프레임 간격 증가**:
   ```python
   process_every_n_frames = 5  # 더 높은 값으로
   ```

---

## 📊 성능 벤치마크

### Intel i5 (8세대 이상, 8GB RAM)
- **FPS**: 15-20
- **해상도**: 1056x594
- **CPU 사용률**: 40-60%

### Intel i7 (8세대 이상, 16GB RAM)
- **FPS**: 20-25
- **해상도**: 1056x594
- **CPU 사용률**: 30-50%

### Intel i9 (10세대 이상, 32GB RAM)
- **FPS**: 25-30+
- **해상도**: 1920x1080 가능
- **CPU 사용률**: 20-40%

---

## 💡 추가 팁

### 1. Anaconda 사용 (권장 대안)

복잡한 의존성 문제를 피하려면:

```cmd
# Anaconda 설치 후
conda create -n face_recognition python=3.9
conda activate face_recognition
conda install -c conda-forge dlib
pip install face_recognition opencv-python Pillow
```

### 2. Windows Defender 예외 추가

프로그램 실행 속도 향상:

```
Windows 보안 → 바이러스 및 위협 방지 → 설정 관리 → 제외 추가
→ 폴더 추가 → "facedetection-system" 폴더 선택
```

### 3. 성능 모니터링

```cmd
# 리소스 모니터 열기
resmon

# 또는 작업 관리자 (Ctrl + Shift + Esc)
```

### 4. 로그 파일 저장

```cmd
python face_recognition_gui.py > log.txt 2>&1
```

### 5. GPU 가속 (NVIDIA GPU 있는 경우)

```cmd
# CUDA Toolkit 설치 후
pip uninstall dlib
pip install dlib-cuda
```

---

## 🔒 보안 및 개인정보

### 데이터베이스 암호화

민감한 얼굴 데이터 보호:

```python
# database.py에 추가
from cryptography.fernet import Fernet

# 암호화 키 생성
key = Fernet.generate_key()
cipher = Fernet(key)

# 얼굴 인코딩 암호화
encrypted_encoding = cipher.encrypt(pickle.dumps(encoding))
```

### 방화벽 설정

프로그램이 외부 접근이 필요 없으므로:

```
Windows Defender 방화벽 → 고급 설정 → 인바운드 규칙
→ Python 관련 규칙 모두 차단
```

---

## 📚 추가 자료

- [Python Windows 공식 문서](https://docs.python.org/3/using/windows.html)
- [Visual Studio 설치 가이드](https://visualstudio.microsoft.com/downloads/)
- [OpenCV Windows 설치](https://docs.opencv.org/master/d5/de5/tutorial_py_setup_in_windows.html)
- [Windows 카메라 설정](https://support.microsoft.com/ko-kr/windows/camera-settings)

---

## 🆘 지원

문제가 발생하면:
1. [Issues](https://github.com/limchanggeon/facedetection-system/issues)에 보고
2. Windows 버전 명시 (Win + R → `winver`)
3. Python 버전 명시 (`python --version`)
4. 오류 로그 첨부

---

## 📝 라이센스

MIT License - 자세한 내용은 [LICENSE](LICENSE) 파일 참조

---

## ✅ 체크리스트

설치 전 확인:
- [ ] Python 3.7-3.11 설치됨
- [ ] Visual Studio Build Tools 설치됨
- [ ] CMake 설치됨 (선택사항)
- [ ] 웹캠 작동 확인
- [ ] 관리자 권한 있음

설치 후 확인:
- [ ] `python --version` 작동
- [ ] `pip list` 에서 face_recognition 확인
- [ ] 카메라 권한 허용됨
- [ ] 프로그램 실행 성공
