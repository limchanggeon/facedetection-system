#!/usr/bin/env python3
"""
Jetson Nano 최적화 스크립트
GUI, 카메라, 성능 문제 자동 해결
"""
import os
import sys
import subprocess

def check_display():
    """DISPLAY 환경변수 확인 및 설정"""
    print("=" * 60)
    print("1. DISPLAY 환경변수 확인")
    print("=" * 60)
    
    display = os.environ.get('DISPLAY')
    if not display:
        print("⚠️  DISPLAY 환경변수가 설정되지 않았습니다")
        print("✅ 자동으로 :0으로 설정합니다")
        os.environ['DISPLAY'] = ':0'
        display = ':0'
    
    print(f"✅ DISPLAY={display}")
    return True

def check_camera():
    """카메라 장치 확인"""
    print("\n" + "=" * 60)
    print("2. 카메라 장치 확인")
    print("=" * 60)
    
    try:
        result = subprocess.run(['v4l2-ctl', '--list-devices'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ 감지된 카메라:")
            print(result.stdout)
        else:
            print("⚠️  v4l2-ctl 명령어를 찾을 수 없습니다")
            print("   설치: sudo apt-get install v4l-utils")
    except FileNotFoundError:
        print("⚠️  v4l2-ctl이 설치되지 않았습니다")
        print("   설치: sudo apt-get install v4l-utils")
    except Exception as e:
        print(f"⚠️  오류: {e}")
    
    # /dev/video* 확인
    video_devices = []
    for i in range(10):
        dev = f"/dev/video{i}"
        if os.path.exists(dev):
            video_devices.append(dev)
    
    if video_devices:
        print(f"\n✅ 발견된 비디오 장치: {', '.join(video_devices)}")
    else:
        print("\n⚠️  /dev/video* 장치를 찾을 수 없습니다")
    
    return True

def optimize_jetson():
    """Jetson Nano 성능 최적화"""
    print("\n" + "=" * 60)
    print("3. Jetson Nano 성능 최적화")
    print("=" * 60)
    
    try:
        # 현재 전력 모드 확인
        result = subprocess.run(['sudo', 'nvpmodel', '-q'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("현재 전력 모드:")
            print(result.stdout)
    except Exception as e:
        print(f"⚠️  nvpmodel 확인 실패: {e}")
    
    print("\n권장 설정:")
    print("  1. 최대 성능 모드 (5W → 10W):")
    print("     sudo nvpmodel -m 0")
    print("  2. GPU 클럭 최대화:")
    print("     sudo jetson_clocks")
    print("  3. 스왑 메모리 확인:")
    print("     free -h")
    
    return True

def create_jetson_launcher():
    """Jetson용 실행 스크립트 생성"""
    print("\n" + "=" * 60)
    print("4. Jetson용 실행 스크립트 생성")
    print("=" * 60)
    
    launcher_content = '''#!/bin/bash
# Jetson Nano 얼굴 인식 시스템 실행 스크립트

echo "========================================"
echo "  Jetson Nano 얼굴 인식 시스템 시작"
echo "========================================"

# DISPLAY 환경변수 설정
export DISPLAY=:0

# 가상환경 활성화
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "✅ 가상환경 활성화"
else
    echo "⚠️  가상환경을 찾을 수 없습니다"
    echo "   python3 -m venv .venv 로 생성하세요"
    exit 1
fi

# PyTorch 버전 확인
echo ""
echo "환경 확인 중..."
python3 << 'PYEOF'
import sys
try:
    import torch
    print(f"✅ PyTorch: {torch.__version__}")
    print(f"✅ CUDA 사용 가능: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"✅ CUDA 장치: {torch.cuda.get_device_name(0)}")
except ImportError:
    print("⚠️  PyTorch가 설치되지 않았습니다")
    
try:
    import cv2
    print(f"✅ OpenCV: {cv2.__version__}")
except ImportError:
    print("⚠️  OpenCV가 설치되지 않았습니다")
    
try:
    import face_recognition
    print("✅ face_recognition 설치됨")
except ImportError:
    print("⚠️  face_recognition이 설치되지 않았습니다")
PYEOF

echo ""
echo "프로그램 시작..."
echo ""

# 프로그램 실행
python3 face_recognition_app.py

echo ""
echo "프로그램 종료"
'''
    
    with open('run_jetson.sh', 'w') as f:
        f.write(launcher_content)
    
    # 실행 권한 부여
    os.chmod('run_jetson.sh', 0o755)
    
    print("✅ run_jetson.sh 생성 완료")
    print("\n사용법:")
    print("  ./run_jetson.sh")
    
    return True

def create_camera_test():
    """카메라 테스트 스크립트 생성"""
    print("\n" + "=" * 60)
    print("5. 카메라 테스트 스크립트 생성")
    print("=" * 60)
    
    test_content = '''#!/usr/bin/env python3
"""
Jetson Nano 카메라 테스트
"""
import cv2
import sys

def test_camera(camera_index=0):
    print(f"카메라 {camera_index} 테스트 중...")
    
    # GStreamer 파이프라인 (Jetson 최적화)
    gst_pipeline = (
        f"v4l2src device=/dev/video{camera_index} ! "
        "video/x-raw, width=640, height=480, framerate=30/1 ! "
        "videoconvert ! appsink"
    )
    
    # 일반 OpenCV 방식
    cap_normal = cv2.VideoCapture(camera_index)
    
    # GStreamer 방식 시도
    try:
        cap_gst = cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)
        if cap_gst.isOpened():
            print("✅ GStreamer 파이프라인 사용 가능")
            cap = cap_gst
        else:
            print("⚠️  GStreamer 사용 불가, 일반 모드 사용")
            cap = cap_normal
    except:
        print("⚠️  GStreamer 초기화 실패, 일반 모드 사용")
        cap = cap_normal
    
    if not cap.isOpened():
        print(f"❌ 카메라 {camera_index}를 열 수 없습니다")
        return False
    
    # 해상도 설정
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    # 실제 해상도 확인
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    
    print(f"✅ 카메라 열림")
    print(f"   해상도: {width}x{height}")
    print(f"   FPS: {fps}")
    print("")
    print("ESC 키를 눌러 종료하세요")
    
    import time
    frame_count = 0
    start_time = time.time()
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ 프레임을 읽을 수 없습니다")
            break
        
        frame_count += 1
        elapsed = time.time() - start_time
        
        if elapsed >= 1.0:
            actual_fps = frame_count / elapsed
            cv2.putText(frame, f"FPS: {actual_fps:.1f}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            frame_count = 0
            start_time = time.time()
        
        cv2.putText(frame, f"Camera {camera_index}: {width}x{height}", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.imshow(f'Camera Test - {camera_index}', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("\\n✅ 테스트 완료")
    return True

if __name__ == "__main__":
    camera_index = 0
    if len(sys.argv) > 1:
        camera_index = int(sys.argv[1])
    
    test_camera(camera_index)
'''
    
    with open('test_camera_jetson.py', 'w') as f:
        f.write(test_content)
    
    os.chmod('test_camera_jetson.py', 0o755)
    
    print("✅ test_camera_jetson.py 생성 완료")
    print("\n사용법:")
    print("  python3 test_camera_jetson.py [카메라번호]")
    print("  예: python3 test_camera_jetson.py 0")
    
    return True

def print_recommendations():
    """권장 사항 출력"""
    print("\n" + "=" * 60)
    print("📋 Jetson Nano 최적화 권장 사항")
    print("=" * 60)
    
    print("""
1️⃣  성능 모드 설정 (필수):
   sudo nvpmodel -m 0        # 10W 최대 성능 모드
   sudo jetson_clocks        # 클럭 최대화

2️⃣  스왑 메모리 확대 (권장):
   sudo fallocate -l 4G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile

3️⃣  카메라 최적화:
   - USB 카메라 사용 시 USB 3.0 포트 사용
   - 해상도 640x480 권장 (480p)
   - FPS 15-30 설정

4️⃣  YOLO 모델 최적화:
   - yolov8n-face.pt 사용 (가장 가벼움)
   - CUDA 활성화 확인
   - TensorRT 변환 고려 (고급)

5️⃣  프로그램 설정:
   - 고속 모드 사용 (upsample=0, scale=0.25)
   - 프레임 처리 간격 늘리기 (3-5 프레임)
   - 동시 인식 인원 제한 (3-5명)

6️⃣  GUI 문제 해결:
   export DISPLAY=:0
   ./run_jetson.sh

7️⃣  모니터링:
   sudo tegrastats           # GPU/CPU 사용률 확인
   htop                      # 메모리 사용률 확인
""")

def main():
    print("=" * 60)
    print("  Jetson Nano 얼굴 인식 시스템 최적화")
    print("=" * 60)
    print()
    
    check_display()
    check_camera()
    optimize_jetson()
    create_jetson_launcher()
    create_camera_test()
    print_recommendations()
    
    print("\n" + "=" * 60)
    print("✅ 최적화 완료!")
    print("=" * 60)
    print("\n다음 단계:")
    print("1. 성능 모드 설정: sudo nvpmodel -m 0 && sudo jetson_clocks")
    print("2. 카메라 테스트: python3 test_camera_jetson.py")
    print("3. 프로그램 실행: ./run_jetson.sh")
    print()

if __name__ == "__main__":
    main()
