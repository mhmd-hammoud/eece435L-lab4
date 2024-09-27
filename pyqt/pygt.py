import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import json
import re
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from marshmallow import Schema, fields, validate, ValidationError
import pandas as pd

Base = declarative_base()
engine = create_engine('sqlite:///student_managementpyqt.db')
Session = sessionmaker(bind=engine)
session = Session()


student_course = Table('student_course', Base.metadata,
    Column('student_id', Integer, ForeignKey('students.id')),
    Column('course_id', Integer, ForeignKey('courses.id'))
)
class StudentTable(Base):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    email = Column(String, nullable=False, unique=True)
    student_id = Column(String, nullable=False, unique=True)
    courses = relationship('CourseTable', secondary=student_course, back_populates='students')

class InstructorTable(Base):
    __tablename__ = 'instructors'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    email = Column(String, nullable=False, unique=True)
    instructor_id = Column(String, nullable=False, unique=True)
    courses = relationship('CourseTable', back_populates='instructor')

class CourseTable(Base):
    __tablename__ = 'courses'
    id = Column(Integer, primary_key=True, autoincrement=True)
    course_name = Column(String, nullable=False)
    course_id = Column(String, nullable=False, unique=True)
    instructor_id = Column(Integer, ForeignKey('instructors.id'))
    instructor = relationship('InstructorTable', back_populates='courses')
    students = relationship('StudentTable', secondary=student_course, back_populates='courses')

Base.metadata.create_all(engine)

class StudentSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1))
    age = fields.Integer(required=True, validate=lambda n: n > 0)
    email = fields.Email(required=True)
    student_id = fields.String(required=True, validate=validate.Length(min=1))

class InstructorSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1))
    age = fields.Integer(required=True, validate=lambda n: n > 0)
    email = fields.Email(required=True)
    instructor_id = fields.String(required=True, validate=validate.Length(min=1))

class CourseSchema(Schema):
    course_name = fields.String(required=True, validate=validate.Length(min=1))
    course_id = fields.String(required=True, validate=validate.Length(min=1))
    instructor_id = fields.Integer()

instructor_schema = InstructorSchema()
course_schema = CourseSchema()
student_schema = StudentSchema()

available_courses = []
students_list = []
instructors_list = []
class person(object):
    def __init__(self,name, age ,email):
        self.name=name
        self.age=age
        self.__email =email
    def get_email(self):
        return self.__email
    def introduce(self):
        print(f'Hello {self.name} your age is {self.age}')
    def save_to_file(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.serialize(), f)
    def load_from_file(cls, filename):
        with open(filename, 'r') as f:
            data = json.load(f)
            return cls(**data)
    ## the below function was found online to verify the integrity of the email
    def validate_email(self, email):
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, email):
            raise ValueError(f"Invalid email format: {email}")
        return email
    def validate_age(self, age):
        if not isinstance(age, int) or age < 0:
            raise ValueError(f"Invalid age: {age}. Age must be a non-negative integer.")
        return age
    

class student(person):
    def __init__(self,name, age ,email,student_id,registered_courses=[]):
        super().__init__(name,age,email)
        self.student_id=student_id
        self.registered_courses=registered_courses
    def register_course(self,course):
        self.registered_courses.append(course.course_id)
    
    def serialize(self):
        return json.dumps({
            "name":self.name,
            "age":self.age,
            "email":self.get_email(),
            "student_id":self.student_id,
            "registered_courses":self.registered_courses
        })


class instructor(person):
    def __init__(self,name, age ,email,instructor_id,assigned_courses=[]):
        super().__init__(name,age,email)
        self.instructor_id=instructor_id
        self.assigned_courses=assigned_courses     
    def assign_cource(self,course):
        self.assigned_courses.append(course.course_id)
    def serialize(self):
        return json.dumps({
            "name":self.name,
            "age":self.age,
            "email":self.get_email(),
            "instructor_id":self.instructor_id,
            "assigned_courses":self.assigned_courses
        })

