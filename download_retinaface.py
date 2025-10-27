#!/usr/bin/env python3
"""
RetinaFace 모델 다운로드 헬퍼 스크립트
"""
import os
import sys
from pathlib import Path

def download_retinaface():
    """RetinaFace 모델 다운로드"""
    
    print("""
╔════════════════════════════════════════════════════════════════╗
║           RetinaFace 모델 다운로드 도구                        ║
╚════════════════════════════════════════════════════════════════╝
    """)
    
    # models 폴더 생성
    model_dir = Path("models")
    model_dir.mkdir(exist_ok=True)
    
    print("📦 의존성 설치 중...")
    print("=" * 60)
    
    # insightface 설치
    try:
        import insightface
        print("✅ insightface가 이미 설치되어 있습니다")
    except ImportError:
        print("⚙️  insightface 설치 중...")
        os.system(f"{sys.executable} -m pip install insightface onnxruntime")
    
    print("\n📥 RetinaFace 모델 다운로드 중...")
    print("=" * 60)
    
    try:
        from insightface.app import FaceAnalysis
        
        # FaceAnalysis 초기화 (모델 자동 다운로드)
        print("ℹ️  모델 다운로드 시작 (약 30-100MB)...")
        app = FaceAnalysis(providers=['CPUExecutionProvider'])
        app.prepare(ctx_id=0, det_size=(640, 640))
        
        print("✅ 모델 다운로드 완료!")
        
        # 모델 파일 위치 확인
        home = Path.home()
        source_models = [
            home / ".insightface" / "models" / "buffalo_l" / "det_10g.onnx",
            home / ".insightface" / "models" / "buffalo_s" / "det_10g.onnx",
        ]
        
        print("\n📂 모델 파일 복사 중...")
        print("=" * 60)
        
        for source in source_models:
            if source.exists():
                dest = model_dir / "retinaface.onnx"
                
                # 파일 복사
                import shutil
                shutil.copy2(source, dest)
                
                size_mb = dest.stat().st_size / (1024 * 1024)
                print(f"✅ 복사 완료: {dest}")
                print(f"   크기: {size_mb:.1f}MB")
                print(f"   원본: {source}")
                
                print("""
╔════════════════════════════════════════════════════════════════╗
║                    🎉 설치 완료!                               ║
╚════════════════════════════════════════════════════════════════╝

✅ RetinaFace 모델이 성공적으로 설치되었습니다!

📍 모델 위치: models/retinaface.onnx

🚀 다음 단계:

   1. 프로그램 실행:
      python face_recognition_app.py
   
   2. 자동으로 RetinaFace 사용됨
   
   3. 콘솔에서 확인:
      [INFO] ✅ RetinaFace 감지기 사용

📊 성능 비교:

   • RetinaFace: 매우 높은 정확도, 작은 얼굴 감지 우수
   • YOLO-Face: 빠른 속도, 실시간 처리
   • HOG: 기본 감지기, 가장 간단함

💡 팁:
   - 정확도 중시: RetinaFace (현재)
   - 속도 중시: YOLO-Face (yolov8n-face.pt 설치)
   - 간단함 중시: HOG (기본 내장)

📖 자세한 가이드: RETINAFACE_GUIDE.md

                """)
                return True
        
        print("❌ 모델 파일을 찾을 수 없습니다")
        print(f"   검색 위치: {home / '.insightface' / 'models'}")
        return False
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        print("\n수동 설치 방법:")
        print("=" * 60)
        print("""
1. Insightface 설치:
   pip install insightface onnxruntime

2. Python으로 모델 다운로드:
   
   python3 << 'EOF'
   from insightface.app import FaceAnalysis
   app = FaceAnalysis(providers=['CPUExecutionProvider'])
   app.prepare(ctx_id=0, det_size=(640, 640))
   EOF

3. 모델 파일 복사:
   
   cp ~/.insightface/models/buffalo_l/det_10g.onnx models/retinaface.onnx

4. 확인:
   
   ls -lh models/retinaface.onnx
        """)
        return False


if __name__ == "__main__":
    try:
        success = download_retinaface()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  사용자에 의해 중단되었습니다")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
