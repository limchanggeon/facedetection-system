"""
멀티 화면 얼굴 인식 시스템 - 메인 애플리케이션
"""
import tkinter as tk
from gui_screens import ScreenManager

def main():
    root = tk.Tk()
    root.title("얼굴 인식 시스템 v2.0")
    root.geometry("1280x720")
    root.configure(bg="#2c3e50")
    
    # 화면 관리자 생성
    manager = ScreenManager(root)
    
    # 로비 화면으로 시작
    manager.show_screen('lobby')
    
    # 종료 시 정리
    def on_closing():
        # 실행 중인 인식이 있으면 정지
        if 'recognition' in manager.screens:
            recognition_screen = manager.screens['recognition']
            if recognition_screen.is_running:
                recognition_screen.stop_recognition()
        
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
