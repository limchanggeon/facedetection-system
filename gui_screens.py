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
            text="🎯 실시간 얼굴 인식 시스템",
            font=("Arial", 36, "bold"),
            bg="#2c3e50",
            fg="white"
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
            ("🎥 얼굴 인식 시작", "recognition", "#27ae60", 200, 80),
            ("👤 얼굴 등록 관리", "register", "#3498db", 200, 80),
            ("💾 데이터베이스 관리", "database", "#f39c12", 200, 80),
            ("⚙️ 환경 설정", "settings", "#9b59b6", 200, 80),
        ]
        
        row = 0
        col = 0
        for text, screen, color, width, height in buttons:
            btn = tk.Button(
                button_frame,
                text=text,
                command=lambda s=screen: self.manager.show_screen(s),
                bg=color,
                fg="white",
                font=("Arial", 16, "bold"),
                width=width,
                height=height,
                cursor="hand2",
                relief=tk.RAISED,
                bd=3
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
            text=f"📊 등록된 얼굴: {registered_count}명",
            font=("Arial", 14),
            bg="#34495e",
            fg="white",
            pady=15
        ).pack()
        
        # 푸터
        footer_frame = tk.Frame(self, bg="#2c3e50")
        footer_frame.pack(side=tk.BOTTOM, pady=20)
        
        tk.Label(
            footer_frame,
            text="© 2025 Lim Changgeon | MIT License",
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
            text="⚙️ 환경 설정",
            font=("Arial", 24, "bold"),
            bg="#34495e",
            fg="white"
        ).pack(side=tk.LEFT, padx=20, pady=20)
        
        tk.Button(
            header,
            text="← 뒤로 가기",
            command=lambda: self.manager.show_screen('lobby'),
            bg="#7f8c8d",
            fg="white",
            font=("Arial", 12, "bold"),
            cursor="hand2"
        ).pack(side=tk.RIGHT, padx=20, pady=20)
        
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
            text="📷 카메라 설정",
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
            ("💻 노트북 내장 카메라 (카메라 0)", 0),
            ("🎥 외장 USB 카메라 1", 1),
            ("🎥 외장 USB 카메라 2", 2),
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
            text="🔍 카메라 테스트",
            command=self.test_camera,
            bg="#3498db",
            fg="white",
            font=("Arial", 11, "bold"),
            cursor="hand2"
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
            text="⚡ 성능 프리셋",
            font=("Arial", 16, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50",
            padx=20,
            pady=20
        )
        preset_frame.pack(fill=tk.X, padx=20, pady=10)
        
        presets = [
            ("⚡ 고속 모드 (25-30 FPS, 가까운 거리)", "fast", "#27ae60"),
            ("⚖️ 균형 모드 (18-22 FPS, 중거리)", "balanced", "#3498db"),
            ("🎥 CCTV 모드 (10-15 FPS, 원거리)", "cctv", "#e74c3c"),
        ]
        
        for text, mode, color in presets:
            tk.Button(
                preset_frame,
                text=text,
                command=lambda m=mode: self.apply_preset(m),
                bg=color,
                fg="white",
                font=("Arial", 12, "bold"),
                cursor="hand2",
                height=2
            ).pack(fill=tk.X, pady=5)
        
        # 고급 설정
        advanced_frame = tk.LabelFrame(
            scrollable_frame,
            text="🔧 고급 설정",
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
            text="💾 설정 저장",
            command=self.save_settings,
            bg="#27ae60",
            fg="white",
            font=("Arial", 14, "bold"),
            cursor="hand2",
            height=2
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
                    text=f"✅ 카메라 {camera_index} 사용 가능 ({width}x{height})",
                    fg="#27ae60"
                )
            else:
                self.camera_status.config(
                    text=f"⚠️ 카메라 {camera_index}에서 프레임을 읽을 수 없습니다",
                    fg="#e67e22"
                )
            cap.release()
        else:
            self.camera_status.config(
                text=f"❌ 카메라 {camera_index}를 열 수 없습니다",
                fg="#e74c3c"
            )
    
    def apply_preset(self, mode):
        """프리셋 적용"""
        presets = {
            'fast': {
                'tolerance': 0.45,
                'upsample_times': 0,
                'frame_scale': 0.25,
                'name': '⚡ 고속 모드'
            },
            'balanced': {
                'tolerance': 0.40,
                'upsample_times': 1,
                'frame_scale': 0.25,
                'name': '⚖️ 균형 모드'
            },
            'cctv': {
                'tolerance': 0.35,
                'upsample_times': 2,
                'frame_scale': 0.5,
                'name': '🎥 CCTV 모드'
            }
        }
        
        preset = presets[mode]
        self.tolerance_var.set(preset['tolerance'])
        self.upsample_var.set(preset['upsample_times'])
        self.manager.settings['frame_scale'] = preset['frame_scale']
        
        messagebox.showinfo("프리셋 적용", f"{preset['name']}가 적용되었습니다!\n\n설정을 저장하려면 '설정 저장' 버튼을 클릭하세요.")
    
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
            text="👤 얼굴 등록 관리",
            font=("Arial", 24, "bold"),
            bg="#34495e",
            fg="white"
        ).pack(side=tk.LEFT, padx=20, pady=20)
        
        tk.Button(
            header,
            text="← 뒤로 가기",
            command=lambda: self.manager.show_screen('lobby'),
            bg="#7f8c8d",
            fg="white",
            font=("Arial", 12, "bold"),
            cursor="hand2"
        ).pack(side=tk.RIGHT, padx=20, pady=20)
        
        # 메인 컨텐츠
        main_frame = tk.Frame(self, bg="#ecf0f1")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 등록 버튼
        tk.Button(
            main_frame,
            text="➕ 새 얼굴 등록하기",
            command=self.register_new_face,
            bg="#27ae60",
            fg="white",
            font=("Arial", 16, "bold"),
            cursor="hand2",
            height=3
        ).pack(fill=tk.X, pady=10)
        
        # 안내 메시지
        info_frame = tk.Frame(main_frame, bg="#3498db", relief=tk.RAISED, bd=2)
        info_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            info_frame,
            text="💡 등록 방법:\n1. 이름을 입력하세요\n2. 카메라를 보고 스페이스바를 누르세요\n3. ESC를 누르면 취소됩니다",
            font=("Arial", 12),
            bg="#3498db",
            fg="white",
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
        self.stats_label.config(text=f"📊 현재 등록된 얼굴: {count}명")
    
    def register_new_face(self):
        """새 얼굴 등록"""
        name = simpledialog.askstring("이름 입력", "등록할 사람의 이름을 입력하세요:")
        
        if not name:
            return
        
        # 이미 등록된 이름인지 확인
        known_faces = self.manager.db.get_all_faces()
        if name in known_faces["names"]:
            messagebox.showerror("오류", f"'{name}'은(는) 이미 등록된 이름입니다.")
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
            if self.manager.db.add_face(name, encoding):
                messagebox.showinfo("성공", f"'{name}'이(가) 성공적으로 등록되었습니다!")
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
            text="💾 데이터베이스 관리",
            font=("Arial", 24, "bold"),
            bg="#34495e",
            fg="white"
        ).pack(side=tk.LEFT, padx=20, pady=20)
        
        tk.Button(
            header,
            text="← 뒤로 가기",
            command=lambda: self.manager.show_screen('lobby'),
            bg="#7f8c8d",
            fg="white",
            font=("Arial", 12, "bold"),
            cursor="hand2"
        ).pack(side=tk.RIGHT, padx=20, pady=20)
        
        # 메인 컨텐츠
        main_frame = tk.Frame(self, bg="#ecf0f1")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 통계
        stats_frame = tk.LabelFrame(
            main_frame,
            text="📊 통계",
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
            text="👥 등록된 얼굴 목록",
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
            text="🔄 새로고침",
            command=self.refresh_data,
            bg="#3498db",
            fg="white",
            font=("Arial", 12, "bold"),
            cursor="hand2",
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="🗑️ 선택 삭제",
            command=self.delete_selected,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 12, "bold"),
            cursor="hand2",
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="📋 인식 로그 보기",
            command=self.show_logs,
            bg="#f39c12",
            fg="white",
            font=("Arial", 12, "bold"),
            cursor="hand2",
            width=15
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
        for name in known_faces["names"]:
            self.face_listbox.insert(tk.END, name)
    
    def delete_selected(self):
        """선택된 얼굴 삭제"""
        selection = self.face_listbox.curselection()
        if not selection:
            messagebox.showwarning("경고", "삭제할 얼굴을 선택하세요.")
            return
        
        name = self.face_listbox.get(selection[0])
        
        if messagebox.askyesno("확인", f"'{name}'을(를) 삭제하시겠습니까?"):
            if self.manager.db.delete_face(name):
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
        for log in logs:
            status = "✅ 등록됨" if log[2] else "❌ 미등록"
            text_widget.insert(tk.END, f"{log[3]} | {log[1]} | {status}\n")
        
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
            text="🎥 얼굴 인식 실행",
            font=("Arial", 24, "bold"),
            bg="#34495e",
            fg="white"
        ).pack(side=tk.LEFT, padx=20, pady=20)
        
        tk.Button(
            header,
            text="← 뒤로 가기",
            command=self.go_back,
            bg="#7f8c8d",
            fg="white",
            font=("Arial", 12, "bold"),
            cursor="hand2"
        ).pack(side=tk.RIGHT, padx=20, pady=20)
        
        # 비디오 프레임
        video_container = tk.Frame(self, bg="black")
        video_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.video_label = tk.Label(
            video_container,
            bg="black",
            text="카메라 대기 중...\n\n'시작' 버튼을 눌러주세요",
            fg="white",
            font=("Arial", 16)
        )
        self.video_label.pack(fill=tk.BOTH, expand=True)
        
        # 컨트롤 버튼
        control_frame = tk.Frame(self, bg="#2c3e50")
        control_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.start_button = tk.Button(
            control_frame,
            text="▶️ 시작",
            command=self.start_recognition,
            bg="#27ae60",
            fg="white",
            font=("Arial", 14, "bold"),
            cursor="hand2",
            width=20,
            height=2
        )
        self.start_button.pack(side=tk.LEFT, padx=10)
        
        self.stop_button = tk.Button(
            control_frame,
            text="⏹️ 정지",
            command=self.stop_recognition,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 14, "bold"),
            cursor="hand2",
            width=20,
            height=2,
            state=tk.DISABLED
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
        self.status_label.config(text="⚡ 실행 중...", fg="#27ae60")
        
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
        """비디오 처리 (실제 인식 로직은 원본 코드와 동일)"""
        # ... (원본 process_video 로직을 여기에 통합)
        print("[INFO] 비디오 처리 시작 - 간략화된 버전")
        
        frame_count = 0
        
        while self.is_running:
            ret, frame = self.video_capture.read()
            if not ret:
                print("[ERROR] 프레임을 읽을 수 없습니다.")
                break
            
            frame_count += 1
            
            # 간단한 표시 (실제로는 얼굴 인식 로직 필요)
            display_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            display_frame = cv2.resize(display_frame, (960, 540))
            img = Image.fromarray(display_frame)
            imgtk = ImageTk.PhotoImage(image=img)
            
            if self.is_running:
                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk, text="")
            
            time.sleep(0.03)  # ~30 FPS
        
        print("[INFO] 비디오 처리 종료")
