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
engine = create_engine('sqlite:///student_management.db')
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

def load_students():
    global students_list
    students_list = []
    students = session.query(StudentTable).all()
    for student1 in students:
        new_student = student(student1.name, student1.age, student1.email, student1.student_id)
        students_list.append(new_student)

def load_instructors():
    global instructors_list
    instructors_list = []
    instructors = session.query(InstructorTable).all()
    for instructor1 in instructors:
        new_instructor = instructor(instructor1.name, instructor1.age, instructor1.email, instructor1.instructor_id)
        instructors_list.append(new_instructor)

def load_courses():
    global available_courses
    available_courses = []
    courses = session.query(CourseTable).all()
    for course1 in courses:
        new_course = course(course1.course_id, course1.course_name, course1.instructor_id)
        available_courses.append(new_course)

# Functions to handle form submission and registration
def submit_student():
    name = entry_student_name.get()
    age = entry_student_age.get()
    email = entry_student_email.get()
    student_id = entry_student_id.get()

    # Validate input using Marshmallow
    try:
        # Prepare data to validate
        student_data = {
            "name": name,
            "age": int(age),
            "email": email,
            "student_id": student_id
        }

        # Validate input using the Marshmallow schema
        validated_data = student_schema.load(student_data)

        # Check if the student is already in the database based on student_id or email
        existing_student = session.query(StudentTable).filter(
            (StudentTable.student_id == student_id) | (StudentTable.email == email)
        ).first()

        if existing_student:
            messagebox.showerror("Error", "Student ID or Email already exists in the database!")
        else:
            # Create a new student instance with validated data
            new_student = student(
                name=validated_data["name"],
                age=validated_data["age"],
                email=validated_data["email"],
                student_id=validated_data["student_id"]
            )
            new_studentdb = StudentTable(
                name=validated_data["name"],
                age=validated_data["age"],
                email=validated_data["email"],
                student_id=validated_data["student_id"]
            )

            # Add to the database
            session.add(new_studentdb)
            session.commit()

            # Update the treeview and student list
            students_list.append(new_student)
            update_student_tree()
            messagebox.showinfo("Success", f"Student {name} added to the database!")
    
    except ValidationError as err:
        # Catch validation errors and show them in a messagebox
        messagebox.showerror("Validation Error", f"Invalid input: {err.messages}")
    except ValueError as ve:
        messagebox.showerror("Error", f"Invalid input: {ve}")
    
    # Clear the form fields
    entry_student_name.delete(0, tk.END)
    entry_student_age.delete(0, tk.END)
    entry_student_email.delete(0, tk.END)
    entry_student_id.delete(0, tk.END)


def submit_instructor():
    name = entry_instructor_name.get()
    age = entry_instructor_age.get()
    email = entry_instructor_email.get()
    instructor_id = entry_instructor_id.get()

    try:
        # Validate input using Marshmallow
        instructor_data = {
            "name": name,
            "age": int(age),
            "email": email,
            "instructor_id": instructor_id
        }

        validated_data = instructor_schema.load(instructor_data)

        # Check if the instructor already exists in the database
        existing_instructor = session.query(InstructorTable).filter(
            (InstructorTable.instructor_id == instructor_id) | (InstructorTable.email == email)
        ).first()

        if existing_instructor:
            messagebox.showerror("Error", "Instructor ID or Email already exists!")
        else:
            new_instructor = instructor(
                name=validated_data["name"],
                age=validated_data["age"],
                email=validated_data["email"],
                instructor_id=validated_data["instructor_id"]
            )
            new_instructordb = InstructorTable(
                name=validated_data["name"],
                age=validated_data["age"],
                email=validated_data["email"],
                instructor_id=validated_data["instructor_id"]
            )
            session.add(new_instructordb)
            session.commit()
            instructors_list.append(new_instructor)
            update_instructor_tree()
            update_instructor_list()
            messagebox.showinfo("Success", f"Instructor {name} added to the database!")
    
    except ValidationError as err:
        messagebox.showerror("Validation Error", f"Invalid input: {err.messages}")
    except ValueError as ve:
        messagebox.showerror("Error", f"Invalid input: {ve}")

    # Clear the form fields
    entry_instructor_name.delete(0, tk.END)
    entry_instructor_age.delete(0, tk.END)
    entry_instructor_email.delete(0, tk.END)
    entry_instructor_id.delete(0, tk.END)


