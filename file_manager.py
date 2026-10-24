"""CSV-based text file persistence. Each data file remains human-readable."""
import csv
import os
import tempfile


class FileManager:
    HEADERS = {
        "students": ["student_id", "full_name", "class_name", "section", "age", "gender", "contact_number"],
        "teachers": ["teacher_id", "name", "subject", "qualification", "contact_number"],
        "attendance": ["student_id", "student_name", "attendance_date", "status"],
        "results": ["result_id", "student_id", "student_name", "examination", "subject", "marks_obtained", "maximum_marks", "percentage", "grade"],
    }

    def __init__(self, data_dir=None):
        self.data_dir = data_dir or os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        os.makedirs(self.data_dir, exist_ok=True)
        for name, headers in self.HEADERS.items():
            path = self.path_for(name)
            if not os.path.exists(path):
                self.write_all(name, [])

    def path_for(self, name):
        if name not in self.HEADERS:
            raise ValueError("Unknown data collection")
        return os.path.join(self.data_dir, name + ".txt")

    def read_all(self, name):
        headers = self.HEADERS[name]
        path = self.path_for(name)
        try:
            with open(path, "r", newline="", encoding="utf-8-sig") as handle:
                reader = csv.DictReader(handle)
                if reader.fieldnames is None:
                    return []
                missing = set(headers) - set(reader.fieldnames)
                if missing:
                    # A non-empty but incompatible file must never be overwritten silently.
                    raise ValueError(f"{os.path.basename(path)} has an unexpected header")
                rows = []
                for line_number, row in enumerate(reader, start=2):
                    if not row or any(row.get(key) is None for key in headers):
                        print(f"Skipping malformed {name} record at line {line_number}.")
                        continue
                    rows.append({key: row[key] for key in headers})
                return rows
        except FileNotFoundError:
            return []
        except (OSError, csv.Error) as exc:
            raise OSError(f"Could not read {path}: {exc}") from exc

    def write_all(self, name, rows):
        headers = self.HEADERS[name]
        path = self.path_for(name)
        temp_path = None
        try:
            fd, temp_path = tempfile.mkstemp(prefix=name + "_", suffix=".tmp", dir=self.data_dir, text=True)
            with os.fdopen(fd, "w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=headers, extrasaction="ignore")
                writer.writeheader()
                writer.writerows(rows)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_path, path)
        except (OSError, csv.Error) as exc:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
            raise OSError(f"Could not save {path}: {exc}") from exc
