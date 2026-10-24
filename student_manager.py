from models import Student


class StudentManager:
    def __init__(self, files): self.files = files
    def all(self): return [Student(**r) for r in self.files.read_all("students")]
    def add(self, student):
        rows = self.files.read_all("students")
        if any(r["student_id"].casefold() == student.student_id.casefold() for r in rows): raise ValueError("Student ID already exists.")
        rows.append(student.to_dict()); self.files.write_all("students", rows)
    def update(self, student, old_id):
        rows = self.files.read_all("students")
        if student.student_id.casefold() != old_id.casefold() and any(r["student_id"].casefold() == student.student_id.casefold() for r in rows): raise ValueError("Student ID already exists.")
        for i, row in enumerate(rows):
            if row["student_id"] == old_id: rows[i] = student.to_dict(); self.files.write_all("students", rows); return
        raise ValueError("Student record was not found.")
    def delete(self, student_id):
        rows = self.files.read_all("students"); kept = [r for r in rows if r["student_id"] != student_id]
        if len(rows) == len(kept): raise ValueError("Student record was not found.")
        self.files.write_all("students", kept)
