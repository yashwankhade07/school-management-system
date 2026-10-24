"""Tkinter screens for the School Management System."""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from models import Student, Teacher, Attendance, Result
from file_manager import FileManager
from student_manager import StudentManager
from teacher_manager import TeacherManager
from attendance_manager import AttendanceManager
from result_manager import ResultManager


class SchoolManagementApp:
    BG = "#f2f5f9"
    NAV = "#183153"
    ACCENT = "#2764a5"
    
    def __init__(self, root):
        self.root = root
        self.root.title("School Management System")
        self.root.geometry("1120x720")
        self.root.minsize(900, 600)
        self.root.configure(bg=self.BG)
        self.files = FileManager()
        self.students = StudentManager(self.files)
        self.teachers = TeacherManager(self.files)
        self.attendance = AttendanceManager(self.files)
        self.results = ResultManager(self.files)
        self.current_view = "Dashboard"
        self.form_vars = {}
        self.fields = []
        self.editing_id = None
        self._style()
        self._build_shell()
        self.show_dashboard()

    def _style(self):
        style = ttk.Style()
        try: style.theme_use("clam")
        except tk.TclError: pass
        style.configure("Treeview", rowheight=27, font=("Segoe UI", 10), background="white", fieldbackground="white")
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#dce6f1")
        style.configure("TCombobox", padding=5)

    def _build_shell(self):
        self.nav = tk.Frame(self.root, bg=self.NAV, width=190)
        self.nav.pack(side="left", fill="y")
        self.nav.pack_propagate(False)
        tk.Label(self.nav, text="SCHOOL\nMANAGEMENT", bg=self.NAV, fg="white", font=("Segoe UI", 16, "bold"), justify="left", pady=24).pack(fill="x", padx=18)
        for label, callback in [("Dashboard", self.show_dashboard), ("Students", self.show_students), ("Teachers", self.show_teachers), ("Attendance", self.show_attendance), ("Results", self.show_results)]:
            tk.Button(self.nav, text=label, command=callback, anchor="w", padx=20, pady=12, relief="flat", bd=0, bg=self.NAV, fg="white", activebackground="#29486c", activeforeground="white", font=("Segoe UI", 11)).pack(fill="x", padx=8, pady=2)
        tk.Button(self.nav, text="Exit", command=self.exit_app, anchor="w", padx=20, pady=12, relief="flat", bd=0, bg=self.NAV, fg="white", activebackground="#29486c", activeforeground="white", font=("Segoe UI", 11)).pack(side="bottom", fill="x", padx=8, pady=12)
        self.main = tk.Frame(self.root, bg=self.BG)
        self.main.pack(side="left", fill="both", expand=True)

    def _clear(self):
        for child in self.main.winfo_children(): child.destroy()
        self.form_vars = {}; self.fields = []; self.editing_id = None

    def _heading(self, title, subtitle=None):
        header = tk.Frame(self.main, bg=self.BG)
        header.pack(fill="x", padx=28, pady=(24, 14))
        tk.Label(header, text=title, bg=self.BG, fg="#1f2d3d", font=("Segoe UI", 21, "bold")).pack(anchor="w")
        if subtitle: tk.Label(header, text=subtitle, bg=self.BG, fg="#607080", font=("Segoe UI", 10)).pack(anchor="w", pady=(4, 0))

    def _card(self, parent, title, value):
        box = tk.Frame(parent, bg="white", highlightbackground="#d8e0e8", highlightthickness=1, padx=22, pady=18)
        tk.Label(box, text=title, bg="white", fg="#617181", font=("Segoe UI", 10)).pack(anchor="w")
        tk.Label(box, text=str(value), bg="white", fg=self.ACCENT, font=("Segoe UI", 25, "bold")).pack(anchor="w", pady=(6, 0))
        return box

    def show_dashboard(self):
        self._clear(); self.current_view = "Dashboard"
        self._heading("School Management System", "Manage students, teachers, attendance, and examination results.")
        try:
            counts = [len(self.students.all()), len(self.teachers.all()), len(self.attendance.all()), len(self.results.all())]
        except (OSError, ValueError) as exc:
            messagebox.showerror("Data error", str(exc)); counts = [0, 0, 0, 0]
        cards = tk.Frame(self.main, bg=self.BG); cards.pack(fill="x", padx=28, pady=12)
        for idx, (title, count) in enumerate(zip(("Registered Students", "Registered Teachers", "Attendance Records", "Result Records"), counts)):
            self._card(cards, title, count).grid(row=0, column=idx, sticky="nsew", padx=(0 if idx == 0 else 10, 0))
            cards.grid_columnconfigure(idx, weight=1)
        tk.Label(self.main, text="Quick access", bg=self.BG, fg="#1f2d3d", font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=28, pady=(30, 10))
        actions = tk.Frame(self.main, bg=self.BG); actions.pack(anchor="w", padx=28)
        for title, callback in (("Open Students", self.show_students), ("Open Teachers", self.show_teachers), ("Mark Attendance", self.show_attendance), ("Enter Results", self.show_results)):
            ttk.Button(actions, text=title, command=callback).pack(side="left", padx=(0, 10), ipady=6)

    def _module(self, title, subtitle, fields, columns, loader, search_hint, save_handler, delete_handler=None, search_keys=None):
        self._clear(); self.current_view = title
        self.fields = fields
        self._heading(title, subtitle)
        form = tk.LabelFrame(self.main, text="Record details", bg="white", fg="#34495e", font=("Segoe UI", 10, "bold"), padx=12, pady=10)
        form.pack(fill="x", padx=28, pady=(0, 12))
        for i, (key, label, kind, options) in enumerate(fields):
            row, col = divmod(i, 4)
            tk.Label(form, text=label, bg="white", fg="#34495e", font=("Segoe UI", 9)).grid(row=row*2, column=col, sticky="w", padx=8, pady=(4, 2))
            var = tk.StringVar(); self.form_vars[key] = var
            if kind == "combo":
                widget = ttk.Combobox(form, textvariable=var, values=options, state="readonly", width=22)
            elif kind == "student":
                widget = ttk.Combobox(form, textvariable=var, state="readonly", width=22)
                self._refresh_student_choices(widget)
            else:
                widget = ttk.Entry(form, textvariable=var, width=25)
            widget.grid(row=row*2+1, column=col, sticky="ew", padx=8, pady=(0, 6))
            form.grid_columnconfigure(col, weight=1)
            if key == "attendance_date": var.set(date.today().isoformat())
        btns = tk.Frame(form, bg="white"); btns.grid(row=((len(fields)+3)//4)*2, column=0, columnspan=4, sticky="w", padx=8, pady=(5, 0))
        ttk.Button(btns, text="Save record", command=lambda: save_handler()).pack(side="left", padx=(0, 7))
        ttk.Button(btns, text="Clear form", command=self._reset_form).pack(side="left", padx=7)
        if delete_handler: ttk.Button(btns, text="Delete selected", command=lambda: delete_handler()).pack(side="left", padx=7)
        if title == "Attendance": ttk.Button(btns, text="Attendance %", command=self._show_attendance_percentage).pack(side="left", padx=7)

        searchbar = tk.Frame(self.main, bg=self.BG); searchbar.pack(fill="x", padx=28, pady=(0, 8))
        tk.Label(searchbar, text="Search", bg=self.BG, font=("Segoe UI", 10)).pack(side="left", padx=(0, 8))
        self.search_var = tk.StringVar()
        entry = ttk.Entry(searchbar, textvariable=self.search_var, width=34); entry.pack(side="left")
        entry.insert(0, "")
        self.search_var.trace_add("write", lambda *_: self._refresh_table(loader, columns, search_keys))
        ttk.Button(searchbar, text="Refresh", command=lambda: self._refresh_table(loader, columns, search_keys)).pack(side="left", padx=8)
        table_wrap = tk.Frame(self.main, bg=self.BG); table_wrap.pack(fill="both", expand=True, padx=28, pady=(0, 22))
        self.tree = ttk.Treeview(table_wrap, columns=[c[0] for c in columns], show="headings", selectmode="browse")
        for key, label, width in columns:
            self.tree.heading(key, text=label); self.tree.column(key, width=width, minwidth=70, anchor="w")
        yscroll = ttk.Scrollbar(table_wrap, orient="vertical", command=self.tree.yview); xscroll = ttk.Scrollbar(table_wrap, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        self.tree.grid(row=0, column=0, sticky="nsew"); yscroll.grid(row=0, column=1, sticky="ns"); xscroll.grid(row=1, column=0, sticky="ew")
        table_wrap.grid_rowconfigure(0, weight=1); table_wrap.grid_columnconfigure(0, weight=1)
        self.tree.bind("<<TreeviewSelect>>", self._select_record)
        self._refresh_table(loader, columns, search_keys)

    def _refresh_table(self, loader, columns, search_keys):
        if not hasattr(self, "tree") or not self.tree.winfo_exists(): return
        try: rows = loader()
        except (OSError, ValueError) as exc: messagebox.showerror("Data error", str(exc)); return
        query = getattr(self, "search_var", tk.StringVar()).get().strip().casefold()
        self.tree.delete(*self.tree.get_children())
        for row in rows:
            record = row.to_dict() if hasattr(row, "to_dict") else row
            if query and not any(query in str(record.get(key, "")).casefold() for key in search_keys or []): continue
            values = [record.get(key, "") for key, _, _ in columns]
            # The first column is not necessarily unique (one student has many
            # attendance dates), so let Treeview generate a unique row ID.
            self.tree.insert("", "end", values=values)

    def _select_record(self, _event=None):
        if not self.tree.selection(): return
        values = self.tree.item(self.tree.selection()[0], "values")
        if not values: return
        # Fill form fields from the selected table row, matching by field name.
        selected = self.tree.item(self.tree.selection()[0], "values")
        mapping = {c: v for c, v in zip(self.tree["columns"], selected)}
        for key, *_ in self.fields:
            if key in mapping:
                self.form_vars[key].set(mapping[key])
            elif key == "student" and "student_id" in mapping:
                # Student pickers display both the ID and name, while tables
                # store those in separate columns.
                try:
                    student = next(s for s in self.students.all() if s.student_id == mapping["student_id"])
                    self.form_vars[key].set(f"{student.student_id} — {student.full_name}")
                except (StopIteration, OSError, ValueError):
                    self.form_vars[key].set("")
        self.editing_id = str(values[0])

    def _reset_form(self):
        self.editing_id = None
        for key, var in self.form_vars.items():
            var.set(date.today().isoformat() if key == "attendance_date" else "")
        if hasattr(self, "tree") and self.tree.winfo_exists(): self.tree.selection_remove(self.tree.selection())

    def _refresh_student_choices(self, combo):
        try:
            records = self.students.all()
            combo.configure(values=[f"{s.student_id} — {s.full_name}" for s in records])
        except (OSError, ValueError) as exc: messagebox.showerror("Data error", str(exc))

    @staticmethod
    def _required(values):
        if any(not str(value).strip() for value in values): raise ValueError("Please complete all required fields.")

    def _save_student(self):
        try:
            v = {k: x.get().strip() for k, x in self.form_vars.items()}; self._required(v.values())
            if not v["age"].isdigit() or int(v["age"]) < 1: raise ValueError("Age must be a positive whole number.")
            obj = Student(v["student_id"], v["full_name"], v["class_name"], v["section"], int(v["age"]), v["gender"], v["contact_number"])
            if self.editing_id: self.students.update(obj, self.editing_id)
            else: self.students.add(obj)
            messagebox.showinfo("Saved", "Student record saved."); self._after_save()
        except (ValueError, OSError) as exc: messagebox.showerror("Unable to save", str(exc))

    def _save_teacher(self):
        try:
            v = {k: x.get().strip() for k, x in self.form_vars.items()}; self._required(v.values())
            obj = Teacher(**v)
            if self.editing_id: self.teachers.update(obj, self.editing_id)
            else: self.teachers.add(obj)
            messagebox.showinfo("Saved", "Teacher record saved."); self._after_save()
        except (ValueError, OSError) as exc: messagebox.showerror("Unable to save", str(exc))

    def _save_attendance(self):
        try:
            v = {k: x.get().strip() for k, x in self.form_vars.items()}; self._required(v.values())
            sid = v["student"].split(" — ", 1)[0]
            student = next((s for s in self.students.all() if s.student_id == sid), None)
            if not student: raise ValueError("Select a registered student first.")
            obj = Attendance(sid, student.full_name, v["attendance_date"], v["status"]); self.attendance.add(obj)
            messagebox.showinfo("Saved", "Attendance recorded."); self._after_save()
        except (ValueError, OSError) as exc: messagebox.showerror("Unable to save", str(exc))

    def _save_result(self):
        try:
            v = {k: x.get().strip() for k, x in self.form_vars.items()}; self._required(v.values())
            sid = v["student"].split(" — ", 1)[0]
            student = next((s for s in self.students.all() if s.student_id == sid), None)
            if not student: raise ValueError("Select a registered student first.")
            try: marks, maximum = float(v["marks_obtained"]), float(v["maximum_marks"])
            except ValueError as exc: raise ValueError("Marks must be numeric.") from exc
            if maximum <= 0 or marks < 0 or marks > maximum: raise ValueError("Marks must be between zero and a positive maximum mark.")
            percentage = marks / maximum * 100
            obj = Result(v["result_id"], sid, student.full_name, v["examination"], v["subject"], marks, maximum, round(percentage, 2), ResultManager.grade_for(percentage))
            if self.editing_id: self.results.update(obj, self.editing_id)
            else: self.results.add(obj)
            messagebox.showinfo("Saved", f"Result saved. Grade: {obj.grade}"); self._after_save()
        except (ValueError, OSError) as exc: messagebox.showerror("Unable to save", str(exc))

    def _after_save(self):
        self._reset_form()
        self._refresh_current()

    def _refresh_current(self):
        view = self.current_view
        if view == "Students": self.show_students()
        elif view == "Teachers": self.show_teachers()
        elif view == "Attendance": self.show_attendance()
        elif view == "Results": self.show_results()
        else: self.show_dashboard()

    def _delete_student(self):
        if not self.editing_id: messagebox.showwarning("Select a record", "Select a student row first."); return
        if messagebox.askyesno("Confirm deletion", "Delete this student record?"):
            try: self.students.delete(self.editing_id); messagebox.showinfo("Deleted", "Student record deleted."); self.show_students()
            except (ValueError, OSError) as exc: messagebox.showerror("Unable to delete", str(exc))

    def _delete_teacher(self):
        if not self.editing_id: messagebox.showwarning("Select a record", "Select a teacher row first."); return
        if messagebox.askyesno("Confirm deletion", "Delete this teacher record?"):
            try: self.teachers.delete(self.editing_id); messagebox.showinfo("Deleted", "Teacher record deleted."); self.show_teachers()
            except (ValueError, OSError) as exc: messagebox.showerror("Unable to delete", str(exc))

    def _delete_result(self):
        if not self.editing_id: messagebox.showwarning("Select a record", "Select a result row first."); return
        if messagebox.askyesno("Confirm deletion", "Delete this result record?"):
            try: self.results.delete(self.editing_id); messagebox.showinfo("Deleted", "Result record deleted."); self.show_results()
            except (ValueError, OSError) as exc: messagebox.showerror("Unable to delete", str(exc))

    def _show_attendance_percentage(self):
        chosen = self.form_vars.get("student")
        if not chosen or not chosen.get(): messagebox.showwarning("Select student", "Choose a student to calculate attendance."); return
        sid = chosen.get().split(" — ", 1)[0]
        try: pct = self.attendance.percentage(sid); messagebox.showinfo("Attendance percentage", f"Attendance: {pct:.1f}%")
        except (OSError, ValueError) as exc: messagebox.showerror("Data error", str(exc))

    def show_students(self):
        self._module("Students", "Add, find, update, and remove student records.", [("student_id", "Student ID", "text", None), ("full_name", "Full name", "text", None), ("class_name", "Class", "combo", [str(n) for n in range(1, 13)]), ("section", "Section", "text", None), ("age", "Age", "text", None), ("gender", "Gender", "combo", ["Female", "Male", "Other"]), ("contact_number", "Contact number", "text", None)], [("student_id", "Student ID", 100), ("full_name", "Full name", 180), ("class_name", "Class", 70), ("section", "Section", 75), ("age", "Age", 55), ("gender", "Gender", 85), ("contact_number", "Contact", 130)], self.students.all, "ID or name", self._save_student, self._delete_student, ["student_id", "full_name"])

    def show_teachers(self):
        self._module("Teachers", "Maintain teacher details and subject assignments.", [("teacher_id", "Teacher ID", "text", None), ("name", "Name", "text", None), ("subject", "Subject", "text", None), ("qualification", "Qualification", "text", None), ("contact_number", "Contact number", "text", None)], [("teacher_id", "Teacher ID", 100), ("name", "Name", 180), ("subject", "Subject", 140), ("qualification", "Qualification", 180), ("contact_number", "Contact", 140)], self.teachers.all, "ID or name", self._save_teacher, self._delete_teacher, ["teacher_id", "name"])

    def show_attendance(self):
        self._module("Attendance", "Mark daily attendance and review a student's attendance percentage.", [("student", "Student", "student", None), ("attendance_date", "Date (YYYY-MM-DD)", "text", None), ("status", "Status", "combo", ["Present", "Absent"])], [("student_id", "Student ID", 110), ("student_name", "Student name", 180), ("attendance_date", "Date", 120), ("status", "Status", 100)], self.attendance.all, "student ID or date", None, None, ["student_id", "attendance_date", "student_name"])

    def show_results(self):
        self._module("Results", "Record exam marks; percentages and grades are calculated automatically.", [("result_id", "Result ID", "text", None), ("student", "Student", "student", None), ("examination", "Examination", "text", None), ("subject", "Subject", "text", None), ("marks_obtained", "Marks obtained", "text", None), ("maximum_marks", "Maximum marks", "text", None)], [("result_id", "Result ID", 95), ("student_id", "Student ID", 95), ("student_name", "Student name", 150), ("examination", "Examination", 130), ("subject", "Subject", 115), ("marks_obtained", "Marks", 70), ("maximum_marks", "Out of", 70), ("percentage", "%", 70), ("grade", "Grade", 65)], self.results.all, "student ID or name", self._save_result, self._delete_result, ["student_id", "student_name"])

    def exit_app(self):
        if messagebox.askyesno("Exit", "Close the School Management System?"): self.root.destroy()


def run_app():
    root = tk.Tk()
    SchoolManagementApp(root)
    root.mainloop()
