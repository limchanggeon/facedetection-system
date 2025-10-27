"""
멀티 화면 GUI를 위한 화면 관리 클래스들
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import cv2
from PIL import Image, ImageTk, ImageDraw, ImageFont
import face_recognition
import threading
import time
import numpy as np
import queue
from database import FaceDatabase
from yolo_face_detector import YOLOFaceDetector

class ScreenManager:
    """화면 전환을 관리하는 클래스"""
    def __init__(self, root):
        self.root = root
        self.current_screen = None
        self.screens = {}
        self.db = FaceDatabase()
        
        # 전역 설정
        self.settings = {
            'camera_index': 0,
            'tolerance': 0.45,
            'distance_threshold': 0.50,
            'upsample_times': 1,
            'frame_scale': 0.25,
            'show_confidence': True
        }
        
    def show_screen(self, screen_name):
        """화면 전환"""
        if self.current_screen:
            self.current_screen.pack_forget()
        
        if screen_name not in self.screens:
            if screen_name == 'lobby':
                self.screens[screen_name] = LobbyScreen(self.root, self)
            elif screen_name == 'settings':
                self.screens[screen_name] = SettingsScreen(self.root, self)
            elif screen_name == 'register':
                self.screens[screen_name] = RegisterScreen(self.root, self)
            elif screen_name == 'recognition':
                self.screens[screen_name] = RecognitionScreen(self.root, self)
            elif screen_name == 'database':
                self.screens[screen_name] = DatabaseScreen(self.root, self)
        
        self.current_screen = self.screens[screen_name]
        self.current_screen.pack(fill=tk.BOTH, expand=True)
        if hasattr(self.current_screen, 'on_show'):
            self.current_screen.on_show()


class LobbyScreen(tk.Frame):
    """로비(메인 메뉴) 화면"""
    def __init__(self, parent, manager):
        super().__init__(parent, bg="#2c3e50")
        self.manager = manager
        self.setup_ui()
    
    def setup_ui(self):
        # 타이틀
        title_frame = tk.Frame(self, bg="#2c3e50")
        title_frame.pack(pady=50)
        
        tk.Label(
            title_frame,
            text="실시간 얼굴 인식 시스템",
            font=("Arial", 36, "bold"),
            bg="#2c3e50",
            fg="black"
        ).pack()
        
        tk.Label(
            title_frame,
            text="Face Recognition System v2.0",
            font=("Arial", 14),
            bg="#2c3e50",
            fg="#bdc3c7"
        ).pack(pady=10)
        
        # 버튼 프레임
        button_frame = tk.Frame(self, bg="#2c3e50")
        button_frame.pack(pady=30)
        
        buttons = [
            ("얼굴 인식 시작", "recognition", "#27ae60"),
            ("얼굴 등록 관리", "register", "#3498db"),
            ("데이터베이스 관리", "database", "#f39c12"),
            ("환경 설정", "settings", "#9b59b6"),
        ]
        
        row = 0
        col = 0
        for text, screen, color in buttons:
            btn = tk.Button(
                button_frame,
                text=text,
                command=lambda s=screen: self.manager.show_screen(s),
                bg=color,
                fg="black",
                font=("Arial", 16, "bold"),
                width=20,
                height=3,
                cursor="hand2",
                relief=tk.RAISED,
                bd=3,
                activebackground=color,
                activeforeground="black"
            )
            btn.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
            
            col += 1
            if col > 1:
                col = 0
                row += 1
        
        # 통계 정보
        stats_frame = tk.Frame(self, bg="#34495e", relief=tk.RAISED, bd=2)
        stats_frame.pack(pady=30, padx=50, fill=tk.X)
        
        registered_count = self.manager.db.get_registered_count()
        
        tk.Label(
            stats_frame,
            text=f"등록된 얼굴: {registered_count}명",
            font=("Arial", 14, "bold"),
            bg="#34495e",
            fg="black",
            pady=15
        ).pack()
        
        # 푸터
        footer_frame = tk.Frame(self, bg="#2c3e50")
        footer_frame.pack(side=tk.BOTTOM, pady=20)
        
        tk.Label(
            footer_frame,
            text="Lim Changgeon | MIT License",
            font=("Arial", 10),
            bg="#2c3e50",
            fg="#7f8c8d"
        ).pack()
    
    def on_show(self):
        """🔔 화면이 표시될 때 통계 갱신"""
        # 통계 정보 프레임 찾기
        for widget in self.winfo_children():
            if isinstance(widget, tk.Frame) and widget.cget('bg') == "#34495e":
                for label in widget.winfo_children():
                    if isinstance(label, tk.Label) and "등록된 얼굴" in label.cget('text'):
                        registered_count = self.manager.db.get_registered_count()
                        label.config(text=f"등록된 얼굴: {registered_count}명")
                        break
                break


class SettingsScreen(tk.Frame):
    """환경 설정 화면"""
    def __init__(self, parent, manager):
        super().__init__(parent, bg="#ecf0f1")
        self.manager = manager
        self.setup_ui()
    
    def setup_ui(self):
        # 헤더
        header = tk.Frame(self, bg="#34495e", height=80)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="환경 설정",
            font=("Arial", 24, "bold"),
            bg="#34495e",
            fg="black"
        ).pack(side=tk.LEFT, padx=20, pady=20)
        
        tk.Button(
            header,
            text="< 뒤로 가기",
            command=lambda: self.manager.show_screen('lobby'),
            bg="#7f8c8d",
            fg="black",
            font=("Arial", 12, "bold"),
            cursor="hand2",
            width=12,
            height=2,
            relief=tk.RAISED,
            bd=2
        ).pack(side=tk.RIGHT, padx=20, pady=15)
        
        # 스크롤 가능한 컨텐츠
        canvas = tk.Canvas(self, bg="#ecf0f1", highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#ecf0f1")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 카메라 설정
        camera_frame = tk.LabelFrame(
            scrollable_frame,
            text=" 카메라 설정 ",
            font=("Arial", 16, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50",
            padx=20,
            pady=20
        )
        camera_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(
            camera_frame,
            text="사용할 카메라를 선택하세요:",
            font=("Arial", 12),
            bg="#ecf0f1"
        ).pack(anchor=tk.W, pady=5)
        
        self.camera_var = tk.IntVar(value=self.manager.settings['camera_index'])
        
        cameras = [
            ("카메라 0 - 노트북 내장 카메라", 0),
            ("카메라 1 - 외장 USB 카메라", 1),
            ("카메라 2 - 외장 USB 카메라", 2),
        ]
        
        for text, value in cameras:
            tk.Radiobutton(
                camera_frame,
                text=text,
                variable=self.camera_var,
                value=value,
                font=("Arial", 11),
                bg="#ecf0f1",
                command=self.test_camera
            ).pack(anchor=tk.W, padx=20, pady=5)
        
        tk.Button(
            camera_frame,
            text="카메라 테스트",
            command=self.test_camera,
            bg="#3498db",
            fg="black",
            font=("Arial", 12, "bold"),
            cursor="hand2",
            width=15,
            height=2,
            relief=tk.RAISED,
            bd=2
        ).pack(pady=10)
        
        self.camera_status = tk.Label(
            camera_frame,
            text="",
            font=("Arial", 10),
            bg="#ecf0f1",
            fg="#27ae60"
        )
        self.camera_status.pack()
        
        # 얼굴 감지기 설정 ⭐ NEW
        detector_frame = tk.LabelFrame(
            scrollable_frame,
            text=" 얼굴 감지 엔진 선택 ",
            font=("Arial", 16, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50",
            padx=20,
            pady=20
        )
        detector_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(
            detector_frame,
            text="사용할 얼굴 감지 엔진을 선택하세요:",
            font=("Arial", 12),
            bg="#ecf0f1"
        ).pack(anchor=tk.W, pady=5)
        
        # 현재 사용 가능한 감지기 확인
        available_detectors = self._check_available_detectors()
        
        # 기본값 설정 (설정에 없으면 'auto')
        if 'detector_type' not in self.manager.settings:
            self.manager.settings['detector_type'] = 'auto'
        
        self.detector_var = tk.StringVar(value=self.manager.settings['detector_type'])
        
        # 감지기 옵션
        detectors = [
            ("자동 선택 (RetinaFace → YOLO → HOG)", "auto", "🤖"),
            ("RetinaFace (최고 정확도, 작은 얼굴)", "retinaface", "🏆"),
            ("YOLO-Face (최고 속도, GPU 가속)", "yolo", "⚡"),
            ("HOG (기본 내장, 간단함)", "hog", "🔧"),
        ]
        
        for text, value, emoji in detectors:
            # 사용 가능한지 확인
            if value == 'auto' or value in available_detectors:
                status = "✅"
            else:
                status = "❌"
            
            radio = tk.Radiobutton(
                detector_frame,
                text=f"{emoji} {text} {status}",
                variable=self.detector_var,
                value=value,
                font=("Arial", 11),
                bg="#ecf0f1",
                state=tk.NORMAL if (value == 'auto' or value in available_detectors) else tk.DISABLED
            )
            radio.pack(anchor=tk.W, padx=20, pady=5)
        
        # 현재 감지기 상태 표시
        self.detector_status = tk.Label(
            detector_frame,
            text="",
            font=("Arial", 10, "bold"),
            bg="#ecf0f1",
            fg="#2980b9"
        )
        self.detector_status.pack(pady=10)
        self._update_detector_status()
        
        # 설치 안내
        install_info = tk.Frame(detector_frame, bg="#ecf0f1")
        install_info.pack(fill=tk.X, pady=10)
        
        tk.Label(
            install_info,
            text="💡 설치 방법:",
            font=("Arial", 10, "bold"),
            bg="#ecf0f1",
            fg="#7f8c8d"
        ).pack(anchor=tk.W)
        
        if 'retinaface' not in available_detectors:
            tk.Label(
                install_info,
                text="  • RetinaFace: python download_retinaface.py",
                font=("Arial", 9),
                bg="#ecf0f1",
                fg="#7f8c8d"
            ).pack(anchor=tk.W)
        
        if 'yolo' not in available_detectors:
            tk.Label(
                install_info,
                text="  • YOLO-Face: models/README.md 참조",
                font=("Arial", 9),
                bg="#ecf0f1",
                fg="#7f8c8d"
            ).pack(anchor=tk.W)
        
        # 성능 프리셋
        preset_frame = tk.LabelFrame(
            scrollable_frame,
            text=" 성능 프리셋 (권장) ",
            font=("Arial", 16, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50",
            padx=20,
            pady=20
        )
        preset_frame.pack(fill=tk.X, padx=20, pady=10)
        
        presets = [
            ("고속 모드 (25-30 FPS, 가까운 거리)", "fast", "#27ae60"),
            ("균형 모드 (18-22 FPS, 중거리)", "balanced", "#3498db"),
            ("CCTV 모드 (10-15 FPS, 원거리)", "cctv", "#e74c3c"),
        ]
        
        for text, mode, color in presets:
            tk.Button(
                preset_frame,
                text=text,
                command=lambda m=mode: self.apply_preset(m),
                bg=color,
                fg="black",
                font=("Arial", 12, "bold"),
                cursor="hand2",
                height=2,
                relief=tk.RAISED,
                bd=2,
                activebackground=color,
                activeforeground="black"
            ).pack(fill=tk.X, pady=5)
        
        # 고급 설정
        advanced_frame = tk.LabelFrame(
            scrollable_frame,
            text=" 고급 설정 (수동 조절) ",
            font=("Arial", 16, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50",
            padx=20,
            pady=20
        )
        advanced_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Tolerance
        tk.Label(
            advanced_frame,
            text="매칭 엄격도 (낮을수록 엄격):",
            font=("Arial", 11, "bold"),
            bg="#ecf0f1"
        ).pack(anchor=tk.W, pady=5)
        
        self.tolerance_var = tk.DoubleVar(value=self.manager.settings['tolerance'])
        self.tolerance_scale = tk.Scale(
            advanced_frame,
            from_=0.3,
            to=0.6,
            resolution=0.05,
            orient=tk.HORIZONTAL,
            variable=self.tolerance_var,
            bg="#ecf0f1",
            length=400
        )
        self.tolerance_scale.pack(fill=tk.X, pady=5)
        
        # Upsample
        tk.Label(
            advanced_frame,
            text="원거리 감도 (높을수록 먼 얼굴 탐지):",
            font=("Arial", 11, "bold"),
            bg="#ecf0f1"
        ).pack(anchor=tk.W, pady=5)
        
        self.upsample_var = tk.IntVar(value=self.manager.settings['upsample_times'])
        self.upsample_scale = tk.Scale(
            advanced_frame,
            from_=0,
            to=2,
            resolution=1,
            orient=tk.HORIZONTAL,
            variable=self.upsample_var,
            bg="#ecf0f1",
            length=400
        )
        self.upsample_scale.pack(fill=tk.X, pady=5)
        
        # 신뢰도 표시
        self.confidence_var = tk.BooleanVar(value=self.manager.settings['show_confidence'])
        tk.Checkbutton(
            advanced_frame,
            text="신뢰도 표시 (얼굴 옆에 %로 표시)",
            variable=self.confidence_var,
            font=("Arial", 11),
            bg="#ecf0f1"
        ).pack(anchor=tk.W, pady=10)
        
        # 저장 버튼
        tk.Button(
            scrollable_frame,
            text="설정 저장하기",
            command=self.save_settings,
            bg="#27ae60",
            fg="black",
            font=("Arial", 16, "bold"),
            cursor="hand2",
            height=3,
            relief=tk.RAISED,
            bd=3,
            activebackground="#27ae60",
            activeforeground="black"
        ).pack(fill=tk.X, padx=20, pady=20)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def _check_available_detectors(self):
        """사용 가능한 감지기 확인"""
        available = []
        
        # RetinaFace 확인
        try:
            from pathlib import Path
            retinaface_model = Path("models/retinaface.onnx")
            if retinaface_model.exists() and retinaface_model.stat().st_size > 1000000:
                available.append('retinaface')
        except:
            pass
        
        # YOLO-Face 확인
        try:
            from pathlib import Path
            yolo_models = [
                Path("models/yolov8n-face.pt"),
                Path("models/yolov8s-face.pt"),
                Path("models/yolov8m-face.pt"),
                Path("models/yolov5n-face.pt"),
                Path("models/yolov5s-face.pt"),
            ]
            if any(m.exists() and m.stat().st_size > 1000000 for m in yolo_models):
                available.append('yolo')
        except:
            pass
        
        # HOG는 항상 사용 가능
        available.append('hog')
        
        return available
    
    def _update_detector_status(self):
        """현재 감지기 상태 업데이트"""
        detector_type = self.detector_var.get()
        
        if detector_type == 'auto':
            # 자동 선택 시 실제 사용될 감지기 표시
            available = self._check_available_detectors()
            if 'retinaface' in available:
                actual = "RetinaFace 🏆"
            elif 'yolo' in available:
                actual = "YOLO-Face ⚡"
            else:
                actual = "HOG 🔧"
            self.detector_status.config(text=f"현재 감지기: 자동 선택 → {actual}")
        elif detector_type == 'retinaface':
            self.detector_status.config(text="현재 감지기: RetinaFace 🏆 (최고 정확도)")
        elif detector_type == 'yolo':
            self.detector_status.config(text="현재 감지기: YOLO-Face ⚡ (최고 속도)")
        elif detector_type == 'hog':
            self.detector_status.config(text="현재 감지기: HOG 🔧 (기본)")
    
    def test_camera(self):
        """카메라 테스트"""
        camera_index = self.camera_var.get()
        cap = cv2.VideoCapture(camera_index)
        
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                height, width = frame.shape[:2]
                self.camera_status.config(
                    text=f"카메라 {camera_index} 사용 가능 ({width}x{height})",
                    fg="#27ae60"
                )
            else:
                self.camera_status.config(
                    text=f"카메라 {camera_index}에서 프레임을 읽을 수 없습니다",
                    fg="#e67e22"
                )
            cap.release()
        else:
            self.camera_status.config(
                text=f"카메라 {camera_index}를 열 수 없습니다",
                fg="#e74c3c"
            )
    
    def apply_preset(self, mode):
        """프리셋 적용"""
        presets = {
            'fast': {
                'tolerance': 0.45,
                'upsample_times': 0,
                'frame_scale': 0.25,
                'name': '고속 모드'
            },
            'balanced': {
                'tolerance': 0.40,
                'upsample_times': 1,
                'frame_scale': 0.25,
                'name': '균형 모드'
            },
            'cctv': {
                'tolerance': 0.35,
                'upsample_times': 2,
                'frame_scale': 0.5,
                'name': 'CCTV 모드'
            }
        }
        
        preset = presets[mode]
        self.tolerance_var.set(preset['tolerance'])
        self.upsample_var.set(preset['upsample_times'])
        self.manager.settings['frame_scale'] = preset['frame_scale']
        
        messagebox.showinfo("프리셋 적용", f"{preset['name']}가 적용되었습니다!\n\n설정을 저장하려면 '설정 저장하기' 버튼을 클릭하세요.")
    
    def save_settings(self):
        """설정 저장"""
        self.manager.settings['camera_index'] = self.camera_var.get()
        self.manager.settings['tolerance'] = self.tolerance_var.get()
        self.manager.settings['distance_threshold'] = self.tolerance_var.get() + 0.05
        self.manager.settings['upsample_times'] = self.upsample_var.get()
        self.manager.settings['show_confidence'] = self.confidence_var.get()
        self.manager.settings['detector_type'] = self.detector_var.get()
        
        # 감지기 상태 업데이트
        self._update_detector_status()
        
        messagebox.showinfo("저장 완료", "설정이 저장되었습니다!")
        print(f"[INFO] 설정 저장: {self.manager.settings}")


class RegisterScreen(tk.Frame):
    """얼굴 등록 화면"""
    def __init__(self, parent, manager):
        super().__init__(parent, bg="#ecf0f1")
        self.manager = manager
        
        # 🔔 감지기 초기화 (RecognitionScreen과 동일)
        self.detector = None
        self.detector_type = "HOG"
        self._initialize_detector()
        
        self.setup_ui()
    
    def _initialize_detector(self):
        """사용자 설정에 따라 감지기 초기화 (RecognitionScreen과 동일)"""
        if 'detector_type' not in self.manager.settings:
            self.manager.settings['detector_type'] = 'auto'
        
        detector_choice = self.manager.settings['detector_type']
        
        if detector_choice == 'retinaface':
            if self._try_init_retinaface():
                return
        elif detector_choice == 'yolo':
            if self._try_init_yolo():
                return
        elif detector_choice == 'hog':
            self.detector_type = "HOG"
            return
        
        # 'auto' 모드 또는 선택한 감지기 사용 불가 시 자동 선택
        if self._try_init_retinaface():
            return
        if self._try_init_yolo():
            return
        
        self.detector_type = "HOG"
    
    def _try_init_retinaface(self):
        try:
            from retinaface_detector import RetinaFaceDetector
            self.detector = RetinaFaceDetector(conf_threshold=0.5)
            self.detector_type = "RetinaFace"
            return True
        except:
            return False
    
    def _try_init_yolo(self):
        try:
            from yolo_face_detector import YOLOFaceDetector
            self.detector = YOLOFaceDetector(conf_threshold=0.3)
            self.detector_type = "YOLO-Face"
            return True
        except:
            return False
    
    def setup_ui(self):
        # 헤더
        header = tk.Frame(self, bg="#34495e", height=80)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="얼굴 등록 관리",
            font=("Arial", 24, "bold"),
            bg="#34495e",
            fg="black"
        ).pack(side=tk.LEFT, padx=20, pady=20)
        
        tk.Button(
            header,
            text="< 뒤로 가기",
            command=lambda: self.manager.show_screen('lobby'),
            bg="#7f8c8d",
            fg="black",
            font=("Arial", 12, "bold"),
            cursor="hand2",
            width=12,
            height=2,
            relief=tk.RAISED,
            bd=2
        ).pack(side=tk.RIGHT, padx=20, pady=15)
        
        # 메인 컨텐츠
        main_frame = tk.Frame(self, bg="#ecf0f1")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 등록 버튼
        tk.Button(
            main_frame,
            text="새 얼굴 등록하기",
            command=self.register_new_face,
            bg="#27ae60",
            fg="black",
            font=("Arial", 18, "bold"),
            cursor="hand2",
            height=3,
            relief=tk.RAISED,
            bd=3,
            activebackground="#27ae60",
            activeforeground="black"
        ).pack(fill=tk.X, pady=10)
        
        # 안내 메시지
        info_frame = tk.Frame(main_frame, bg="#3498db", relief=tk.RAISED, bd=2)
        info_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            info_frame,
            text="[ 등록 방법 ]\n\n1. 이름을 입력하세요\n2. 카메라를 보고 스페이스바를 누르세요\n3. ESC를 누르면 취소됩니다",
            font=("Arial", 13),
            bg="#3498db",
            fg="black",
            justify=tk.LEFT,
            padx=20,
            pady=15
        ).pack()
        
        # 통계
        self.stats_label = tk.Label(
            main_frame,
            text="",
            font=("Arial", 14, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50"
        )
        self.stats_label.pack(pady=10)
        
        self.update_stats()
    
    def on_show(self):
        """화면이 표시될 때"""
        self.update_stats()
    
    def update_stats(self):
        """통계 업데이트"""
        count = self.manager.db.get_registered_count()
        self.stats_label.config(text=f"현재 등록된 얼굴: {count}명")
    
    def register_new_face(self):
        """새 얼굴 등록"""
        # 학생 정보 입력 받기
        name = simpledialog.askstring("이름 입력", "등록할 사람의 이름을 입력하세요:")
        if not name:
            return
        
        student_id = simpledialog.askstring("학번 입력", "학번을 입력하세요:")
        if not student_id:
            return
        
        department = simpledialog.askstring("학과 입력", "학과를 입력하세요:")
        if not department:
            return
        
        grade = simpledialog.askstring("학년 입력", "학년을 입력하세요 (예: 1, 2, 3, 4):")
        if not grade:
            return
        
        # 이미 등록된 학번인지 확인
        known_faces = self.manager.db.get_all_faces()
        if student_id in known_faces["student_ids"]:
            messagebox.showerror("오류", f"학번 '{student_id}'은(는) 이미 등록되어 있습니다.")
            return
        
        # 웹캠 열기
        camera_index = self.manager.settings['camera_index']
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            messagebox.showerror("오류", f"카메라 {camera_index}를 열 수 없습니다.\n환경 설정에서 카메라를 확인하세요.")
            return
        
        messagebox.showinfo("안내", "카메라를 보고 스페이스바를 눌러 사진을 촬영하세요.\nESC를 누르면 취소됩니다.")
        
        encoding = None
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # 화면에 표시
            display_frame = frame.copy()
            cv2.putText(
                display_frame,
                f"Registering: {name}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )
            cv2.putText(
                display_frame,
                "SPACE: Capture | ESC: Cancel",
                (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )
            
            cv2.imshow("Face Registration", display_frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == 27:  # ESC
                break
            elif key == 32:  # SPACE
                # 🔔 얼굴 감지 및 인코딩 (설정된 감지기 사용)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # RecognitionScreen과 동일한 감지기 사용
                try:
                    if self.detector and self.detector_type != "HOG":
                        # 🔔 RetinaFace/YOLO는 upsample_times 불필요
                        face_locations = self.detector.detect_faces(rgb_frame)
                    else:
                        face_locations = face_recognition.face_locations(
                            rgb_frame,
                            model="hog",
                            number_of_times_to_upsample=self.manager.settings.get('upsample_times', 1)
                        )
                except Exception as e:
                    print(f"[ERROR] 얼굴 감지 오류: {e}")
                    messagebox.showerror("오류", f"얼굴 감지 실패: {e}")
                    continue
                
                if len(face_locations) == 0:
                    messagebox.showwarning("경고", "얼굴을 감지할 수 없습니다. 다시 시도하세요.")
                    continue
                elif len(face_locations) > 1:
                    messagebox.showwarning("경고", "여러 얼굴이 감지되었습니다. 한 명만 촬영하세요.")
                    continue
                
                # 얼굴 인코딩 생성
                face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
                encoding = face_encodings[0]
                
                messagebox.showinfo("성공", f"'{name}'의 얼굴이 촬영되었습니다!")
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        # 데이터베이스에 저장
        if encoding is not None:
            if self.manager.db.add_face(name, student_id, department, grade, encoding):
                messagebox.showinfo("성공", f"'{name}' (학번: {student_id})이(가) 성공적으로 등록되었습니다!")
                self.update_stats()
            else:
                messagebox.showerror("오류", "얼굴 등록에 실패했습니다.")


class DatabaseScreen(tk.Frame):
    """데이터베이스 관리 화면"""
    def __init__(self, parent, manager):
        super().__init__(parent, bg="#ecf0f1")
        self.manager = manager
        self.setup_ui()
    
    def setup_ui(self):
        # 헤더
        header = tk.Frame(self, bg="#34495e", height=80)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="데이터베이스 관리",
            font=("Arial", 24, "bold"),
            bg="#34495e",
            fg="black"
        ).pack(side=tk.LEFT, padx=20, pady=20)
        
        tk.Button(
            header,
            text="< 뒤로 가기",
            command=lambda: self.manager.show_screen('lobby'),
            bg="#7f8c8d",
            fg="black",
            font=("Arial", 12, "bold"),
            cursor="hand2",
            width=12,
            height=2,
            relief=tk.RAISED,
            bd=2
        ).pack(side=tk.RIGHT, padx=20, pady=15)
        
        # 메인 컨텐츠
        main_frame = tk.Frame(self, bg="#ecf0f1")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 통계
        stats_frame = tk.LabelFrame(
            main_frame,
            text=" 통계 ",
            font=("Arial", 14, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50",
            padx=20,
            pady=20
        )
        stats_frame.pack(fill=tk.X, pady=10)
        
        self.stats_text = tk.Label(
            stats_frame,
            text="",
            font=("Arial", 12),
            bg="#ecf0f1",
            justify=tk.LEFT
        )
        self.stats_text.pack()
        
        # 등록된 얼굴 목록
        list_frame = tk.LabelFrame(
            main_frame,
            text=" 등록된 얼굴 목록 ",
            font=("Arial", 14, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50"
        )
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 리스트박스와 스크롤바
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.face_listbox = tk.Listbox(
            list_frame,
            font=("Arial", 12),
            yscrollcommand=scrollbar.set,
            selectmode=tk.SINGLE,
            height=15
        )
        self.face_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.config(command=self.face_listbox.yview)
        
        # 버튼 프레임
        button_frame = tk.Frame(main_frame, bg="#ecf0f1")
        button_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(
            button_frame,
            text="새로고침",
            command=self.refresh_data,
            bg="#3498db",
            fg="black",
            font=("Arial", 12, "bold"),
            cursor="hand2",
            width=15,
            height=2,
            relief=tk.RAISED,
            bd=2
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="선택 삭제",
            command=self.delete_selected,
            bg="#e74c3c",
            fg="black",
            font=("Arial", 12, "bold"),
            cursor="hand2",
            width=15,
            height=2,
            relief=tk.RAISED,
            bd=2
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="인식 로그",
            command=self.show_logs,
            bg="#f39c12",
            fg="black",
            font=("Arial", 12, "bold"),
            cursor="hand2",
            width=15,
            height=2,
            relief=tk.RAISED,
            bd=2
        ).pack(side=tk.LEFT, padx=5)
        
        self.refresh_data()
    
    def on_show(self):
        """화면이 표시될 때"""
        self.refresh_data()
    
    def refresh_data(self):
        """데이터 새로고침"""
        # 통계 업데이트
        count = self.manager.db.get_registered_count()
        self.stats_text.config(text=f"등록된 얼굴: {count}명")
        
        # 목록 업데이트
        self.face_listbox.delete(0, tk.END)
        known_faces = self.manager.db.get_all_faces()
        for i in range(len(known_faces["names"])):
            name = known_faces["names"][i]
            student_id = known_faces["student_ids"][i]
            department = known_faces["departments"][i]
            grade = known_faces["grades"][i]
            display_text = f"{name} | {student_id} | {department} | {grade}학년"
            self.face_listbox.insert(tk.END, display_text)
    
    def delete_selected(self):
        """선택된 얼굴 삭제"""
        selection = self.face_listbox.curselection()
        if not selection:
            messagebox.showwarning("경고", "삭제할 얼굴을 선택하세요.")
            return
        
        selected_text = self.face_listbox.get(selection[0])
        # "이름 | 학번 | 학과 | 학년" 형식에서 학번 추출
        parts = selected_text.split(" | ")
        if len(parts) < 2:
            messagebox.showerror("오류", "데이터 형식이 올바르지 않습니다.")
            return
        
        name = parts[0]
        student_id = parts[1]
        
        if messagebox.askyesno("확인", f"'{name}' (학번: {student_id})을(를) 삭제하시겠습니까?"):
            if self.manager.db.delete_face(student_id):
                messagebox.showinfo("성공", f"'{name}'이(가) 삭제되었습니다.")
                self.refresh_data()
            else:
                messagebox.showerror("오류", "삭제에 실패했습니다.")
    
    def show_logs(self):
        """인식 로그 표시"""
        logs = self.manager.db.get_recognition_logs(limit=100)
        
        if not logs:
            messagebox.showinfo("로그", "인식 로그가 없습니다.")
            return
        
        # 새 창으로 로그 표시
        log_window = tk.Toplevel(self)
        log_window.title("인식 로그")
        log_window.geometry("600x400")
        
        # 텍스트 위젯
        text_frame = tk.Frame(log_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_widget = tk.Text(
            text_frame,
            font=("Courier", 10),
            yscrollcommand=scrollbar.set
        )
        text_widget.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_widget.yview)
        
        # 로그 삽입
        text_widget.insert(tk.END, "=== 최근 100개 인식 로그 ===\n\n")
        text_widget.insert(tk.END, "시간 | 이름 | 학번 | 상태\n")
        text_widget.insert(tk.END, "-" * 60 + "\n")
        for log in logs:
            log_id, name, student_id, is_registered, timestamp = log
            status = "[등록됨]" if is_registered else "[미등록]"
            student_id_str = student_id if student_id else "N/A"
            text_widget.insert(tk.END, f"{timestamp} | {name} | {student_id_str} | {status}\n")
        
        text_widget.config(state=tk.DISABLED)


class RecognitionScreen(tk.Frame):
    """얼굴 인식 실행 화면"""
    def __init__(self, parent, manager):
        super().__init__(parent, bg="#2c3e50")
        self.manager = manager
        self.video_capture = None
        self.is_running = False
        self.recognition_thread = None
        
        # 🔔 스레드 안전 GUI 업데이트를 위한 큐
        self.frame_queue = queue.Queue(maxsize=2)
        
        # 🔔 비동기 로깅을 위한 큐
        self.log_queue = queue.Queue()
        self.logging_thread = None
        
        # 감지기 초기화 (사용자 설정 우선)
        self.detector = None
        self.detector_type = "HOG"
        self._initialize_detector()
        
        # 하위 호환성을 위한 별칭
        self.yolo_detector = self.detector
        self.use_yolo = (self.detector_type != "HOG")
        
        # 한글 폰트 설정 (프로젝트 폴더 우선)
        font_paths = [
            "fonts/NanumGothic.ttf",  # 프로젝트 폴더
            "/System/Library/Fonts/AppleSDGothicNeo.ttc",  # macOS
            "/Library/Fonts/Arial Unicode.ttf",  # macOS
            "C:\\Windows\\Fonts\\malgun.ttf",  # Windows 맑은고딕
            "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",  # Linux
        ]
        
        self.font = None
        self.font_small = None
        
        for font_path in font_paths:
            try:
                self.font = ImageFont.truetype(font_path, 28)
                self.font_small = ImageFont.truetype(font_path, 18)
                print(f"[INFO] 폰트 로드 성공: {font_path}")
                break
            except:
                continue
        
        if self.font is None:
            print("[WARN] 한글 폰트를 찾을 수 없습니다. 기본 폰트 사용 (한글 깨짐 가능)")
            self.font = ImageFont.load_default()
            self.font_small = ImageFont.load_default()
        
        self.setup_ui()
    
    def _initialize_detector(self):
        """사용자 설정에 따라 감지기 초기화"""
        # 기본값 설정
        if 'detector_type' not in self.manager.settings:
            self.manager.settings['detector_type'] = 'auto'
        
        detector_choice = self.manager.settings['detector_type']
        
        print(f"[INFO] 감지기 설정: {detector_choice}")
        
        # 사용자가 특정 감지기를 선택한 경우
        if detector_choice == 'retinaface':
            if self._try_init_retinaface():
                return
            else:
                print("[WARN] RetinaFace를 사용할 수 없습니다. 다른 감지기로 전환합니다.")
        
        elif detector_choice == 'yolo':
            if self._try_init_yolo():
                return
            else:
                print("[WARN] YOLO-Face를 사용할 수 없습니다. 다른 감지기로 전환합니다.")
        
        elif detector_choice == 'hog':
            self.detector_type = "HOG"
            print("[INFO] ℹ️  HOG 감지기 사용 (사용자 선택)")
            return
        
        # 'auto' 모드 또는 선택한 감지기 사용 불가 시 자동 선택
        print("[INFO] 자동 감지기 선택 중...")
        
        # RetinaFace 시도
        if self._try_init_retinaface():
            return
        
        # YOLO-Face 시도
        if self._try_init_yolo():
            return
        
        # HOG 사용 (기본)
        self.detector_type = "HOG"
        print("[INFO] ℹ️  HOG 감지기 사용 (기본)")
    
    def _try_init_retinaface(self):
        """RetinaFace 초기화 시도"""
        try:
            from retinaface_detector import RetinaFaceDetector
            self.detector = RetinaFaceDetector(conf_threshold=0.5)
            self.detector_type = "RetinaFace"
            print("[INFO] ✅ RetinaFace 감지기 사용")
            return True
        except Exception as e:
            print(f"[WARN] RetinaFace 초기화 실패: {e}")
            return False
    
    def _try_init_yolo(self):
        """YOLO-Face 초기화 시도"""
        try:
            from yolo_face_detector import YOLOFaceDetector
            self.detector = YOLOFaceDetector(conf_threshold=0.3)
            self.detector_type = "YOLO-Face"
            print("[INFO] ✅ YOLO-Face 감지기 사용")
            return True
        except Exception as e:
            print(f"[WARN] YOLO-Face 초기화 실패: {e}")
            return False
    
    def setup_ui(self):
        # 헤더
        header = tk.Frame(self, bg="#34495e", height=80)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="얼굴 인식 실행",
            font=("Arial", 24, "bold"),
            bg="#34495e",
            fg="black"
        ).pack(side=tk.LEFT, padx=20, pady=20)
        
        tk.Button(
            header,
            text="< 뒤로 가기",
            command=self.go_back,
            bg="#7f8c8d",
            fg="black",
            font=("Arial", 12, "bold"),
            cursor="hand2",
            width=12,
            height=2,
            relief=tk.RAISED,
            bd=2
        ).pack(side=tk.RIGHT, padx=20, pady=15)
        
        # 비디오 프레임
        video_container = tk.Frame(self, bg="black")
        video_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.video_label = tk.Label(
            video_container,
            bg="black",
            text="카메라 대기 중...\n\n'시작' 버튼을 눌러주세요",
            fg="black",
            font=("Arial", 16)
        )
        self.video_label.pack(fill=tk.BOTH, expand=True)
        
        # 컨트롤 버튼
        control_frame = tk.Frame(self, bg="#2c3e50")
        control_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.start_button = tk.Button(
            control_frame,
            text="시 작",
            command=self.start_recognition,
            bg="#27ae60",
            fg="black",
            font=("Arial", 16, "bold"),
            cursor="hand2",
            width=20,
            height=2,
            relief=tk.RAISED,
            bd=3,
            activebackground="#27ae60",
            activeforeground="black"
        )
        self.start_button.pack(side=tk.LEFT, padx=10)
        
        self.stop_button = tk.Button(
            control_frame,
            text="정 지",
            command=self.stop_recognition,
            bg="#e74c3c",
            fg="black",
            font=("Arial", 16, "bold"),
            cursor="hand2",
            width=20,
            height=2,
            state=tk.DISABLED,
            relief=tk.RAISED,
            bd=3,
            activebackground="#e74c3c",
            activeforeground="black"
        )
        self.stop_button.pack(side=tk.LEFT, padx=10)
        
        # 상태 표시
        self.status_label = tk.Label(
            self,
            text="대기 중",
            font=("Arial", 12),
            bg="#2c3e50",
            fg="#bdc3c7"
        )
        self.status_label.pack(pady=10)
        
        # 감지기 정보 표시
        detector_emoji = {
            "RetinaFace": "🏆",
            "YOLO-Face": "⚡",
            "HOG": "🔧"
        }
        emoji = detector_emoji.get(self.detector_type, "🔍")
        
        self.detector_info = tk.Label(
            self,
            text=f"감지 엔진: {emoji} {self.detector_type}",
            font=("Arial", 11, "bold"),
            bg="#2c3e50",
            fg="#3498db"
        )
        self.detector_info.pack(pady=5)
    
    def on_show(self):
        """화면이 표시될 때"""
        if not self.is_running:
            # 🔔 설정이 변경되었을 수 있으므로 감지기 재로드
            self._initialize_detector()
            
            detector_emoji = {
                "RetinaFace": "🏆",
                "YOLO-Face": "⚡",
                "HOG": "🔧"
            }
            emoji = detector_emoji.get(self.detector_type, "🔍")
            self.status_label.config(text=f"대기 중 - '시작' 버튼을 누르세요")
            self.detector_info.config(text=f"감지 엔진: {emoji} {self.detector_type}")
    
    def start_recognition(self):
        """얼굴 인식 시작"""
        # 등록된 얼굴 확인
        known_faces = self.manager.db.get_all_faces()
        if len(known_faces["names"]) == 0:
            if not messagebox.askyesno("경고", "등록된 얼굴이 없습니다.\n\n그래도 카메라를 시작하시겠습니까?"):
                return
        
        # 카메라 열기
        camera_index = self.manager.settings['camera_index']
        self.video_capture = cv2.VideoCapture(camera_index)
        
        if not self.video_capture.isOpened():
            messagebox.showerror("오류", f"카메라 {camera_index}를 열 수 없습니다.\n환경 설정에서 카메라를 확인하세요.")
            return
        
        # 카메라 해상도 및 FPS 최적화 (Jetson Nano 포함)
        self.video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.video_capture.set(cv2.CAP_PROP_FPS, 30)
        
        # 🚀 카메라 버퍼 최소화 (중요! - 지연 감소)
        self.video_capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        # 🚀 추가 최적화 (macOS/Linux)
        try:
            self.video_capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M','J','P','G'))
        except:
            pass
        
        # 실제 설정된 값 확인
        actual_width = int(self.video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(self.video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        actual_fps = int(self.video_capture.get(cv2.CAP_PROP_FPS))
        print(f"[INFO] 카메라 해상도: {actual_width}x{actual_height} @ {actual_fps}FPS")
        print(f"[INFO] ⚡ 최적화 모드: 버퍼=1, MJPG 코덱")
        
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        detector_emoji = {
            "RetinaFace": "🏆",
            "YOLO-Face": "⚡",
            "HOG": "🔧"
        }
        emoji = detector_emoji.get(self.detector_type, "🔍")
        self.status_label.config(text=f"실행 중... ({emoji} {self.detector_type})", fg="#27ae60")
        
        # 🔔 비동기 로깅 스레드 시작
        self.logging_thread = threading.Thread(target=self._process_log_queue, daemon=True)
        self.logging_thread.start()
        
        # 인식 스레드 시작
        self.recognition_thread = threading.Thread(target=self.process_video, daemon=True)
        self.recognition_thread.start()
        
        # 🔔 메인 스레드에서 GUI 업데이터 시작
        self.update_gui()
        
        print(f"[INFO] 얼굴 인식 시작 - 카메라: {camera_index}, 설정: {self.manager.settings}")
    
    def stop_recognition(self):
        """얼굴 인식 정지"""
        self.is_running = False
        
        if self.video_capture:
            self.video_capture.release()
        
        # 🔔 큐 비우기
        while not self.frame_queue.empty():
            try:
                self.frame_queue.get_nowait()
            except queue.Empty:
                break
        
        while not self.log_queue.empty():
            try:
                self.log_queue.get_nowait()
            except queue.Empty:
                break
        
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="정지됨", fg="#e74c3c")
        self.video_label.config(image="", text="정지됨\n\n'시작' 버튼을 눌러 다시 시작하세요")
        
        print("[INFO] 얼굴 인식 정지")
    
    def go_back(self):
        """뒤로 가기"""
        if self.is_running:
            if messagebox.askyesno("확인", "인식이 실행 중입니다. 정지하고 나가시겠습니까?"):
                self.stop_recognition()
                self.manager.show_screen('lobby')
        else:
            self.manager.show_screen('lobby')
    
    def process_video(self):
        """비디오 프레임 처리 및 얼굴 인식"""
        # 성능 최적화: 프레임 스킵 설정 (얼굴 인식용)
        process_every_n_frames = 3 if self.manager.settings['upsample_times'] >= 1 else 2
        frame_count = 0
        
        # 이전 프레임의 얼굴 정보 저장 (화면 표시용)
        display_face_locations = []
        display_face_names = []
        
        # 로깅 쿨다운 관리
        last_logged_names = {}
        log_cooldown = 5.0  # 5초마다 로그
        
        # 등록된 얼굴 로드 (NumPy 배열로 미리 변환)
        known_faces = self.manager.db.get_all_faces()
        known_encodings_array = np.array(known_faces["encodings"]) if len(known_faces["encodings"]) > 0 else None
        
        print("[INFO] 비디오 처리 시작...")
        print(f"[INFO] 등록된 얼굴: {len(known_faces['names'])}명")
        print(f"[INFO] 성능 설정 - 프레임스킵: {process_every_n_frames}, 업샘플: {self.manager.settings['upsample_times']}, 스케일: {self.manager.settings['frame_scale']}")
        
        fps_start_time = time.time()
        fps_frame_count = 0
        current_fps = 0
        
        while self.is_running:
            ret, frame = self.video_capture.read()
            if not ret:
                break
            
            frame_count += 1
            fps_frame_count += 1
            
            # FPS 계산 (30프레임마다)
            if fps_frame_count >= 30:
                elapsed = time.time() - fps_start_time
                current_fps = fps_frame_count / elapsed if elapsed > 0 else 0
                fps_start_time = time.time()
                fps_frame_count = 0
            
            # 매 N 프레임마다 얼굴 인식 수행 (무거운 작업)
            if frame_count % process_every_n_frames == 0:
                # 프레임 크기 조정 (INTER_NEAREST가 가장 빠름)
                frame_scale = self.manager.settings['frame_scale']
                small_frame = cv2.resize(frame, (0, 0), fx=frame_scale, fy=frame_scale, interpolation=cv2.INTER_NEAREST)
                rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                
                # 얼굴 위치 및 인코딩
                try:
                    # RetinaFace, YOLO-Face 또는 HOG 사용
                    if self.detector and self.detector_type != "HOG":
                        # 🔔 RetinaFace/YOLO는 upsample_times 불필요
                        face_locations = self.detector.detect_faces(rgb_small_frame)
                    else:
                        face_locations = face_recognition.face_locations(
                            rgb_small_frame,
                            model="hog",
                            number_of_times_to_upsample=self.manager.settings['upsample_times']
                        )
                    
                    # 얼굴이 없으면 인코딩 스킵 (성능 향상)
                    if len(face_locations) == 0:
                        face_encodings = []
                    else:
                        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                    
                except Exception as e:
                    print(f"[ERROR] 얼굴 인식 오류: {e}")
                    continue
                
                face_names = []
                face_student_ids = []
                
                for face_encoding in face_encodings:
                    name = "Unknown"
                    student_id = None
                    confidence = 0.0
                    
                    if known_encodings_array is not None:
                        try:
                            # NumPy로 빠른 거리 계산
                            face_distances = np.linalg.norm(known_encodings_array - face_encoding, axis=1)
                            best_match_index = face_distances.argmin()
                            best_distance = face_distances[best_match_index]
                            
                            # 신뢰도 계산
                            confidence = max(0, 1 - best_distance)
                            
                            # 매칭 확인 (단일 비교로 최적화)
                            tolerance = self.manager.settings['tolerance']
                            distance_threshold = self.manager.settings['distance_threshold']
                            
                            if best_distance <= min(tolerance, distance_threshold):
                                name = known_faces["names"][best_match_index]
                                student_id = known_faces["student_ids"][best_match_index]
                                
                                # 🔔 비동기 로깅 큐에 넣기
                                current_time = time.time()
                                if student_id not in last_logged_names or \
                                   (current_time - last_logged_names[student_id]) > log_cooldown:
                                    self.log_queue.put((name, student_id, True))
                                    last_logged_names[student_id] = current_time
                        except Exception as e:
                            pass  # 에러 무시하고 계속
                    
                    # Unknown 로그 (빈도 낮춤)
                    if name == "Unknown":
                        if "Unknown" not in last_logged_names or \
                           (time.time() - last_logged_names["Unknown"]) > log_cooldown * 2:  # Unknown은 더 낮은 빈도
                            # 🔔 비동기 로깅 큐에 넣기
                            self.log_queue.put(("Unknown", None, False))
                            last_logged_names["Unknown"] = time.time()
                    
                    # 신뢰도 표시 (문자열 포맷 최적화)
                    if self.manager.settings['show_confidence'] and name != "Unknown":
                        name_with_confidence = f"{name} ({int(confidence*100)}%)"
                    else:
                        name_with_confidence = name
                    
                    face_names.append(name_with_confidence)
                    face_student_ids.append(student_id)
                
                # 화면 표시용 위치 업데이트 (스케일 적용)
                scale_factor = int(1 / frame_scale)
                display_face_locations = [(t*scale_factor, r*scale_factor, b*scale_factor, l*scale_factor)
                                         for (t, r, b, l) in face_locations]
                display_face_names = face_names
            
            # 🔔 매 프레임 화면 표시 (PIL로 한글 지원)
            display_frame = frame.copy()
            
            # OpenCV로 바운딩 박스 그리기
            for i, (top, right, bottom, left) in enumerate(display_face_locations):
                if i >= len(display_face_names):
                    break
                
                name = display_face_names[i]
                
                # 바운딩 박스 색상 (등록: 녹색, 미등록: 빨강)
                color = (0, 255, 0) if "Unknown" not in name else (0, 0, 255)
                
                # 박스 그리기
                cv2.rectangle(display_frame, (left, top), (right, bottom), color, 2)
            
            # BGR -> RGB 변환
            rgb_display = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
            
            # 🔔 PIL로 변환 (한글 폰트 사용)
            img = Image.fromarray(rgb_display)
            draw = ImageDraw.Draw(img)
            
            # 🔔 PIL로 텍스트 그리기 (한글 지원!)
            for i, (top, right, bottom, left) in enumerate(display_face_locations):
                if i >= len(display_face_names):
                    break
                
                name = display_face_names[i]
                color_rgb = (0, 255, 0) if "Unknown" not in name else (255, 0, 0)
                
                # 이름 배경 박스
                label_height = 35
                draw.rectangle([(left, bottom - label_height), (right, bottom)], fill=color_rgb)
                
                # 텍스트 그리기 (self.font_small 사용)
                draw.text((left + 6, bottom - label_height + 4), name, font=self.font_small, fill=(255, 255, 255))
            
            # FPS 정보
            info_text = f"FPS: {int(current_fps)} | 얼굴: {len(display_face_names)}"
            draw.text((10, 10), info_text, font=self.font_small, fill=(0, 255, 0))
            
            # 🔔 리사이즈 및 PhotoImage 변환
            img_resized = img.resize((960, 540), Image.Resampling.NEAREST)
            photo = ImageTk.PhotoImage(image=img_resized)
            
            # 🔔 큐에 넣기 (서브 스레드는 GUI 업데이트 금지!)
            if self.is_running:
                try:
                    # 큐가 꽉 찼으면 이전 프레임 버리고 새 프레임 넣기
                    if self.frame_queue.full():
                        try:
                            self.frame_queue.get_nowait()
                        except queue.Empty:
                            pass
                    self.frame_queue.put_nowait(photo)
                except queue.Full:
                    pass  # 큐가 꽉 찼으면 그냥 넘어감
        
        print("[INFO] 비디오 처리 종료")
    
    def update_gui(self):
        """🔔 메인 스레드에서 큐를 확인하고 GUI를 안전하게 업데이트"""
        if not self.is_running:
            return  # 인식이 중지되었으면 업데이터도 종료
        
        try:
            # 큐에서 프레임을 가져옴 (블로킹 없이)
            photo = self.frame_queue.get_nowait()
            
            # GUI 업데이트 (메인 스레드이므로 안전!)
            self.video_label.imgtk = photo
            self.video_label.configure(image=photo, text="")
        
        except queue.Empty:
            pass  # 큐가 비었으면 아무것도 안 함
        
        # 16ms(약 60fps) 후에 이 함수를 다시 실행하도록 예약
        self.master.after(16, self.update_gui)
    
    def _process_log_queue(self):
        """🔔 비동기 로깅 처리 스레드"""
        while self.is_running:
            try:
                # 큐에서 로그 데이터 가져오기 (최대 1초 대기)
                log_data = self.log_queue.get(timeout=1.0)
                name, student_id, is_registered = log_data
                
                # DB에 기록 (시간이 걸려도 비디오 처리에 영향 없음)
                try:
                    self.manager.db.log_recognition(name, student_id, is_registered)
                except Exception as e:
                    print(f"[ERROR] 로그 기록 실패: {e}")
            
            except queue.Empty:
                continue  # 타임아웃 시 계속
        
        print("[INFO] 로깅 스레드 종료")