def submit_course():
    course_name = entry_course_name.get()
    course_id = entry_course_id.get()
    instructor_id = entry_course_instructor_id.get()  # This could be optional

    try:
        # Validate input using Marshmallow
        course_data = {
            "course_name": course_name,
            "course_id": course_id,
            "instructor_id": instructor_id if instructor_id else None
        }

        validated_data = course_schema.load(course_data)
        print(validated_data)
        # Check if the course already exists in the database
        existing_course = session.query(CourseTable).filter(
            CourseTable.course_id == course_id
        ).first()

        if existing_course:
            messagebox.showerror("Error", "Course ID already exists!")
        else:
            new_course = course(
                course_id=validated_data["course_id"],
                course_name=validated_data["course_name"],
                instructor=validated_data["instructor_id"]
            )
            new_coursedb = CourseTable(
                course_name=validated_data["course_name"],
                course_id=validated_data["course_id"],
                instructor_id=validated_data["instructor_id"]
            )
            session.add(new_coursedb)
            session.commit()
            available_courses.append(new_course)
            update_course_tree()
            update_course_list()
            update_course_list_for_instructors()
            messagebox.showinfo("Success", f"Course {course_name} added to the database!")
    
    except ValidationError as err:
        messagebox.showerror("Validation Error", f"Invalid input: {err.messages}")
    except ValueError as ve:
        messagebox.showerror("Error", f"Invalid input: {ve}")

    # Clear the form fields
    entry_course_name.delete(0, tk.END)
    entry_course_id.delete(0, tk.END)
    entry_course_instructor_id.delete(0, tk.END)


def update_student_tree():
    student_tree.delete(*student_tree.get_children())
    for student in students_list:
        student_tree.insert("", "end", values=(student.name, student.age, student.get_email(), student.student_id))

def update_instructor_tree():
    instructor_tree.delete(*instructor_tree.get_children())
    for instructor in instructors_list:
        instructor_tree.insert("", "end", values=(instructor.name, instructor.age, instructor.get_email(), instructor.instructor_id))

def update_course_tree():
    course_tree.delete(*course_tree.get_children())
    for course in available_courses:
        course_tree.insert("", "end", values=(course.course_name, course.course_id, course.instructor))
def update_enrollment_tree():
    enrollment_tree.delete(*enrollment_tree.get_children())
    enrollments = session.query(StudentTable, CourseTable).\
        join(student_course, StudentTable.id == student_course.c.student_id).\
        join(CourseTable, CourseTable.id == student_course.c.course_id).\
        all()
    for student, course in enrollments:
        enrollment_tree.insert("", "end", values=(student.name, student.student_id, course.course_name, course.course_id))

def update_course_list():
    course_names = [course.course_name for course in available_courses]
    course_combobox['values'] = course_names

def update_student_list():
    student_names = [student.name for student in students_list]
    student_combobox['values'] = student_names

def assign_instructor_to_course():
    selected_instructor_name = instructor_combobox.get()
    selected_course_name = course_combobox_instructor.get()

    instructor = session.query(InstructorTable).filter_by(name=selected_instructor_name).first()
    course = session.query(CourseTable).filter_by(course_name=selected_course_name).first()
    
    if instructor and course:
        course.instructor = instructor
        session.commit()
        messagebox.showinfo("Success", f"{instructor.name} assigned to {course.course_name}!")
        update_course_tree()
    else:
        messagebox.showerror("Error", "Instructor or Course not found!")

def update_instructor_list():
    instructor_names = [instructor.name for instructor in instructors_list]
    instructor_combobox['values'] = instructor_names

def update_course_list_for_instructors():
    course_names = [course.course_name for course in available_courses]
    course_combobox_instructor['values'] = course_names

def register_student_for_course():
    selected_student_name = student_combobox.get()
    selected_course_name = course_combobox.get()
    
    student = session.query(StudentTable).filter_by(name=selected_student_name).first()
    course = session.query(CourseTable).filter_by(course_name=selected_course_name).first()
    
    if student and course:
        if course not in student.courses:
            student.courses.append(course)
            session.commit()
            messagebox.showinfo("Success", f"{student.name} registered for {course.course_name}!")
            update_enrollment_tree()
        else:
            messagebox.showinfo("Info", f"{student.name} is already registered for {course.course_name}!")
    else:
        messagebox.showerror("Error", "Student or Course not found!")

