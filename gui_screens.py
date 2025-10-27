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
from database import FaceDatabase

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
        
        messagebox.showinfo("저장 완료", "설정이 저장되었습니다!")
        print(f"[INFO] 설정 저장: {self.manager.settings}")


class RegisterScreen(tk.Frame):
    """얼굴 등록 화면"""
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
                # 얼굴 감지 및 인코딩
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                face_locations = face_recognition.face_locations(rgb_frame)
                
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
        
        # 한글 폰트 설정
        try:
            self.font = ImageFont.truetype("/System/Library/Fonts/AppleSDGothicNeo.ttc", 30)
            self.font_small = ImageFont.truetype("/System/Library/Fonts/AppleSDGothicNeo.ttc", 20)
        except:
            try:
                self.font = ImageFont.truetype("/Library/Fonts/Arial Unicode.ttf", 30)
                self.font_small = ImageFont.truetype("/Library/Fonts/Arial Unicode.ttf", 20)
            except:
                self.font = ImageFont.load_default()
                self.font_small = ImageFont.load_default()
        
        self.setup_ui()
    
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
    
    def on_show(self):
        """화면이 표시될 때"""
        if not self.is_running:
            self.status_label.config(text="대기 중 - '시작' 버튼을 누르세요")
    
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
        
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="실행 중...", fg="#27ae60")
        
        # 인식 스레드 시작
        self.recognition_thread = threading.Thread(target=self.process_video, daemon=True)
        self.recognition_thread.start()
        
        print(f"[INFO] 얼굴 인식 시작 - 카메라: {camera_index}, 설정: {self.manager.settings}")
    
    def stop_recognition(self):
        """얼굴 인식 정지"""
        self.is_running = False
        
        if self.video_capture:
            self.video_capture.release()
        
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
        process_every_n_frames = 2  # 성능 최적화: 매 2 프레임마다 얼굴 인식
        frame_count = 0
        
        # 이전 프레임의 얼굴 정보 저장
        previous_face_locations = []
        previous_face_names = []
        previous_student_ids = []
        
        # 부드러운 이동을 위한 변수
        smoothed_face_locations = []
        target_face_locations = []
        smoothing_factor = 0.2
        
        # 로깅 쿨다운 관리
        last_logged_names = {}
        log_cooldown = 5.0  # 5초마다 로그
        
        # 등록된 얼굴 로드
        known_faces = self.manager.db.get_all_faces()
        
        print("[INFO] 비디오 처리 시작...")
        print(f"[INFO] 등록된 얼굴: {len(known_faces['names'])}명")
        print(f"[INFO] 성능 설정 - 업샘플: {self.manager.settings['upsample_times']}, 스케일: {self.manager.settings['frame_scale']}")
        
        fps_start_time = time.time()
        
        while self.is_running:
            ret, frame = self.video_capture.read()
            if not ret:
                print("[ERROR] 프레임을 읽을 수 없습니다.")
                break
            
            frame_count += 1
            
            # 매 N 프레임마다 얼굴 인식 수행
            if frame_count % process_every_n_frames == 0:
                # 프레임 크기 조정
                frame_scale = self.manager.settings['frame_scale']
                small_frame = cv2.resize(frame, (0, 0), fx=frame_scale, fy=frame_scale)
                rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                
                # 얼굴 위치 및 인코딩
                try:
                    face_locations = face_recognition.face_locations(
                        rgb_small_frame,
                        model="hog",
                        number_of_times_to_upsample=self.manager.settings['upsample_times']
                    )
                    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                    
                    if len(face_locations) > 0:
                        print(f"[INFO] {len(face_locations)}개의 얼굴 감지됨")
                except Exception as e:
                    print(f"[ERROR] 얼굴 인식 오류: {e}")
                    continue
                
                face_names = []
                face_student_ids = []
                
                for face_encoding in face_encodings:
                    name = "Unknown"
                    student_id = None
                    confidence = 0.0
                    
                    if len(known_faces["encodings"]) > 0:
                        try:
                            # 거리 계산
                            face_distances = face_recognition.face_distance(
                                known_faces["encodings"],
                                face_encoding
                            )
                            best_match_index = face_distances.argmin()
                            best_distance = face_distances[best_match_index]
                            
                            # 신뢰도 계산
                            confidence = max(0, 1 - best_distance)
                            
                            # 매칭 확인
                            if best_distance <= self.manager.settings['tolerance'] and \
                               best_distance <= self.manager.settings['distance_threshold']:
                                matches = face_recognition.compare_faces(
                                    [known_faces["encodings"][best_match_index]],
                                    face_encoding,
                                    tolerance=self.manager.settings['tolerance']
                                )
                                
                                if matches[0]:
                                    name = known_faces["names"][best_match_index]
                                    student_id = known_faces["student_ids"][best_match_index]
                                    
                                    # 등록된 사람 로그
                                    current_time = time.time()
                                    if student_id not in last_logged_names or \
                                       (current_time - last_logged_names[student_id]) > log_cooldown:
                                        try:
                                            self.manager.db.log_recognition(name, student_id, True)
                                            last_logged_names[student_id] = current_time
                                            print(f"[INFO] 인식: {name} ({student_id}) - 신뢰도: {confidence:.2%}")
                                        except Exception as e:
                                            print(f"[WARNING] 로그 저장 실패: {e}")
                        except Exception as e:
                            print(f"[ERROR] 얼굴 비교 오류: {e}")
                    
                    # Unknown 로그
                    if name == "Unknown":
                        if "Unknown" not in last_logged_names or \
                           (time.time() - last_logged_names["Unknown"]) > log_cooldown:
                            try:
                                self.manager.db.log_recognition("Unknown", None, False)
                                last_logged_names["Unknown"] = time.time()
                            except Exception as e:
                                print(f"[WARNING] 로그 저장 실패: {e}")
                    
                    # 신뢰도 표시
                    if self.manager.settings['show_confidence'] and name != "Unknown":
                        name_with_confidence = f"{name} ({confidence:.0%})"
                    else:
                        name_with_confidence = name
                    
                    face_names.append(name_with_confidence)
                    face_student_ids.append(student_id)
                
                # 목표 위치 업데이트
                scale_factor = int(1 / frame_scale)
                target_face_locations = [(t*scale_factor, r*scale_factor, b*scale_factor, l*scale_factor)
                                        for (t, r, b, l) in face_locations]
                previous_face_names = face_names
                previous_student_ids = face_student_ids
                
                # 첫 프레임이거나 얼굴 수가 변경된 경우 즉시 업데이트
                if len(smoothed_face_locations) != len(target_face_locations):
                    smoothed_face_locations = target_face_locations.copy()
            
            # 부드러운 이동 적용
            if len(smoothed_face_locations) > 0 and len(target_face_locations) > 0:
                for i in range(len(smoothed_face_locations)):
                    if i < len(target_face_locations):
                        st, sr, sb, sl = smoothed_face_locations[i]
                        tt, tr, tb, tl = target_face_locations[i]
                        
                        smoothed_face_locations[i] = (
                            int(st + (tt - st) * smoothing_factor),
                            int(sr + (tr - sr) * smoothing_factor),
                            int(sb + (tb - sb) * smoothing_factor),
                            int(sl + (tl - sl) * smoothing_factor)
                        )
            
            # OpenCV BGR을 RGB로 변환 후 PIL로 처리
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_frame)
            draw = ImageDraw.Draw(pil_image)
            
            # 바운딩 박스 그리기
            for i, (top, right, bottom, left) in enumerate(smoothed_face_locations):
                if i >= len(previous_face_names):
                    break
                
                name = previous_face_names[i]
                
                # 바운딩 박스 색상 (등록: 녹색, 미등록: 빨강)
                color = (0, 255, 0) if name != "Unknown" else (255, 0, 0)
                
                # 박스 그리기
                for thickness in range(3):
                    draw.rectangle(
                        [left - thickness, top - thickness, right + thickness, bottom + thickness],
                        outline=color,
                        width=1
                    )
                
                # 이름 배경 박스
                text_bbox = draw.textbbox((0, 0), name, font=self.font_small)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                
                draw.rectangle(
                    [left, bottom - text_height - 15, left + text_width + 20, bottom],
                    fill=color
                )
                
                # 한글 이름 텍스트
                draw.text(
                    (left + 10, bottom - text_height - 10),
                    name,
                    font=self.font_small,
                    fill=(0, 0, 0)  # 검은색
                )
            
            # 상태 정보 표시
            info_text = f"얼굴: {len(previous_face_names)}명"
            draw.text((10, 10), info_text, font=self.font_small, fill=(255, 255, 255))
            
            # PIL Image를 numpy 배열로 변환
            frame = np.array(pil_image)
            
            # FPS 계산
            if frame_count == 1:
                fps_start_time = time.time()
            
            if frame_count % 30 == 0 and frame_count > 1:
                fps = 30 / (time.time() - fps_start_time)
                fps_start_time = time.time()
                print(f"[INFO] FPS: {fps:.1f}, 인식된 얼굴: {len(previous_face_names)}명")
            
            # PIL Image로 변환 및 리사이즈
            img = Image.fromarray(frame)
            img = img.resize((960, 540), Image.Resampling.LANCZOS)
            
            # PhotoImage로 변환
            photo = ImageTk.PhotoImage(image=img)
            
            # GUI 업데이트
            try:
                if self.is_running:
                    self.video_label.imgtk = photo
                    self.video_label.configure(image=photo, text="")
            except Exception as e:
                print(f"[ERROR] GUI 업데이트 오류: {e}")
                break
            
            time.sleep(0.01)
        
        print("[INFO] 비디오 처리 종료")

