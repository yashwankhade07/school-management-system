# School Management System

A local desktop application for managing school students, teachers, attendance, and examination results. It uses Python's built-in Tkinter widgets and stores records in readable CSV-formatted `.txt` files.

## Features

- Student and teacher create, search, update, and delete operations
- Attendance recording by student and date, duplicate prevention, and attendance percentage
- Examination results with validated marks, calculated percentages, and grades
- Dashboard counts for students, teachers, attendance, and results
- CSV quoting protects names and other values containing commas
- Data files and the `data/` folder are created automatically on first launch

## Technologies and concepts

Python 3, Tkinter/ttk, `csv`, `dataclasses`, file handling, exception handling, classes, objects, lists, and dictionaries. No third-party packages or database are used.

## Folder structure

```text
SchoolManagementSystem/
  main.py
  gui.py
  models.py
  file_manager.py
  student_manager.py
  teacher_manager.py
  attendance_manager.py
  result_manager.py
  README.md
  data/
    students.txt
    teachers.txt
    attendance.txt
    results.txt
```

The four data files are generated when the app runs if they are missing. Each contains a header row followed by CSV-quoted records. Keep the files in `data/` to preserve records between runs. File updates are written to a temporary file and atomically replace the target only after a complete successful write.

## Run

From this folder, run:

```bash
python main.py
```

Python 3 with Tk support is required (the standard Windows Python installer includes Tkinter).

## Use

Choose a module from the left navigation. Enter the record fields and select **Save record**. Selecting a table row loads it into the form so it can be edited; use **Delete selected** to remove a selected student, teacher, or result after confirming. Attendance dates use `YYYY-MM-DD`; select a student and status before saving. In Results, enter a unique Result ID and marks; percentage and grade are computed automatically. Search filters update as you type. The dashboard refreshes when opened.

## OOP and storage design

`Student`, `Teacher`, `Attendance`, and `Result` are data classes representing records. Each manager owns the operations for its record type, while `FileManager` handles CSV text file reads and writes independently of the GUI. `SchoolManagementApp` builds the Tkinter interface and connects widgets to those managers.
