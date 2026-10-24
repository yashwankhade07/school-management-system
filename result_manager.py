from models import Result


class ResultManager:
    GRADES = ((90, "A+"), (80, "A"), (70, "B"), (60, "C"), (40, "D"), (0, "F"))
    @classmethod
    def grade_for(cls, percentage): return next(g for floor, g in cls.GRADES if percentage >= floor)
    def __init__(self, files): self.files = files
    def all(self): return [Result(**r) for r in self.files.read_all("results")]
    def add(self, result):
        rows = self.files.read_all("results")
        if any(r["result_id"].casefold() == result.result_id.casefold() for r in rows): raise ValueError("Result ID already exists.")
        rows.append(result.to_dict()); self.files.write_all("results", rows)
    def update(self, result, old_id):
        rows = self.files.read_all("results")
        if result.result_id.casefold() != old_id.casefold() and any(r["result_id"].casefold() == result.result_id.casefold() for r in rows): raise ValueError("Result ID already exists.")
        for i, row in enumerate(rows):
            if row["result_id"] == old_id: rows[i] = result.to_dict(); self.files.write_all("results", rows); return
        raise ValueError("Result record was not found.")
    def delete(self, result_id):
        rows = self.files.read_all("results"); kept = [r for r in rows if r["result_id"] != result_id]
        if len(rows) == len(kept): raise ValueError("Result record was not found.")
        self.files.write_all("results", kept)
