from datetime import datetime
from models import Attendance


class AttendanceManager:
    def __init__(self, files): self.files = files
    def all(self): return [Attendance(**r) for r in self.files.read_all("attendance")]
    def add(self, attendance):
        datetime.strptime(attendance.attendance_date, "%Y-%m-%d")
        rows = self.files.read_all("attendance")
        if any(r["student_id"] == attendance.student_id and r["attendance_date"] == attendance.attendance_date for r in rows): raise ValueError("Attendance is already recorded for this student and date.")
        rows.append(attendance.to_dict()); self.files.write_all("attendance", rows)
    def percentage(self, student_id):
        records = [r for r in self.files.read_all("attendance") if r["student_id"] == student_id]
        return (sum(r["status"] == "Present" for r in records) / len(records) * 100) if records else 0.0
