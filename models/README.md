# YOLO-Face 모델 다운로드

## 자동 설치 (권장)
프로그램 실행 시 자동으로 다운로드됩니다.

## 수동 다운로드

### YOLOv8-Face (권장, 최신)

1. 다음 링크에서 모델 다운로드:
   - https://github.com/derronqi/yolov8-face/releases

2. 다음 모델 중 하나 선택:
   - **yolov8n-face.pt** (3MB, 가장 빠름, 권장) ⭐
   - yolov8s-face.pt (11MB, 균형)
   - yolov8m-face.pt (26MB, 정확)

3. 다운로드한 파일을 이 폴더(models/)에 저장

### YOLOv5-Face (호환)

1. 다음 링크에서 모델 다운로드:
   - https://github.com/deepcam-cn/yolov5-face/releases

2. 다음 모델 중 하나 선택:
   - yolov5n-face.pt (2MB, 빠름)
   - yolov5s-face.pt (7MB, 균형)
   - yolov5m-face.pt (21MB, 정확)

## 성능 비교

| 모델 | 크기 | 속도 | 정확도 | 추천 용도 |
|------|------|------|--------|----------|
| yolov8n-face.pt | 3MB | 매우 빠름 | 높음 | 실시간 (권장) ⭐ |
| yolov8s-face.pt | 11MB | 빠름 | 매우 높음 | 고정확도 |
| yolov8m-face.pt | 26MB | 보통 | 최고 | 최고 정확도 |

## 참고
- 모델이 없으면 HOG 방식으로 자동 전환됩니다
- YOLOv8-Face는 HOG보다 3-5배 빠릅니다
- YOLOv8이 YOLOv5보다 더 빠르고 정확합니다
- Jetson Nano에서는 yolov8n-face.pt 권장
