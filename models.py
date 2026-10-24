"""Small data objects used by the school management application."""
from dataclasses import dataclass, asdict


@dataclass
class Student:
    student_id: str
    full_name: str
    class_name: str
    section: str
    age: int
    gender: str
    contact_number: str

    def to_dict(self):
        return asdict(self)


@dataclass
class Teacher:
    teacher_id: str
    name: str
    subject: str
    qualification: str
    contact_number: str

    def to_dict(self):
        return asdict(self)


@dataclass
class Attendance:
    student_id: str
    student_name: str
    attendance_date: str
    status: str

    def to_dict(self):
        return asdict(self)


@dataclass
class Result:
    result_id: str
    student_id: str
    student_name: str
    examination: str
    subject: str
    marks_obtained: float
    maximum_marks: float
    percentage: float
    grade: str

    def to_dict(self):
        return asdict(self)
