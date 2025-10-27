# 실시간 얼굴 인식 시스템 기술 명세서

## 1. 프로젝트 개요

### 1.1 시스템 목적
학생 정보를 포함한 실시간 다중 얼굴 인식 시스템 구현

### 1.2 개발 환경
- 언어: Python 3.9+
- 운영체제: macOS, Windows, Linux (Jetson Nano 지원)
- 개발 도구: VS Code

## 2. 핵심 기술 스택

### 2.1 얼굴 인식 라이브러리
**YOLOv5-face + face_recognition**
- YOLO-Face: 얼굴 감지 전용 YOLOv5 모델
- 기반: PyTorch 딥러닝 프레임워크
- 얼굴 감지: YOLO-Face (YOLOv5 기반)
- 얼굴 인코딩: dlib 기반 face_recognition (128차원 벡터)
- 얼굴 비교: 유클리드 거리 계산 방식
- GPU 가속: CUDA 지원 (Jetson Nano 최적화)

### 2.2 딥러닝 프레임워크
**PyTorch (v2.0+)**
- 딥러닝 모델 실행 엔진
- GPU 가속 지원 (CUDA/cuDNN)
- Jetson Nano 최적화
- 동적 계산 그래프

**Ultralytics YOLOv5**
- YOLO-Face 모델 백엔드
- 사전 학습된 가중치 제공
- 실시간 추론 최적화

### 2.3 컴퓨터 비전
**OpenCV (v4.12.0)**
- 비디오 캡처 및 프레임 처리
- 이미지 전처리 (리사이징, 색상 변환)
- 카메라 제어 및 다중 카메라 지원

### 2.3 이미지 처리
**Pillow (PIL)**
- 한글 텍스트 렌더링
- ImageDraw를 통한 바운딩 박스 그리기
- 폰트 관리 (AppleSDGothicNeo.ttc)

### 2.4 데이터 처리
**NumPy**
- 배열 연산 및 이미지 데이터 처리
- 선형 보간을 통한 부드러운 추적
- 얼굴 위치 좌표 계산

## 3. 데이터베이스 설계

### 3.1 데이터베이스 시스템
**SQLite3**
- 임베디드 관계형 데이터베이스
- 서버 불필요, 파일 기반 저장
- 스레드 안전 모드 (check_same_thread=False)

### 3.2 테이블 구조

**registered_faces (등록된 얼굴)**
```sql
CREATE TABLE registered_faces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    student_id TEXT UNIQUE NOT NULL,
    department TEXT NOT NULL,
    grade TEXT NOT NULL,
    encoding BLOB NOT NULL,
    registered_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**recognition_logs (인식 로그)**
```sql
CREATE TABLE recognition_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    student_id TEXT,
    is_registered INTEGER NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3.3 데이터 직렬화
**pickle**
- 얼굴 인코딩 벡터를 BLOB로 변환
- Python 객체의 직렬화 및 역직렬화

## 4. 얼굴 인식 알고리즘

### 4.1 얼굴 감지 (Face Detection)
**YOLO-Face (YOLOv5-face)**
- 딥러닝 기반 실시간 객체 감지 모델
- CNN (Convolutional Neural Network) 아키텍처
- GPU 가속 지원 (CUDA)
- HOG 대비 3-5배 빠른 처리 속도

**모델 구조**
- Backbone: CSPDarknet53
- Neck: PANet (Path Aggregation Network)
- Head: YOLO Detection Head
- 입력: 640x640 RGB 이미지
- 출력: 바운딩 박스 좌표 + 신뢰도 점수

**업샘플링 (Upsampling)**
- 원본 이미지 확대 후 감지
- 작은 얼굴 및 원거리 감지 향상
- 설정 범위: 0~2 (0: 원본, 1: 2배, 2: 4배)
- GPU 활용으로 성능 저하 최소화

### 4.2 얼굴 인코딩 (Face Encoding)
**dlib 딥러닝 모델**
- ResNet 기반 신경망
- 68개 얼굴 랜드마크 추출
- 128차원 특징 벡터 생성

### 4.3 얼굴 인식 (Face Recognition)
**유클리드 거리 계산**
```python
distance = sqrt(sum((encoding1[i] - encoding2[i])^2))
```

**이중 임계값 방식**
- tolerance: 얼굴 매칭 허용 거리 (0.3~0.6)
- distance_threshold: 추가 필터링 임계값
- 두 조건 모두 만족 시 인식 성공

**신뢰도 계산**
```python
confidence = max(0, 1 - distance)
```

## 5. 성능 최적화 기법

### 5.1 프레임 처리 최적화
**프레임 스케일링**
- 원본 프레임 축소 후 처리 (기본 0.25배)
- 처리 속도 대폭 향상
- 결과는 원본 크기로 역변환

**프레임 스킵**
- 매 2 프레임마다 얼굴 인식 수행
- 중간 프레임은 이전 결과 재사용
- CPU 부하 50% 감소

### 5.2 부드러운 추적 (Smooth Tracking)
**선형 보간 (Linear Interpolation)**
```python
new_position = old_position + (target_position - old_position) * smoothing_factor
```
- smoothing_factor: 0.2 (0~1 범위)
- 바운딩 박스의 떨림 현상 제거
- 자연스러운 시각적 효과

### 5.3 성능 프리셋

