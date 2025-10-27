# YOLO-Face 모델 다운로드

## 자동 설치 (권장)
프로그램 실행 시 자동으로 다운로드됩니다.

## 수동 다운로드

YOLOv5-Face 모델을 수동으로 다운로드하려면:

1. 다음 링크에서 모델 다운로드:
   - https://github.com/deepcam-cn/yolov5-face/releases

2. 다음 모델 중 하나 선택:
   - **yolov5n-face.pt** (2MB, 가장 빠름, 권장)
   - yolov5s-face.pt (7MB, 균형)
   - yolov5m-face.pt (21MB, 정확)

3. 다운로드한 파일을 이 폴더(models/)에 저장

## 참고
- 모델이 없으면 HOG 방식으로 자동 전환됩니다
- YOLO-Face는 HOG보다 2-3배 빠릅니다
