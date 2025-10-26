import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import cv2
from PIL import Image, ImageTk, ImageDraw, ImageFont
import face_recognition
import threading
import time
import numpy as np
from database import FaceDatabase

class FaceRecognitionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("얼굴 인식 시스템")
        self.root.geometry("1920x1080")
        
        # 데이터베이스 초기화
        self.db = FaceDatabase()
        
        # 비디오 캡처 관련 변수
        self.video_capture = None
        self.is_running = False
        self.current_frame = None
        
        # 얼굴 인식 관련 변수
        self.known_faces = {"names": [], "encodings": []}
        self.load_known_faces()
        
        # 로그 저장을 위한 변수 (중복 방지)
        self.last_logged_names = {}
        self.log_cooldown = 5  # 같은 사람을 5초마다 한 번만 로그
        
        # 한글 폰트 설정
        try:
            # macOS 시스템 폰트 사용
            self.font = ImageFont.truetype("/System/Library/Fonts/AppleSDGothicNeo.ttc", 30)
            self.font_small = ImageFont.truetype("/System/Library/Fonts/AppleSDGothicNeo.ttc", 20)
        except:
            try:
                self.font = ImageFont.truetype("/Library/Fonts/Arial Unicode.ttf", 30)
                self.font_small = ImageFont.truetype("/Library/Fonts/Arial Unicode.ttf", 20)
            except:
                print("[WARNING] 한글 폰트를 찾을 수 없습니다. 기본 폰트 사용")
                self.font = ImageFont.load_default()
                self.font_small = ImageFont.load_default()
        
        # GUI 구성
        self.setup_gui()
        
        # 종료 시 정리
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_gui(self):
        """GUI 레이아웃 구성"""
        # 상단 프레임 (제목 및 통계)
        top_frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        top_frame.pack(fill=tk.X, side=tk.TOP)
        
        title_label = tk.Label(
            top_frame, 
            text="실시간 얼굴 인식 시스템", 
            font=("Arial", 24, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title_label.pack(pady=20)
        
        # 메인 컨테이너
        main_container = tk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 왼쪽 패널 (비디오 및 컨트롤)
        left_panel = tk.Frame(main_container, bg="#ecf0f1")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # 비디오 디스플레이 (크기 10% 증가: 1056x594)
        video_frame = tk.Frame(left_panel, bg="black", relief=tk.SUNKEN, bd=2, width=1056, height=594)
        video_frame.pack(padx=10, pady=(10, 5), fill=tk.NONE, expand=False)
        video_frame.pack_propagate(False)  # 크기 고정
        
        self.video_label = tk.Label(video_frame, bg="black", text="카메라 대기 중...", fg="white", font=("Arial", 16))
        self.video_label.pack(fill=tk.BOTH, expand=True)
        
        # 컨트롤 버튼 (비디오 프레임 아래 고정)
        control_frame = tk.Frame(left_panel, bg="#ecf0f1", height=80)
        control_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        control_frame.pack_propagate(False)
        
        self.start_button = tk.Button(
            control_frame,
            text="얼굴 인식 시작",
            command=self.start_recognition,
            bg="#2ecc71",
            fg="#1a1a1a",
            activeforeground="#1a1a1a",
            activebackground="#27ae60",
            font=("Arial", 14, "bold"),
            height=2,
            cursor="hand2"
        )
        self.start_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.stop_button = tk.Button(
            control_frame,
            text="정지",
            command=self.stop_recognition,
            bg="#ff6b6b",
            fg="#1a1a1a",
            activeforeground="#1a1a1a",
            activebackground="#e74c3c",
            font=("Arial", 14, "bold"),
            height=2,
            state=tk.DISABLED,
            cursor="hand2"
        )
        self.stop_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 오른쪽 패널 (등록 및 관리)
        right_panel = tk.Frame(main_container, bg="#ecf0f1", width=550)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))
        right_panel.pack_propagate(False)
        
        # 통계 정보
        stats_frame = tk.LabelFrame(
            right_panel,
            text="통계",
            font=("Arial", 16, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50"
        )
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.stats_label = tk.Label(
            stats_frame,
            text=f"등록된 얼굴: {self.db.get_registered_count()}명",
            font=("Arial", 14),
            bg="#ecf0f1",
            justify=tk.LEFT
        )
        self.stats_label.pack(pady=10, padx=10)
        
        # 얼굴 등록 섹션
        register_frame = tk.LabelFrame(
            right_panel,
            text="얼굴 등록",
            font=("Arial", 16, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50"
        )
        register_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(
            register_frame,
            text="새 얼굴 등록",
            command=self.register_new_face,
            bg="#5dade2",
            fg="#1a1a1a",
            activeforeground="#1a1a1a",
            activebackground="#3498db",
            font=("Arial", 14, "bold"),
            height=2,
            cursor="hand2"
        ).pack(fill=tk.X, padx=10, pady=10)
        
        # 등록된 얼굴 목록
        list_frame = tk.LabelFrame(
            right_panel,
            text="등록된 얼굴 목록",
            font=("Arial", 16, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50"
        )
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 스크롤바가 있는 리스트박스
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.face_listbox = tk.Listbox(
            list_frame,
            font=("Arial", 14),
            yscrollcommand=scrollbar.set,
            selectmode=tk.SINGLE
        )
        self.face_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.config(command=self.face_listbox.yview)
        
        # 삭제 버튼
        tk.Button(
            list_frame,
            text="선택한 얼굴 삭제",
            command=self.delete_selected_face,
            bg="#f39c12",
            fg="#1a1a1a",
            activeforeground="#1a1a1a",
            activebackground="#e67e22",
            font=("Arial", 13, "bold"),
            cursor="hand2"
        ).pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # 목록 업데이트
        self.update_face_list()
    
    def load_known_faces(self):
        """데이터베이스에서 등록된 얼굴 로드"""
        self.known_faces = self.db.get_all_faces()
        print(f"[INFO] {len(self.known_faces['names'])}명의 얼굴을 로드했습니다.")
    
    def update_face_list(self):
        """등록된 얼굴 목록 업데이트"""
        self.face_listbox.delete(0, tk.END)
        for name in self.known_faces["names"]:
            self.face_listbox.insert(tk.END, name)
        
        # 통계 업데이트
        self.stats_label.config(text=f"등록된 얼굴: {len(self.known_faces['names'])}명")
    
    def register_new_face(self):
        """새로운 얼굴 등록"""
        name = simpledialog.askstring("이름 입력", "등록할 사람의 이름을 입력하세요:")
        
        if not name:
            return
        
        # 이미 등록된 이름인지 확인
        if name in self.known_faces["names"]:
            messagebox.showerror("오류", f"'{name}'은(는) 이미 등록된 이름입니다.")
            return
        
        # 웹캠 열기
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("오류", "웹캠을 열 수 없습니다.")
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
                f"등록 중: {name}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )
            cv2.putText(
                display_frame,
                "SPACE: 촬영 | ESC: 취소",
                (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )
            
            cv2.imshow("얼굴 등록", display_frame)
            
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
            if self.db.add_face(name, encoding):
                messagebox.showinfo("성공", f"'{name}'이(가) 성공적으로 등록되었습니다!")
                self.load_known_faces()
                self.update_face_list()
            else:
                messagebox.showerror("오류", "얼굴 등록에 실패했습니다.")
    
    def delete_selected_face(self):
        """선택된 얼굴 삭제"""
        selection = self.face_listbox.curselection()
        if not selection:
            messagebox.showwarning("경고", "삭제할 얼굴을 선택하세요.")
            return
        
        name = self.face_listbox.get(selection[0])
        
        if messagebox.askyesno("확인", f"'{name}'을(를) 삭제하시겠습니까?"):
            if self.db.delete_face(name):
                messagebox.showinfo("성공", f"'{name}'이(가) 삭제되었습니다.")
                self.load_known_faces()
                self.update_face_list()
            else:
                messagebox.showerror("오류", "삭제에 실패했습니다.")
    
    def start_recognition(self):
        """얼굴 인식 시작"""
        if len(self.known_faces["names"]) == 0:
            if not messagebox.askyesno("경고", "등록된 얼굴이 없습니다.\n\n그래도 카메라를 시작하시겠습니까?"):
                return
        
        print("[INFO] 얼굴 인식을 시작합니다...")
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # 비디오 캡처 시작
        self.video_capture = cv2.VideoCapture(0)
        
        if not self.video_capture.isOpened():
            messagebox.showerror("오류", "웹캠을 열 수 없습니다!")
            self.stop_recognition()
            return
        
        print("[INFO] 웹캠이 성공적으로 열렸습니다.")
        
        # 비디오 레이블에 초기 메시지 표시
        self.video_label.config(text="카메라 시작 중...", fg="white", bg="black")
        
        # 별도 스레드에서 비디오 처리
        threading.Thread(target=self.process_video, daemon=True).start()
    
    def stop_recognition(self):
        """얼굴 인식 정지"""
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        if self.video_capture:
            self.video_capture.release()
            self.video_capture = None
        
        # 비디오 레이블 초기화
        self.video_label.config(image="", text="정지됨", fg="white")
    
    def process_video(self):
        """비디오 프레임 처리 및 얼굴 인식"""
        process_every_n_frames = 3  # 성능 최적화: 매 3 프레임마다 얼굴 인식
        frame_count = 0
        
        # 이전 프레임의 얼굴 정보 저장 (부드러운 표시를 위해)
        previous_face_locations = []
        previous_face_names = []
        
        # 부드러운 이동을 위한 변수
        smoothed_face_locations = []  # 보간된 위치
        target_face_locations = []    # 목표 위치
        smoothing_factor = 0.3        # 부드러움 정도 (0.1~0.5, 낮을수록 부드러움)
        
        print("[INFO] 비디오 처리 시작...")
        
        while self.is_running:
            ret, frame = self.video_capture.read()
            if not ret:
                print("[ERROR] 프레임을 읽을 수 없습니다.")
                break
            
            frame_count += 1
            
            # 매 N 프레임마다 얼굴 인식 수행
            if frame_count % process_every_n_frames == 0:
                # 처리 속도를 위해 프레임 크기 축소
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                
                # 얼굴 위치 및 인코딩
                try:
                    face_locations = face_recognition.face_locations(rgb_small_frame, model="hog")
                    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                except Exception as e:
                    print(f"[ERROR] 얼굴 인식 오류: {e}")
                    continue
                
                face_names = []
                
                for face_encoding in face_encodings:
                    name = "Unknown"
                    
                    if len(self.known_faces["encodings"]) > 0:
                        try:
                            matches = face_recognition.compare_faces(
                                self.known_faces["encodings"],
                                face_encoding,
                                tolerance=0.5  # 더 엄격한 매칭
                            )
                            
                            if True in matches:
                                # 거리 계산으로 가장 가까운 얼굴 찾기
                                face_distances = face_recognition.face_distance(
                                    self.known_faces["encodings"], 
                                    face_encoding
                                )
                                best_match_index = face_distances.argmin()
                                
                                if matches[best_match_index]:
                                    name = self.known_faces["names"][best_match_index]
                                    
                                    # 등록된 사람 로그
                                    current_time = time.time()
                                    if name not in self.last_logged_names or \
                                       (current_time - self.last_logged_names[name]) > self.log_cooldown:
                                        try:
                                            self.db.log_recognition(name, True)
                                            self.last_logged_names[name] = current_time
                                        except Exception as e:
                                            print(f"[WARNING] 로그 저장 실패: {e}")
                        except Exception as e:
                            print(f"[ERROR] 얼굴 비교 오류: {e}")
                    
                    # Unknown 로그
                    if name == "Unknown":
                        if "Unknown" not in self.last_logged_names or \
                           (time.time() - self.last_logged_names["Unknown"]) > self.log_cooldown:
                            try:
                                self.db.log_recognition("Unknown", False)
                                self.last_logged_names["Unknown"] = time.time()
                            except Exception as e:
                                print(f"[WARNING] 로그 저장 실패: {e}")
                    
                    face_names.append(name)
                
                # 목표 위치 업데이트
                target_face_locations = [(t*4, r*4, b*4, l*4) for (t, r, b, l) in face_locations]
                previous_face_names = face_names
                
                # 첫 프레임이거나 얼굴 수가 변경된 경우 즉시 업데이트
                if len(smoothed_face_locations) != len(target_face_locations):
                    smoothed_face_locations = target_face_locations.copy()
            
            # 부드러운 이동 적용 (선형 보간)
            if len(smoothed_face_locations) > 0 and len(target_face_locations) > 0:
                for i in range(len(smoothed_face_locations)):
                    if i < len(target_face_locations):
                        st, sr, sb, sl = smoothed_face_locations[i]
                        tt, tr, tb, tl = target_face_locations[i]
                        
                        # 선형 보간으로 부드럽게 이동
                        smoothed_face_locations[i] = (
                            int(st + (tt - st) * smoothing_factor),
                            int(sr + (tr - sr) * smoothing_factor),
                            int(sb + (tb - sb) * smoothing_factor),
                            int(sl + (tl - sl) * smoothing_factor)
                        )
            
            # OpenCV BGR을 RGB로 변환 (한글 표시를 위해 PIL 사용)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_frame)
            draw = ImageDraw.Draw(pil_image)
            
            # 바운딩 박스 그리기 (부드럽게 이동하는 위치 사용)
            for i, (top, right, bottom, left) in enumerate(smoothed_face_locations):
                if i >= len(previous_face_names):
                    break
                    
                name = previous_face_names[i]
                
                # 바운딩 박스 색상 (등록: 녹색, 미등록: 빨강)
                color = (0, 255, 0) if name != "Unknown" else (255, 0, 0)  # RGB for PIL
                
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
                
                # 한글 이름 텍스트 (검은색으로 변경하여 가시성 향상)
                draw.text(
                    (left + 10, bottom - text_height - 10),
                    name,
                    font=self.font_small,
                    fill=(0, 0, 0)  # 검은색
                )
            
            # 상태 정보 표시
            info_text = f"얼굴: {len(previous_face_names)}명"
            draw.text((10, 10), info_text, font=self.font_small, fill=(255, 255, 255))
            
            # PIL Image를 다시 numpy 배열로 변환
            frame = np.array(pil_image)
            
            # FPS 계산 및 표시
            if frame_count == 1:
                fps_start_time = time.time()
            
            if frame_count % 30 == 0 and frame_count > 1:
                fps = 30 / (time.time() - fps_start_time)
                fps_start_time = time.time()
                print(f"[INFO] FPS: {fps:.1f}, 인식된 얼굴: {len(previous_face_names)}명")
            
            # PIL Image로 변환 (이미 RGB)
            img = Image.fromarray(frame)
            
            # 비디오 프레임에 맞게 리사이즈 (1056x594)
            img = img.resize((1056, 594), Image.Resampling.LANCZOS)
            
            # PhotoImage로 변환
            photo = ImageTk.PhotoImage(image=img)
            
            # GUI 업데이트 (메인 스레드에서 안전하게)
            try:
                self.video_label.config(image=photo, text="", bg="black")
                self.video_label.image = photo
            except Exception as e:
                print(f"[ERROR] GUI 업데이트 오류: {e}")
                break
            
            # 첫 프레임 표시 확인
            if frame_count == 1:
                print("[INFO] 첫 프레임이 표시되었습니다!")
            
            time.sleep(0.01)
        
        print("[INFO] 비디오 처리 종료")
    
    def on_closing(self):
        """앱 종료 시 정리"""
        self.is_running = False
        if self.video_capture:
            self.video_capture.release()
        self.db.close()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = FaceRecognitionApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