| 모드 | tolerance | upsample | frame_scale | FPS | 감지 거리 | 동시 인원 | GPU |
|------|-----------|----------|-------------|-----|---------|----------|-----|
| 고속 | 0.45 | 0 | 0.25 | 40-60 | 1-2m | 5-8명 | 권장 |
| 균형 | 0.40 | 1 | 0.25 | 30-45 | 2-4m | 8-12명 | 권장 |
| CCTV | 0.35 | 2 | 0.50 | 20-30 | 1-7m | 12-15명 | 필수 |

**YOLO-Face 성능 향상**
- HOG 대비 FPS 2-3배 향상
- GPU 활용 시 최대 5배 향상
- Jetson Nano: CUDA 가속으로 실시간 처리
- CPU 모드도 HOG보다 빠름

## 6. GUI 아키텍처

### 6.1 GUI 프레임워크
**Tkinter**
- Python 기본 내장 GUI 라이브러리
- 크로스 플랫폼 지원
- 경량화된 인터페이스

### 6.2 디자인 패턴
**ScreenManager 패턴**
- 화면 전환 관리 클래스
- 전역 설정 및 데이터베이스 공유
- 5개 독립 화면 구조

**화면 구성**
1. LobbyScreen: 메인 메뉴
2. SettingsScreen: 설정 관리
3. RegisterScreen: 얼굴 등록
4. DatabaseScreen: 데이터 관리
5. RecognitionScreen: 실시간 인식

### 6.3 멀티스레딩
**threading 모듈**
- 비디오 처리와 GUI 분리
- 데몬 스레드로 백그라운드 실행
- 메인 스레드의 응답성 유지

## 7. 다중 얼굴 처리

### 7.1 동시 감지
- 프레임당 최대 10명 감지
- face_locations() 결과 배열 처리
- 각 얼굴마다 독립적 인코딩 및 비교

### 7.2 개별 추적
- 각 얼굴의 위치 좌표 저장
- 프레임 간 위치 보간
- 개별 바운딩 박스 및 라벨 표시

### 7.3 색상 구분
- 등록된 얼굴: 녹색 바운딩 박스 (RGB: 0, 255, 0)
- 미등록 얼굴: 빨간색 바운딩 박스 (RGB: 255, 0, 0)

## 8. 로깅 시스템

### 8.1 중복 방지
**쿨다운 메커니즘**
- 학번별 마지막 로그 시간 저장
- 5초 간격으로 중복 로그 방지
- 딕셔너리 자료구조 활용

### 8.2 로그 데이터
- 인식 시간 (TIMESTAMP)
- 이름 및 학번
- 등록 여부 (1: 등록, 0: 미등록)
- 최근 100개 로그 조회 기능

## 9. 의존성 라이브러리

### 9.1 핵심 라이브러리
```
# 얼굴 인식
face_recognition==1.3.0
dlib==19.24.2

# 딥러닝 (YOLO-Face)
torch>=2.0.0
torchvision>=0.15.0
ultralytics>=8.0.0

# 컴퓨터 비전
opencv-python==4.8.1.78
Pillow==10.1.0
numpy==1.26.4

# 빌드 도구
cmake==3.27.7
```

### 9.2 시스템 요구사항
**최소 사양**
- Python 3.9 이상
- CMake (dlib 컴파일용)
- C++ 컴파일러
- 최소 4GB RAM
- 웹캠 또는 카메라

**권장 사양 (GPU)**
- NVIDIA GPU (CUDA 11.0+)
- 8GB RAM 이상
- Jetson Nano 또는 더 높은 사양

**Jetson Nano 최적화**
- JetPack 4.6+
- CUDA 10.2
- cuDNN 8.2
- PyTorch 1.10+ (ARM64)

## 10. 주요 알고리즘 흐름도

### 10.1 얼굴 등록 프로세스
```
1. 사용자 정보 입력 (이름, 학번, 학과, 학년)
2. 웹캠으로 얼굴 촬영
3. HOG 알고리즘으로 얼굴 감지
4. ResNet 모델로 128차원 인코딩 생성
5. pickle로 직렬화하여 SQLite에 BLOB 저장
```

### 10.2 실시간 인식 프로세스
```
1. 비디오 프레임 캡처 (OpenCV)
2. 프레임 스케일링 (0.25배 축소)
3. RGB 색상 변환
4. YOLO-Face로 얼굴 위치 감지
   - PyTorch 추론
   - GPU 가속 적용
   - 바운딩 박스 좌표 반환
5. 각 얼굴 인코딩 생성 (face_recognition)
6. 데이터베이스의 모든 얼굴과 거리 비교
7. 최소 거리 및 임계값 확인
8. 일치 시 이름 표시, 불일치 시 "Unknown"
9. 바운딩 박스 및 신뢰도 표시
10. 로그 기록 (5초 쿨다운)
```

### 10.3 거리 기반 매칭 알고리즘
```python
for face_encoding in detected_faces:
    distances = face_distance(known_encodings, face_encoding)
    best_match_index = argmin(distances)
    best_distance = distances[best_match_index]
    
    if best_distance <= tolerance and best_distance <= distance_threshold:
        matches = compare_faces([known_encodings[best_match_index]], 
                               face_encoding, 
                               tolerance)
        if matches[0]:
            name = known_names[best_match_index]
            confidence = max(0, 1 - best_distance)
```

---

**작성일**: 2024년 10월 27일  
**작성자**: 임창건  
**프로젝트**: 실시간 얼굴 인식 시스템 v2.1
