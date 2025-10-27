# 변경 이력 (Changelog)

## [v2.1.0] - 2024-10-27

### 🎉 주요 변경사항

#### 프로젝트 최적화
- ✅ 불필요한 백업 파일 제거 (*.bak, *_backup_*.db)
- ✅ 일회성 마이그레이션 스크립트 제거
- ✅ 중복 문서 정리 (UPDATE_SUMMARY.md, USER_GUIDE.md)
- ✅ .gitignore 업데이트 (백업 파일 및 데이터베이스 제외)

#### 데이터베이스 개선
- ✅ 학생 정보 관리 기능 추가
  - 이름 (name)
  - 학번 (student_id) - 고유 식별자
  - 학과 (department)
  - 학년 (grade)
- ✅ 고유 제약조건 변경: name → student_id
- ✅ 동명이인 지원

#### UI 개선
- ✅ 버튼 텍스트 가시성 개선 (흰색 → 검은색)
- ✅ 모든 화면의 버튼 텍스트 명확하게 표시

### 📝 API 변경사항

#### 수정된 메서드
```python
# 이전
db.add_face(name, encoding)

# 현재
db.add_face(name, student_id, department, grade, encoding)
```

```python
# 이전
db.get_all_faces()
# 반환: {"names": [...], "encodings": [...]}

# 현재
db.get_all_faces()
# 반환: {
#     "names": [...],
#     "student_ids": [...],
#     "departments": [...],
#     "grades": [...],
#     "encodings": [...]
# }
```

```python
# 이전
db.delete_face(name)

# 현재
db.delete_face(student_id)
```

```python
# 이전
db.log_recognition(name, is_registered)

# 현재
db.log_recognition(name, student_id, is_registered)
```

#### 추가된 메서드
```python
db.get_person_info(student_id)
# 반환: {
#     "name": "이름",
#     "student_id": "학번",
#     "department": "학과",
#     "grade": "학년"
# }
```

### 📂 최종 파일 구조

#### 핵심 파일
- `face_recognition_app.py` - v2.0 메인 애플리케이션 (멀티 스크린)
- `face_recognition_gui.py` - v1.0 호환 버전 (단일 화면)
- `gui_screens.py` - v2.0 모든 화면 클래스
- `database.py` - 향상된 데이터베이스 관리자

#### 문서
- `README.md` - 프로젝트 개요 및 시작 가이드
- `MULTI_SCREEN_GUIDE.md` - v2.0 사용 가이드
- `ACCURACY_GUIDE.md` - 정확도 튜닝 가이드
- `JETSON_TUTORIAL.md` - Jetson Nano 설치 가이드
- `WINDOWS_TUTORIAL.md` - Windows 설치 가이드
- `CHANGELOG.md` - 변경 이력 (이 문서)

#### 설정 파일
- `requirements.txt` - Python 의존성
- `.gitignore` - Git 제외 파일
- `LICENSE` - MIT 라이선스

### 🔄 업그레이드 가이드

#### 기존 데이터베이스 마이그레이션
기존 v1.0 데이터베이스를 v2.1로 업그레이드하려면:

1. 데이터베이스 백업
   ```bash
   cp face_recognition.db face_recognition_backup.db
   ```

2. 새로운 스키마로 마이그레이션
   - 기존 사용자는 임시 학번(TEMP0001, TEMP0002...)이 부여됩니다
   - GUI에서 사용자를 삭제하고 실제 정보로 재등록하세요

3. 재등록 방법
   - 로비 → 데이터베이스 관리 → 임시 학번 사용자 삭제
   - 로비 → 얼굴 등록 관리 → 실제 정보(이름, 학번, 학과, 학년)로 등록

---

## [v2.0.0] - 2024-10-27

### 멀티 스크린 GUI 추가
- 5개 화면 구조 (로비, 설정, 등록, 데이터베이스, 인식)
- 카메라 선택 기능
- 성능 프리셋 (고속/균형/CCTV 모드)

### 성능 최적화
- FPS 2배 향상 (10-15 → 25-30)
- 기본 upsample: 2 → 1
- 기본 frame_scale: 0.5 → 0.25

---

## [v1.0.0] - 2024-10-26

### 초기 릴리스
- 실시간 얼굴 인식
- 다중 얼굴 감지 (최대 10명)
- SQLite 데이터베이스
- 단일 화면 GUI
- 거리 기반 인식
- 신뢰도 표시

---

**Last Updated**: 2024-10-27  
**Repository**: https://github.com/limchanggeon/facedetection-system