def search_student(search_term):
    student_tree.delete(*student_tree.get_children())
    students = session.query(StudentTable).filter(
        (StudentTable.name.like(f"%{search_term}%")) | (StudentTable.student_id == search_term)
    ).all()
    for student in students:
        student_tree.insert("", "end", values=(student.name, student.age, student.email, student.student_id))

def search_instructor(search_term):
    instructor_tree.delete(*instructor_tree.get_children())
    instructors = session.query(InstructorTable).filter(
        (InstructorTable.name.like(f"%{search_term}%")) | (InstructorTable.instructor_id == search_term)
    ).all()
    for instructor in instructors:
        instructor_tree.insert("", "end", values=(instructor.name, instructor.age, instructor.email, instructor.instructor_id))

def search_course(search_term):
    course_tree.delete(*course_tree.get_children())
    courses = session.query(CourseTable).filter(
        (CourseTable.course_name.like(f"%{search_term}%")) | (CourseTable.course_id == search_term)
    ).all()
    for course in courses:
        course_tree.insert("", "end", values=(course.course_name, course.course_id, course.instructor_id))

def export_to_csv(table_name, file_name):
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql_query(query, engine)
    df.to_csv(file_name, index=False)
    print(f"Data from table '{table_name}' has been exported to '{file_name}'")

load_courses()
load_instructors()
load_students()

# Create the main window
window = tk.Tk()
window.title("Student Management System")
window.geometry("1200x1000")

# Create a frame to hold the canvas and scrollbar
main_frame = tk.Frame(window)
main_frame.pack(fill=tk.BOTH, expand=1)

# Create a canvas inside the main frame
canvas = tk.Canvas(main_frame)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

# Add a scrollbar to the canvas
scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Configure the canvas to work with the scrollbar
canvas.configure(yscrollcommand=scrollbar.set)
canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

# Create another frame inside the canvas to hold all form widgets
form_frame = tk.Frame(canvas)

# Add the form frame to the canvas
canvas.create_window((0, 0), window=form_frame, anchor="nw")

# Student form
ttk.Label(form_frame, text="Add Student").pack(pady=10)
ttk.Label(form_frame, text="Name").pack()
entry_student_name = ttk.Entry(form_frame)
entry_student_name.pack()
ttk.Label(form_frame, text="Age").pack()
entry_student_age = ttk.Entry(form_frame)
entry_student_age.pack()
ttk.Label(form_frame, text="Email").pack()
entry_student_email = ttk.Entry(form_frame)
entry_student_email.pack()
ttk.Label(form_frame, text="Student ID").pack()
entry_student_id = ttk.Entry(form_frame)
entry_student_id.pack()
submit_student_button = ttk.Button(form_frame, text="Submit Student", command=submit_student)
submit_student_button.pack(pady=10)

# Instructor form
ttk.Label(form_frame, text="Add Instructor").pack(pady=10)
ttk.Label(form_frame, text="Name").pack()
entry_instructor_name = ttk.Entry(form_frame)
entry_instructor_name.pack()
ttk.Label(form_frame, text="Age").pack()
entry_instructor_age = ttk.Entry(form_frame)
entry_instructor_age.pack()
ttk.Label(form_frame, text="Email").pack()
entry_instructor_email = ttk.Entry(form_frame)
entry_instructor_email.pack()
ttk.Label(form_frame, text="Instructor ID").pack()
entry_instructor_id = ttk.Entry(form_frame)
entry_instructor_id.pack()
submit_instructor_button = ttk.Button(form_frame, text="Submit Instructor", command=submit_instructor)
submit_instructor_button.pack(pady=10)

# Course form
ttk.Label(form_frame, text="Add Course").pack(pady=10)
ttk.Label(form_frame, text="Course Name").pack()
entry_course_name = ttk.Entry(form_frame)
entry_course_name.pack()
ttk.Label(form_frame, text="Course ID").pack()
entry_course_id = ttk.Entry(form_frame)
entry_course_id.pack()
ttk.Label(form_frame, text="Instructor ID").pack()
entry_course_instructor_id = ttk.Entry(form_frame)
entry_course_instructor_id.pack()
submit_course_button = ttk.Button(form_frame, text="Submit Course", command=submit_course)
submit_course_button.pack(pady=10)

