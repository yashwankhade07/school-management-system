from models import Teacher


class TeacherManager:
    def __init__(self, files): self.files = files
    def all(self): return [Teacher(**r) for r in self.files.read_all("teachers")]
    def add(self, teacher):
        rows = self.files.read_all("teachers")
        if any(r["teacher_id"].casefold() == teacher.teacher_id.casefold() for r in rows): raise ValueError("Teacher ID already exists.")
        rows.append(teacher.to_dict()); self.files.write_all("teachers", rows)
    def update(self, teacher, old_id):
        rows = self.files.read_all("teachers")
        if teacher.teacher_id.casefold() != old_id.casefold() and any(r["teacher_id"].casefold() == teacher.teacher_id.casefold() for r in rows): raise ValueError("Teacher ID already exists.")
        for i, row in enumerate(rows):
            if row["teacher_id"] == old_id: rows[i] = teacher.to_dict(); self.files.write_all("teachers", rows); return
        raise ValueError("Teacher record was not found.")
    def delete(self, teacher_id):
        rows = self.files.read_all("teachers"); kept = [r for r in rows if r["teacher_id"] != teacher_id]
        if len(rows) == len(kept): raise ValueError("Teacher record was not found.")
        self.files.write_all("teachers", kept)
