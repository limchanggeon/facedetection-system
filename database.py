import sqlite3
import pickle
import os

class FaceDatabase:
    def __init__(self, db_name="face_recognition.db"):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.init_database()
    
    def init_database(self):
        """데이터베이스 초기화 및 테이블 생성"""
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        
        # 등록된 얼굴 테이블 (이름, 학번, 학과, 학년 추가)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS registered_faces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                student_id TEXT UNIQUE NOT NULL,
                department TEXT NOT NULL,
                grade TEXT NOT NULL,
                encoding BLOB NOT NULL,
                registered_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 인식 로그 테이블 (등록된 사람, 미등록 모두 기록)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS recognition_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                student_id TEXT,
                is_registered INTEGER NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
    
    def add_face(self, name, student_id, department, grade, encoding):
        """새로운 얼굴 등록 (이름, 학번, 학과, 학년)"""
        try:
            encoding_blob = pickle.dumps(encoding)
            self.cursor.execute(
                "INSERT INTO registered_faces (name, student_id, department, grade, encoding) VALUES (?, ?, ?, ?, ?)",
                (name, student_id, department, grade, encoding_blob)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # 이미 존재하는 학번
    
    def get_all_faces(self):
        """모든 등록된 얼굴 정보 가져오기"""
        self.cursor.execute("SELECT name, student_id, department, grade, encoding FROM registered_faces")
        results = self.cursor.fetchall()
        
        names = []
        student_ids = []
        departments = []
        grades = []
        encodings = []
        
        for name, student_id, department, grade, encoding_blob in results:
            names.append(name)
            student_ids.append(student_id)
            departments.append(department)
            grades.append(grade)
            encodings.append(pickle.loads(encoding_blob))
        
        return {
            "names": names,
            "student_ids": student_ids,
            "departments": departments,
            "grades": grades,
            "encodings": encodings
        }
    
    def get_person_info(self, student_id):
        """학번으로 개인 정보 조회"""
        self.cursor.execute(
            "SELECT name, student_id, department, grade FROM registered_faces WHERE student_id = ?",
            (student_id,)
        )
        result = self.cursor.fetchone()
        if result:
            return {
                "name": result[0],
                "student_id": result[1],
                "department": result[2],
                "grade": result[3]
            }
        return None
    
    def delete_face(self, student_id):
        """등록된 얼굴 삭제 (학번으로)"""
        self.cursor.execute("DELETE FROM registered_faces WHERE student_id = ?", (student_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def log_recognition(self, name, student_id, is_registered):
        """얼굴 인식 로그 저장"""
        self.cursor.execute(
            "INSERT INTO recognition_logs (name, student_id, is_registered) VALUES (?, ?, ?)",
            (name, student_id if is_registered else None, 1 if is_registered else 0)
        )
        self.conn.commit()
    
    def get_recognition_logs(self, limit=100):
        """최근 인식 로그 가져오기"""
        self.cursor.execute(
            "SELECT id, name, student_id, is_registered, timestamp FROM recognition_logs ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        return self.cursor.fetchall()
    
    def get_registered_count(self):
        """등록된 얼굴 수"""
        self.cursor.execute("SELECT COUNT(*) FROM registered_faces")
        return self.cursor.fetchone()[0]
    
    def close(self):
        """데이터베이스 연결 종료"""
        if self.conn:
            self.conn.close()