# Dropdown for selecting student to register
ttk.Label(form_frame, text="Register Student for Course").pack(pady=10)
ttk.Label(form_frame, text="Select Student").pack()
student_combobox = ttk.Combobox(form_frame)
student_combobox.pack()

ttk.Label(form_frame, text="Select Course").pack()
course_combobox = ttk.Combobox(form_frame)
course_combobox.pack()

register_button = ttk.Button(form_frame, text="Register for Course", command=register_student_for_course)
register_button.pack(pady=10)

# Close button
close_button = ttk.Button(form_frame, text="Close", command=window.destroy)
close_button.pack(pady=20)

# Dropdown for selecting instructor to assign to a course
ttk.Label(form_frame, text="Assign Instructor to Course").pack(pady=10)
ttk.Label(form_frame, text="Select Instructor").pack()
instructor_combobox = ttk.Combobox(form_frame)
instructor_combobox.pack()

ttk.Label(form_frame, text="Select Course").pack()
course_combobox_instructor = ttk.Combobox(form_frame)
course_combobox_instructor.pack()

assign_button = ttk.Button(form_frame, text="Assign Instructor", command=assign_instructor_to_course)
assign_button.pack(pady=10)


# Search bar for students
ttk.Label(form_frame, text="Search Students").pack(pady=10)
entry_student_search = ttk.Entry(form_frame)
entry_student_search.pack()

search_student_button = ttk.Button(form_frame, text="Search Student", command=lambda: search_student(entry_student_search.get()))
search_student_button.pack()

# Treeview for displaying students
student_tree = ttk.Treeview(form_frame, columns=("Name", "Age", "Email", "ID"), show="headings")
student_tree.heading("Name", text="Name")
student_tree.heading("Age", text="Age")
student_tree.heading("Email", text="Email")
student_tree.heading("ID", text="ID")
student_tree.pack(pady=10)

# Search bar for instructors
ttk.Label(form_frame, text="Search Instructors").pack(pady=10)
entry_instructor_search = ttk.Entry(form_frame)
entry_instructor_search.pack()

search_instructor_button = ttk.Button(form_frame, text="Search Instructor", command=lambda: search_instructor(entry_instructor_search.get()))
search_instructor_button.pack()

# Treeview for displaying instructors
instructor_tree = ttk.Treeview(form_frame, columns=("Name", "Age", "Email", "ID"), show="headings")
instructor_tree.heading("Name", text="Name")
instructor_tree.heading("Age", text="Age")
instructor_tree.heading("Email", text="Email")
instructor_tree.heading("ID", text="ID")
instructor_tree.pack(pady=10)

# Search bar for courses
ttk.Label(form_frame, text="Search Courses").pack(pady=10)
entry_course_search = ttk.Entry(form_frame)
entry_course_search.pack()

search_course_button = ttk.Button(form_frame, text="Search Course", command=lambda: search_course(entry_course_search.get()))
search_course_button.pack()

# Treeview for displaying courses
course_tree = ttk.Treeview(form_frame, columns=("Course Name", "Course ID", "Instructor ID"), show="headings")
course_tree.heading("Course Name", text="Course Name")
course_tree.heading("Course ID", text="Course ID")
course_tree.heading("Instructor ID", text="Instructor ID")
course_tree.pack(pady=10)


ttk.Label(form_frame, text="Student-Course Enrollments").pack(pady=10)
enrollment_tree = ttk.Treeview(form_frame, columns=("Student Name", "Student ID", "Course Name", "Course ID"), show="headings")
enrollment_tree.heading("Student Name", text="Student Name")
enrollment_tree.heading("Student ID", text="Student ID")
enrollment_tree.heading("Course Name", text="Course Name")
enrollment_tree.heading("Course ID", text="Course ID")
enrollment_tree.pack(pady=10)

# Update all trees and lists
update_course_tree()
update_instructor_tree()
update_student_tree()
update_enrollment_tree()
update_course_list()
update_student_list()
update_instructor_list()
update_course_list_for_instructors()

# Export data
export_to_csv('students', 'students.csv')
export_to_csv('instructors', 'instructors.csv')
export_to_csv('courses', 'courses.csv')
export_to_csv('student_course', 'enrollments.csv')

window.mainloop()

