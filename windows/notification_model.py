import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import datetime, timedelta
import time
import threading

class NotificationModel:
    def __init__(self, db_path='files/timetable.db'):
        self.db_path = db_path
        self._stop_flag = False
        self._notification_thread = None

    def connect_db(self):
        """Connect to the database"""
        return sqlite3.connect(self.db_path)

    def show_notification(self, title, message):
        """Show a notification using Tkinter messagebox"""
        def show():
            messagebox.showinfo(title, message)
        # Run in main thread to avoid Tkinter threading issues
        if threading.current_thread() is threading.main_thread():
            show()
        else:
            tk._default_root.after(0, show)

    def notify_upcoming_class(self, user_id, user_type='student'):
        """Notify about upcoming classes"""
        conn = self.connect_db()
        current_time = datetime.now()
        day_of_week = current_time.weekday()  # Monday is 0
        
        if day_of_week >= 5:  # Weekend
            return
        
        current_hour = current_time.hour
        current_minute = current_time.minute
        
        # Map periods to time slots (adjust these according to your schedule)
        period_times = {
            0: (9, 0),   # 9:00 AM
            1: (10, 0),  # 10:00 AM
            2: (11, 0),  # 11:00 AM
            3: (12, 0),  # 12:00 PM
            4: (2, 0),   # 2:00 PM
            5: (3, 0),   # 3:00 PM
        }
        
        try:
            if user_type.lower() == 'student':
                # Get student's section
                cursor = conn.execute(f"SELECT SECTION FROM STUDENT WHERE SID='{user_id}'")
                student_data = cursor.fetchone()
                if not student_data:
                    return
                
                section = student_data[0]
                
                # Get upcoming classes for the student's section
                for period, (hour, minute) in period_times.items():
                    # Check if class is within next 15 minutes
                    class_time = datetime.now().replace(hour=hour, minute=minute, second=0)
                    time_diff = (class_time - current_time).total_seconds() / 60
                    
                    if 0 <= time_diff <= 15:
                        cursor = conn.execute(f"""
                            SELECT SCHEDULE.SUBCODE, SUBJECTS.SUBNAME, SCHEDULE.FINI, FACULTY.NAME
                            FROM SCHEDULE 
                            JOIN SUBJECTS ON SCHEDULE.SUBCODE = SUBJECTS.SUBCODE
                            JOIN FACULTY ON SCHEDULE.FINI = FACULTY.INI
                            WHERE SECTION='{section}' AND DAYID={day_of_week} AND PERIODID={period}
                        """)
                        class_data = cursor.fetchone()
                        
                        if class_data:
                            title = f"Upcoming Class Alert"
                            message = f"You have {class_data[1]} ({class_data[0]}) in {int(time_diff)} minutes!\nFaculty: {class_data[3]}\nPeriod: {period + 1}"
                            self.show_notification(title, message)
            
            elif user_type.lower() == 'faculty':
                # Get faculty's classes
                for period, (hour, minute) in period_times.items():
                    # Check if class is within next 15 minutes
                    class_time = datetime.now().replace(hour=hour, minute=minute, second=0)
                    time_diff = (class_time - current_time).total_seconds() / 60
                    
                    if 0 <= time_diff <= 15:
                        cursor = conn.execute(f"""
                            SELECT SCHEDULE.SUBCODE, SUBJECTS.SUBNAME, SCHEDULE.SECTION
                            FROM SCHEDULE 
                            JOIN SUBJECTS ON SCHEDULE.SUBCODE = SUBJECTS.SUBCODE
                            WHERE FINI=(SELECT INI FROM FACULTY WHERE FID='{user_id}')
                            AND DAYID={day_of_week} AND PERIODID={period}
                        """)
                        class_data = cursor.fetchone()
                        
                        if class_data:
                            title = f"Upcoming Class Alert"
                            message = f"You have {class_data[1]} ({class_data[0]}) in {int(time_diff)} minutes!\nSection: {class_data[2]}\nPeriod: {period + 1}"
                            self.show_notification(title, message)
                            
        finally:
            conn.close()

    def start_notification_service(self, user_id, user_type='student'):
        """Start the notification service in a background thread"""
        def notification_loop():
            while not self._stop_flag:
                self.notify_upcoming_class(user_id, user_type)
                time.sleep(300)  # Check every 5 minutes

        self._stop_flag = False
        self._notification_thread = threading.Thread(target=notification_loop)
        self._notification_thread.daemon = True
        self._notification_thread.start()

    def stop_notification_service(self):
        """Stop the notification service"""
        self._stop_flag = True
        if self._notification_thread:
            self._notification_thread.join()
            self._notification_thread = None

# Example usage:
if __name__ == "__main__":
    notifier = NotificationModel()
    notifier.show_notification("Test", "Test notification!") 