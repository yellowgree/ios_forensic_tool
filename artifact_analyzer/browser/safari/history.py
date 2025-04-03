import os
import sqlite3
import datetime
from artifact_analyzer.call.backuphelper import BackupPathHelper

def find_safari_history(backup_path=None):
    """
    Safari 방문 기록 데이터베이스 (History.db) 파일 경로 찾기
    """
    if backup_path:
        backup_helper = BackupPathHelper(backup_path)
        safari_paths = [
            "Library/Safari/History.db",
            "private/var/mobile/Library/Safari/History.db",
            "HomeDomain/Library/Safari/History.db"
        ]
        
        # 1. Manifest.db에서 찾기
        for path in safari_paths:
            file_path = backup_helper.get_file_path_from_manifest(path)
            if file_path and os.path.exists(file_path):
                return file_path
        
        # # 2. 알려진 도메인과 경로 조합으로 해시값 계산해서 찾기
        # domains = ["HomeDomain", "PrivateDomain", "AppDomain-com.apple.mobilesafari"]
        # for domain in domains:
        #     for path in safari_paths:
        #         file_path = backup_helper.compute_hash_path(domain, path)
        #         if file_path:
        #             return file_path
        
        # 3. 모든 파일 검사 (느리지만 확실한 방법)
        # return backup_helper.find_sqlite_with_tables(["history_items"])
    

    
    return None


def get_safari_history(backup_path=None):
    db_path = find_safari_history(backup_path)
    if not db_path:
        return "Safari 기록 데이터베이스를 찾을 수 없습니다."
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""SELECT url, title, visit_time
                        FROM history_visits
                        JOIN history_items ON history_visits.history_item = history_items.id
                        ORDER BY visit_time DESC;""")
        
        history = []
        for row in cursor.fetchall():
            url = row[0]
            title = row[1]
            timestamp = row[2]
            visit_time = datetime.datetime(2001, 1, 1) + datetime.timedelta(seconds=timestamp)
            formatted_time = visit_time.strftime('%Y-%m-%d %H:%M:%S')
            history.append((title, url, formatted_time))
        
        conn.close()
        return history if history else "기록이 없습니다."
    except Exception as e:
        return f"오류 발생: {e}"
