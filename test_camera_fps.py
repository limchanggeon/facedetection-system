#!/usr/bin/env python3
"""카메라 실제 FPS 테스트"""
import cv2
import time

print("🎥 카메라 FPS 테스트 시작...")
print("=" * 60)

# 카메라 열기
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ 카메라를 열 수 없습니다!")
    exit(1)

# 설정
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # 버퍼 최소화

# 실제 설정 확인
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps_setting = int(cap.get(cv2.CAP_PROP_FPS))

print(f"📷 카메라 설정:")
print(f"   해상도: {width}x{height}")
print(f"   FPS 설정: {fps_setting}")
print()

# FPS 측정
print("⏱️  FPS 측정 중 (30프레임)...")
frame_count = 0
start_time = time.time()

while frame_count < 30:
    ret, frame = cap.read()
    if not ret:
        print("❌ 프레임 읽기 실패!")
        break
    frame_count += 1

elapsed = time.time() - start_time
actual_fps = frame_count / elapsed

cap.release()

print()
print("=" * 60)
print("📊 결과:")
print(f"   프레임 수: {frame_count}")
print(f"   소요 시간: {elapsed:.2f}초")
print(f"   실제 FPS: {actual_fps:.1f}")
print()

if actual_fps >= 25:
    print("✅ 카메라 성능 좋음 (25+ FPS)")
elif actual_fps >= 15:
    print("⚠️  카메라 성능 보통 (15-25 FPS)")
else:
    print("❌ 카메라 성능 낮음 (<15 FPS)")
    print("   → 카메라 드라이버 또는 하드웨어 문제 가능성")

print()
print("💡 팁:")
if actual_fps < 20:
    print("   - USB 2.0 → USB 3.0 포트로 변경")
    print("   - 다른 프로그램이 카메라 사용 중인지 확인")
    print("   - 카메라 드라이버 업데이트")