class course():
    def __init__(self,course_id,course_name,instructor,enrolled_students=[]):
        self.course_id=course_id
        self.course_name=course_name
        self.instructor=instructor
        self.enrolled_students=enrolled_students
    def add_student(self,student):
        self.enrolled_students.append(student.student_id)
    
    def serialize(self):
        return json.dumps({
            "name":self.course_name,
            "course_id":self.course_id,
            "enrolled_courses": self.enrolled_students
        })
    def save_to_file(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.serialize(), f)

    def load_from_file(cls, filename):
        with open(filename, 'r') as f:
            data = json.load(f)
            return cls(**data)

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QLineEdit, QComboBox, QTreeWidget, 
                             QTreeWidgetItem, QTabWidget, QFormLayout, QMessageBox, QScrollArea)
from PyQt5.QtCore import Qt
import sys
import pandas as pd
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# Assume we have imported all necessary classes and schemas

class StudentManagementSystem(QMainWindow):
    """
    A PyQt5-based Student Management System GUI.

    This class is responsible for creating and managing the interface for students,
    instructors, and course management within the application.

    Attributes
    ----------
    central_widget : QWidget
        The central widget for the main window.
    main_layout : QVBoxLayout
        The main layout of the central widget.
    tab_widget : QTabWidget
        The tab widget to hold different sections (students, instructors, courses).

    Methods
    -------
    load_data():
        Loads student, instructor, and course data from the database into the UI.
    submit_student():
        Submits a new student entry into the database and updates the UI.
    setup_students_tab():
        Sets up the tab for managing students in the system.
    """
    def __init__(self):
        """Initializes the Student Management System main window."""
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setGeometry(100, 100, 1200, 800)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)

        self.setup_students_tab()
        self.setup_instructors_tab()
        self.setup_courses_tab()
        self.setup_registration_tab()
        self.setup_enrollment_tab()

        self.load_data()
    
    def load_data(self):
        # Load students
        students = session.query(StudentTable).all()
        self.student_tree.clear()
        for student in students:
            QTreeWidgetItem(self.student_tree, [student.name, str(student.age), student.email, student.student_id])
        self.update_student_combobox()

        # Load instructors
        instructors = session.query(InstructorTable).all()
        self.instructor_tree.clear()
        for instructor in instructors:
            QTreeWidgetItem(self.instructor_tree, [instructor.name, str(instructor.age), instructor.email, instructor.instructor_id])

        # Load courses
        courses = session.query(CourseTable).all()
        self.course_tree.clear()
        for course in courses:
            instructor_id = course.instructor.instructor_id if course.instructor else "N/A"
            QTreeWidgetItem(self.course_tree, [course.course_name, course.course_id, instructor_id])
        self.update_course_combobox()

        # Load enrollments
        self.update_enrollment_tree()

    def setup_students_tab(self):
        students_tab = QWidget()
        layout = QVBoxLayout(students_tab)

        form_layout = QFormLayout()
        self.student_name_input = QLineEdit()
        self.student_age_input = QLineEdit()
        self.student_email_input = QLineEdit()
        self.student_id_input = QLineEdit()
        form_layout.addRow("Name:", self.student_name_input)
        form_layout.addRow("Age:", self.student_age_input)
        form_layout.addRow("Email:", self.student_email_input)
        form_layout.addRow("Student ID:", self.student_id_input)

        submit_button = QPushButton("Submit Student")
        submit_button.clicked.connect(self.submit_student)

        self.student_search_input = QLineEdit()
        search_button = QPushButton("Search Student")
        search_button.clicked.connect(self.search_student)

        self.student_tree = QTreeWidget()
        self.student_tree.setHeaderLabels(["Name", "Age", "Email", "ID"])

        layout.addLayout(form_layout)
        layout.addWidget(submit_button)
        layout.addWidget(self.student_search_input)
        layout.addWidget(search_button)
        layout.addWidget(self.student_tree)

        self.tab_widget.addTab(students_tab, "Students")

    def setup_instructors_tab(self):
        instructors_tab = QWidget()
        layout = QVBoxLayout(instructors_tab)

        form_layout = QFormLayout()
        self.instructor_name_input = QLineEdit()
        self.instructor_age_input = QLineEdit()
        self.instructor_email_input = QLineEdit()
        self.instructor_id_input = QLineEdit()
        form_layout.addRow("Name:", self.instructor_name_input)
        form_layout.addRow("Age:", self.instructor_age_input)
        form_layout.addRow("Email:", self.instructor_email_input)
        form_layout.addRow("Instructor ID:", self.instructor_id_input)

        submit_button = QPushButton("Submit Instructor")
        submit_button.clicked.connect(self.submit_instructor)

        self.instructor_search_input = QLineEdit()
        search_button = QPushButton("Search Instructor")
        search_button.clicked.connect(self.search_instructor)

        self.instructor_tree = QTreeWidget()
        self.instructor_tree.setHeaderLabels(["Name", "Age", "Email", "ID"])

        layout.addLayout(form_layout)
        layout.addWidget(submit_button)
        layout.addWidget(self.instructor_search_input)
        layout.addWidget(search_button)
        layout.addWidget(self.instructor_tree)

        self.tab_widget.addTab(instructors_tab, "Instructors")

    def setup_courses_tab(self):
        courses_tab = QWidget()
        layout = QVBoxLayout(courses_tab)

        form_layout = QFormLayout()
        self.course_name_input = QLineEdit()
        self.course_id_input = QLineEdit()
        self.course_instructor_id_input = QLineEdit()
        form_layout.addRow("Course Name:", self.course_name_input)
        form_layout.addRow("Course ID:", self.course_id_input)
        form_layout.addRow("Instructor ID:", self.course_instructor_id_input)

        submit_button = QPushButton("Submit Course")
        submit_button.clicked.connect(self.submit_course)

        self.course_search_input = QLineEdit()
        search_button = QPushButton("Search Course")
        search_button.clicked.connect(self.search_course)

        self.course_tree = QTreeWidget()
        self.course_tree.setHeaderLabels(["Course Name", "Course ID", "Instructor ID"])

        layout.addLayout(form_layout)
        layout.addWidget(submit_button)
        layout.addWidget(self.course_search_input)
        layout.addWidget(search_button)
        layout.addWidget(self.course_tree)

        self.tab_widget.addTab(courses_tab, "Courses")

    def setup_registration_tab(self):
        registration_tab = QWidget()
        layout = QVBoxLayout(registration_tab)

        self.student_combobox = QComboBox()
        self.course_combobox = QComboBox()
        register_button = QPushButton("Register for Course")
        register_button.clicked.connect(self.register_student_for_course)

        layout.addWidget(QLabel("Select Student:"))
        layout.addWidget(self.student_combobox)
        layout.addWidget(QLabel("Select Course:"))
        layout.addWidget(self.course_combobox)
        layout.addWidget(register_button)

        self.tab_widget.addTab(registration_tab, "Registration")

    def setup_enrollment_tab(self):
        enrollment_tab = QWidget()
        layout = QVBoxLayout(enrollment_tab)

        self.enrollment_tree = QTreeWidget()
        self.enrollment_tree.setHeaderLabels(["Student Name", "Student ID", "Course Name", "Course ID"])

        layout.addWidget(self.enrollment_tree)

        self.tab_widget.addTab(enrollment_tab, "Enrollments")


    def submit_student(self):
        name = self.student_name_input.text()
        age = self.student_age_input.text()
        email = self.student_email_input.text()
        student_id = self.student_id_input.text()

        try:
            # Validate input using Marshmallow
            student_data = {
                "name": name,
                "age": int(age),
                "email": email,
                "student_id": student_id
            }
            validated_data = student_schema.load(student_data)

            # Check if student already exists
            existing_student = session.query(StudentTable).filter(
                (StudentTable.student_id == student_id) | (StudentTable.email == email)
            ).first()

            if existing_student:
                QMessageBox.warning(self, "Error", "Student ID or Email already exists in the database!")
            else:
                new_student = StudentTable(**validated_data)
                session.add(new_student)
                session.commit()
                self.update_student_tree()
                QMessageBox.information(self, "Success", f"Student {name} added to the database!")

        except ValidationError as err:
            QMessageBox.warning(self, "Validation Error", f"Invalid input: {err.messages}")
        except ValueError as ve:
            QMessageBox.warning(self, "Error", f"Invalid input: {ve}")

        # Clear input fields
        self.student_name_input.clear()
        self.student_age_input.clear()
        self.student_email_input.clear()
        self.student_id_input.clear()

    def submit_instructor(self):
        name = self.instructor_name_input.text()
        age = self.instructor_age_input.text()
        email = self.instructor_email_input.text()
        instructor_id = self.instructor_id_input.text()

        try:
            # Validate input using Marshmallow
            instructor_data = {
                "name": name,
                "age": int(age),
                "email": email,
                "instructor_id": instructor_id
            }
            validated_data = instructor_schema.load(instructor_data)

            # Check if instructor already exists
            existing_instructor = session.query(InstructorTable).filter(
                (InstructorTable.instructor_id == instructor_id) | (InstructorTable.email == email)
            ).first()

            if existing_instructor:
                QMessageBox.warning(self, "Error", "Instructor ID or Email already exists in the database!")
            else:
                new_instructor = InstructorTable(**validated_data)
                session.add(new_instructor)
                session.commit()
                self.update_instructor_tree()
                QMessageBox.information(self, "Success", f"Instructor {name} added to the database!")

        except ValidationError as err:
            QMessageBox.warning(self, "Validation Error", f"Invalid input: {err.messages}")
        except ValueError as ve:
            QMessageBox.warning(self, "Error", f"Invalid input: {ve}")

        # Clear input fields
        self.instructor_name_input.clear()
        self.instructor_age_input.clear()
        self.instructor_email_input.clear()
        self.instructor_id_input.clear()

    def submit_course(self):
        course_name = self.course_name_input.text()
        course_id = self.course_id_input.text()
        instructor_id = self.course_instructor_id_input.text()

        try:
            # Validate input using Marshmallow
            course_data = {
                "course_name": course_name,
                "course_id": course_id,
                "instructor_id": instructor_id if instructor_id else None
            }
            validated_data = course_schema.load(course_data)

            # Check if course already exists
            existing_course = session.query(CourseTable).filter(
                CourseTable.course_id == course_id
            ).first()

            if existing_course:
                QMessageBox.warning(self, "Error", "Course ID already exists in the database!")
            else:
                # If instructor_id is provided, fetch the instructor
                instructor = None
                if instructor_id:
                    instructor = session.query(InstructorTable).filter_by(instructor_id=instructor_id).first()
                    if not instructor:
                        QMessageBox.warning(self, "Error", f"Instructor with ID {instructor_id} not found!")
                        return

                new_course = CourseTable(
                    course_name=validated_data["course_name"],
                    course_id=validated_data["course_id"],
                    instructor=instructor
                )
                session.add(new_course)
                session.commit()
                self.update_course_tree()
                self.update_course_combobox()
                QMessageBox.information(self, "Success", f"Course {course_name} added to the database!")

        except ValidationError as err:
            QMessageBox.warning(self, "Validation Error", f"Invalid input: {err.messages}")
        except ValueError as ve:
            QMessageBox.warning(self, "Error", f"Invalid input: {ve}")

        # Clear input fields
        self.course_name_input.clear()
        self.course_id_input.clear()
        self.course_instructor_id_input.clear()

    def register_student_for_course(self):
        selected_student_name = self.student_combobox.currentText()
        selected_course_name = self.course_combobox.currentText()

        student = session.query(StudentTable).filter_by(name=selected_student_name).first()
        course = session.query(CourseTable).filter_by(course_name=selected_course_name).first()

        if student and course:
            if course not in student.courses:
                student.courses.append(course)
                session.commit()
                QMessageBox.information(self, "Success", f"{student.name} registered for {course.course_name}!")
                self.update_enrollment_tree()
            else:
                QMessageBox.information(self, "Info", f"{student.name} is already registered for {course.course_name}!")
        else:
            QMessageBox.warning(self, "Error", "Student or Course not found!")

    def search_student(self):
        search_term = self.student_search_input.text()
        self.student_tree.clear()
        students = session.query(StudentTable).filter(
            (StudentTable.name.like(f"%{search_term}%")) | (StudentTable.student_id == search_term)
        ).all()
        for student in students:
            QTreeWidgetItem(self.student_tree, [student.name, str(student.age), student.email, student.student_id])

    def search_instructor(self):
        search_term = self.instructor_search_input.text()
        self.instructor_tree.clear()
        instructors = session.query(InstructorTable).filter(
            (InstructorTable.name.like(f"%{search_term}%")) | 
            (InstructorTable.instructor_id == search_term) |
            (InstructorTable.email.like(f"%{search_term}%"))
        ).all()
        for instructor in instructors:
            QTreeWidgetItem(self.instructor_tree, [
                instructor.name, 
                str(instructor.age), 
                instructor.email, 
                instructor.instructor_id
            ])
        
        if not instructors:
            QMessageBox.information(self, "Search Result", "No matching instructors found.")

    def search_course(self):
        search_term = self.course_search_input.text()
        self.course_tree.clear()
        courses = session.query(CourseTable).filter(
            (CourseTable.course_name.like(f"%{search_term}%")) | 
            (CourseTable.course_id == search_term)
        ).all()
        for course in courses:
            instructor_id = course.instructor.instructor_id if course.instructor else "N/A"
            QTreeWidgetItem(self.course_tree, [
                course.course_name, 
                course.course_id, 
                instructor_id
            ])
        
        if not courses:
            QMessageBox.information(self, "Search Result", "No matching courses found.")


    def update_student_tree(self):
        self.student_tree.clear()
        students = session.query(StudentTable).all()
        for student in students:
            QTreeWidgetItem(self.student_tree, [student.name, str(student.age), student.email, student.student_id])

    def update_instructor_tree(self):
        self.instructor_tree.clear()  # Clear the current tree items
        instructors = session.query(InstructorTable).all()  # Fetch all instructors from the database
        for instructor in instructors:
            QTreeWidgetItem(self.instructor_tree, [instructor.name, str(instructor.age), instructor.email, instructor.instructor_id])

    def update_course_tree(self):
        self.course_tree.clear()  # Clear the current tree items
        courses = session.query(CourseTable).all()  # Fetch all courses from the database
        for course in courses:
            instructor = session.query(InstructorTable).filter_by(id=course.instructor_id).first()
            instructor_name = instructor.name if instructor else "N/A"  # If instructor exists, get the name, else "N/A"
            QTreeWidgetItem(self.course_tree, [course.course_name, course.course_id, instructor_name])

    def update_student_combobox(self):
        self.student_combobox.clear()
        students = session.query(StudentTable).all()
        self.student_combobox.addItems([student.name for student in students])

    def update_course_combobox(self):
        self.course_combobox.clear()
        courses = session.query(CourseTable).all()
        self.course_combobox.addItems([course.course_name for course in courses])

    def update_enrollment_tree(self):
        self.enrollment_tree.clear()
        enrollments = session.query(StudentTable, CourseTable).\
            join(student_course, StudentTable.id == student_course.c.student_id).\
            join(CourseTable, CourseTable.id == student_course.c.course_id).\
            all()
        for student, course in enrollments:
            QTreeWidgetItem(self.enrollment_tree, [student.name, student.student_id, course.course_name, course.course_id])

def export_to_csv(table_name, file_name):
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql_query(query, engine)
    df.to_csv(file_name, index=False)
    print(f"Data from table '{table_name}' has been exported to '{file_name}'")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StudentManagementSystem()
    window.show()

    # Export data
    export_to_csv('students', 'students.csv')
    export_to_csv('instructors', 'instructors.csv')
    export_to_csv('courses', 'courses.csv')
    export_to_csv('student_course', 'enrollments.csv')

    sys.exit(app.exec_())