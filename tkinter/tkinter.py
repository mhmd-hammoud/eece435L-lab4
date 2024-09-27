from sqlite3 import connect
import tkinter as tk
from tkinter import ttk
import json


class Person:
    """
    Represents a person with a name, age, and email address.

    :param name: The name of the person.
    :type name: str
    :param age: The age of the person.
    :type age: int
    :param email: The email address of the person.
    :type email: str
    :raises AssertionError: If age is negative or email is invalid.
    """

    def __init__(self, name, age, email):
        assert age >= 0, "Age cannot be negative."
        assert "@" in email, "Invalid email address."
        self.name = name
        self.age = age
        self.__email = email

    def introduce(self):
        """
        Prints an introduction message.
        """
        print(f"Hello, I am {self.name} and I am {self.age} years old.")

    def serialize(self):
        """
        Serializes the Person object to a JSON string.

        :return: The JSON string representation of the Person.
        :rtype: str
        """
        return json.dumps(self, default=lambda o: o.__dict__)

    @staticmethod
    def deserialize(data):
        """
        Deserializes a JSON string to a Person object.

        :param data: The JSON string to deserialize.
        :type data: str
        :return: A Person object.
        :rtype: Person
        :raises AssertionError: If age is negative or email is invalid.
        """
        data = json.loads(data)
        assert data["age"] >= 0, "Age cannot be negative."
        assert "@" in data["_Person__email"], "Invalid email address."
        return Person(data["name"], data["age"], data["_Person__email"])

    def get_email(self):
        """
        Gets the email address of the person.

        :return: The email address.
        :rtype: str
        """
        return self.__email


class Student(Person):
    """
    Represents a student, inheriting from Person.

    :param name: The name of the student.
    :type name: str
    :param age: The age of the student.
    :type age: int
    :param email: The email address of the student.
    :type email: str
    :param student_id: The ID of the student.
    :type student_id: str
    :param registered_courses: A list of registered course IDs.
    :type registered_courses: list
    """

    def __init__(self, name, age, email, student_id, registered_courses=[]):
        super().__init__(name, age, email)
        self.student_id = student_id
        self.registered_courses = registered_courses

    def register_course(self, course_id):
        """
        Registers the student for a course.

        :param course_id: The ID of the course to register.
        :type course_id: str
        """
        self.registered_courses.append(course_id)

    @staticmethod
    def deserialize(data):
        """
        Deserializes a JSON string to a Student object.

        :param data: The JSON string to deserialize.
        :type data: str
        :return: A Student object.
        :rtype: Student
        """
        data = json.loads(data)
        assert data["age"] >= 0, "Age cannot be negative."
        assert "@" in data["_Person__email"], "Invalid email address."
        return Student(data["name"], data["age"], data["_Person__email"], data["student_id"], data["registered_courses"])


class Instructor(Person):
    """
    Represents an instructor, inheriting from Person.

    :param name: The name of the instructor.
    :type name: str
    :param age: The age of the instructor.
    :type age: int
    :param email: The email address of the instructor.
    :type email: str
    :param instructor_id: The ID of the instructor.
    :type instructor_id: str
    :param assigned_courses: A list of assigned course IDs.
    :type assigned_courses: list
    """

    def __init__(self, name, age, email, instructor_id, assigned_courses):
        super().__init__(name, age, email)
        self.instructor_id = instructor_id
        self.assigned_courses = assigned_courses

    def assign_course(self, course_id):
        """
        Assigns a course to the instructor.

        :param course_id: The ID of the course to assign.
        :type course_id: str
        """
        self.assigned_courses.append(course_id)

    @staticmethod
    def deserialize(data):
        """
        Deserializes a JSON string to an Instructor object.

        :param data: The JSON string to deserialize.
        :type data: str
        :return: An Instructor object.
        :rtype: Instructor
        """
        data = json.loads(data)
        assert data["age"] >= 0, "Age cannot be negative."
        assert "@" in data["_Person__email"], "Invalid email address."
        return Instructor(data["name"], data["age"], data["_Person__email"], data["instructor_id"], data["assigned_courses"])


class Course:
    """
    Represents a course.

    :param course_id: The ID of the course.
    :type course_id: str
    :param course_name: The name of the course.
    :type course_name: str
    :param instructor: The instructor of the course.
    :type instructor: Instructor
    :param enrolled_students: A list of enrolled student IDs.
    :type enrolled_students: list
    """

    def __init__(self, course_id, course_name, instructor, enrolled_students):
        self.course_id = course_id
        self.course_name = course_name
        self.instructor = instructor
        self.enrolled_students = enrolled_students

    def add_student(self, student_id):
        """
        Adds a student to the course.

        :param student_id: The ID of the student to add.
        :type student_id: str
        """
        self.enrolled_students.append(student_id)

    def serialize(self):
        """
        Serializes the Course object to a JSON string.

        :return: The JSON string representation of the Course.
        :rtype: str
        """
        return json.dumps(self, default=lambda o: o.__dict__)

    @staticmethod
    def deserialize(data):
        """
        Deserializes a JSON string to a Course object.

        :param data: The JSON string to deserialize.
        :type data: str
        :return: A Course object.
        :rtype: Course
        """
        data = json.loads(data)
        return Course(data["course_id"], data["course_name"], data["instructor"], data["enrolled_students"])

    def __str__(self):
        """
        Returns the string representation of the course.

        :return: The course name.
        :rtype: str
        """
        return self.course_name


def update_data():
    """
    Updates the data by saving students, instructors, and courses to 'data.json'.
    """
    data = {
        "students": [student.serialize() for student in students],
        "instructors": [instructor.serialize() for instructor in instructors],
        "courses": [course.serialize() for course in courses]
    }
    with open("data.json", "w") as file:
        json.dump(data, file)


def load_data():
    """
    Loads data from 'data.json' and deserializes it into students, instructors, and courses.
    """
    try:
        with open("data.json", "r") as file:
            data = json.load(file)
            students = [Student.deserialize(student) for student in data["students"]]
            instructors = [Instructor.deserialize(instructor) for instructor in data["instructors"]]
            courses = [Course.deserialize(course) for course in data["courses"]]
    except:
        students = []
        instructors = []
        courses = []


def update_row():
    """
    Updates a row in the GUI table. Functionality to be implemented.
    """
    ...


def delete_row():
    """
    Deletes a row from the GUI table. Functionality to be implemented.
    """
    ...


try:
    with open("data.json", "r") as file:
        data = json.load(file)
        students = [Student.deserialize(student) for student in data["students"]]
        instructors = [Instructor.deserialize(instructor) for instructor in data["instructors"]]
        courses = [Course.deserialize(course) for course in data["courses"]]
except:
    students = [
        Student("Alice Smith", 20, "mail2@mail.com", "123445", []),
    ]
    instructors = [
        Instructor("John Doe", 30, "mail@mail.com", "12345", []),
    ]
    courses = [
        Course("CSC101", "Introduction to Computer Science", None, []),
    ]


# TKINTER GUI
if True:
    root = tk.Tk()
    root.title("Student Management System")
    root.geometry("1920x1080")

    # STUDENT
    student_form = tk.Frame(root)
    student_form.pack()

    tk.Label(student_form, text="Student Form").grid(row=0, column=0, columnspan=2)
    tk.Label(student_form, text="Name").grid(row=1, column=0)
    tk.Label(student_form, text="Age").grid(row=2, column=0)
    tk.Label(student_form, text="Email").grid(row=3, column=0)
    tk.Label(student_form, text="Student ID").grid(row=4, column=0)

    student_name_entry = tk.Entry(student_form)
    student_name_entry.grid(row=1, column=1)
    student_age_entry = tk.Entry(student_form)
    student_age_entry.grid(row=2, column=1)
    student_email_entry = tk.Entry(student_form)
    student_email_entry.grid(row=3, column=1)
    student_id_entry = tk.Entry(student_form)
    student_id_entry.grid(row=4, column=1)

    def submit_student():
        """
        Submits the student form and adds a new student to the list.
        """
        student = Student(student_name_entry.get(), int(student_age_entry.get()), student_email_entry.get(), student_id_entry.get())
        students.append(student)
        update_data()
        print("Student added successfully.")

    tk.Button(student_form, text="Submit", command=submit_student).grid(row=6, column=0, columnspan=2)

    register_student_form = tk.Frame(root)
    register_student_form.pack()

    tk.Label(register_student_form, text="Register Student to Course").grid(row=0, column=0, columnspan=2)
    tk.Label(register_student_form, text="Student ID").grid(row=1, column=0)
    tk.Label(register_student_form, text="Course ID").grid(row=2, column=0)

    student_id_entry = tk.Entry(register_student_form)
    student_id_entry.grid(row=1, column=1)
    student_course_dropdown = tk.OptionMenu(register_student_form, tk.StringVar(), *courses)
    student_course_dropdown.grid(row=2, column=1)

    def update_student_dropdown():
        """
        Updates the course dropdown menu for students.
        """
        student_course_dropdown["menu"].delete(0, "end")
        for course in courses:
            student_course_dropdown["menu"].add_command(label=course, command=tk._setit(student_course_dropdown.cget("text"), course))

    def register_student():
        """
        Registers a student to a selected course.
        """
        student_id = student_id_entry.get()
        course_id = student_course_dropdown.cget("text")
        for student in students:
            if student.student_id == student_id:
                student.register_course(course_id)
                break
        update_data()
        print("Student registered successfully.")

    tk.Button(register_student_form, text="Submit", command=register_student).grid(row=3, column=0, columnspan=2)

    # INSTRUCTOR
    instructor_form = tk.Frame(root)
    instructor_form.pack()

    tk.Label(instructor_form, text="Instructor Form").grid(row=0, column=0, columnspan=2)
    tk.Label(instructor_form, text="Name").grid(row=1, column=0)
    tk.Label(instructor_form, text="Age").grid(row=2, column=0)
    tk.Label(instructor_form, text="Email").grid(row=3, column=0)
    tk.Label(instructor_form, text="Instructor ID").grid(row=4, column=0)

    instructor_name_entry = tk.Entry(instructor_form)
    instructor_name_entry.grid(row=1, column=1)
    instructor_age_entry = tk.Entry(instructor_form)
    instructor_age_entry.grid(row=2, column=1)
    instructor_email_entry = tk.Entry(instructor_form)
    instructor_email_entry.grid(row=3, column=1)
    instructor_id_entry = tk.Entry(instructor_form)
    instructor_id_entry.grid(row=4, column=1)

    def submit_instructor():
        """
        Submits the instructor form and adds a new instructor to the list.
        """
        instructor = Instructor(instructor_name_entry.get(), int(instructor_age_entry.get()), instructor_email_entry.get(), instructor_id_entry.get(), [])
        instructors.append(instructor)
        update_data()
        print("Instructor added successfully.")

    tk.Button(instructor_form, text="Submit", command=submit_instructor).grid(row=5, column=0, columnspan=2)

    assign_instructor_form = tk.Frame(root)
    assign_instructor_form.pack()

    tk.Label(assign_instructor_form, text="Assign Instructor to Course").grid(row=0, column=0, columnspan=2)
    tk.Label(assign_instructor_form, text="Instructor ID").grid(row=1, column=0)
    tk.Label(assign_instructor_form, text="Course ID").grid(row=2, column=0)

    instructor_id_entry = tk.Entry(assign_instructor_form)
    instructor_id_entry.grid(row=1, column=1)
    instructor_course_dropdown = tk.OptionMenu(assign_instructor_form, tk.StringVar(), *courses)
    instructor_course_dropdown.grid(row=2, column=1)

    def update_instructor_dropdown():
        """
        Updates the course dropdown menu for instructors.
        """
        instructor_course_dropdown["menu"].delete(0, "end")
        for course in courses:
            instructor_course_dropdown["menu"].add_command(label=course, command=tk._setit(instructor_course_dropdown.cget("text"), course))

    def assign_instructor():
        """
        Assigns an instructor to a selected course.
        """
        instructor_id = instructor_id_entry.get()
        course_id = instructor_course_dropdown.cget("text")
        for instructor in instructors:
            if instructor.instructor_id == instructor_id:
                instructor.assign_course(course_id)
                break
        update_data()
        print("Instructor assigned successfully.")

    tk.Button(assign_instructor_form, text="Submit", command=assign_instructor).grid(row=3, column=0, columnspan=2)

    # COURSE
    course_form = tk.Frame(root)
    course_form.pack()

    tk.Label(course_form, text="Course Form").grid(row=0, column=0, columnspan=2)
    tk.Label(course_form, text="Course ID").grid(row=1, column=0)
    tk.Label(course_form, text="Course Name").grid(row=2, column=0)

    course_id_entry = tk.Entry(course_form)
    course_id_entry.grid(row=1, column=1)
    course_name_entry = tk.Entry(course_form)
    course_name_entry.grid(row=2, column=1)

    def submit_course():
        """
        Submits the course form and adds a new course to the list.
        """
        course = Course(course_id_entry.get(), course_name_entry.get(), None, [])
        courses.append(course)
        update_data()
        update_student_dropdown()
        update_instructor_dropdown()
        print("Course added successfully.")

    tk.Button(course_form, text="Submit", command=submit_course).grid(row=3, column=0, columnspan=2)

    tab_control = ttk.Notebook(root)
    tab_control.pack(expand=1, fill="both")

    # STUDENTS TABLE
    student_tab = ttk.Frame(tab_control)
    tab_control.add(student_tab, text="Students")
    student_table = ttk.Treeview(student_tab)
    student_table.pack()

    student_table["columns"] = ("Name", "Age", "Email", "Student ID", "Registered Courses")
    student_table.column("#0", width=50)
    student_table.column("Name", anchor="w", width=100)
    student_table.column("Age", anchor="w", width=50)
    student_table.column("Email", anchor="w", width=100)
    student_table.column("Student ID", anchor="w", width=100)
    student_table.column("Registered Courses", anchor="w", width=100)

    student_table.heading("#0", text="ID")
    student_table.heading("Name", text="Name")
    student_table.heading("Age", text="Age")
    student_table.heading("Email", text="Email")
    student_table.heading("Student ID", text="Student ID")
    student_table.heading("Registered Courses", text="Registered Courses")

    def update_student_table():
        """
        Updates the student table with the current list of students.
        """
        for student in students:
            student_table.insert("", "end", text=student.student_id, values=(student.name, student.age, student.get_email()))

    update_student_table()

    # INSTRUCTORS TABLE
    instructor_tab = ttk.Frame(tab_control)
    tab_control.add(instructor_tab, text="Instructors")
    instructor_table = ttk.Treeview(instructor_tab)
    instructor_table.pack()

    instructor_table["columns"] = ("Name", "Age", "Email", "Instructor ID", "Assigned Courses")
    instructor_table.column("#0", width=50)
    instructor_table.column("Name", anchor="w", width=100)
    instructor_table.column("Age", anchor="w", width=50)
    instructor_table.column("Email", anchor="w", width=100)
    instructor_table.column("Instructor ID", anchor="w", width=100)
    instructor_table.column("Assigned Courses", anchor="w", width=100)

    instructor_table.heading("#0", text="ID")
    instructor_table.heading("Name", text="Name")
    instructor_table.heading("Age", text="Age")
    instructor_table.heading("Email", text="Email")
    instructor_table.heading("Instructor ID", text="Instructor ID")
    instructor_table.heading("Assigned Courses", text="Assigned Courses")

    def update_instructor_table():
        """
        Updates the instructor table with the current list of instructors.
        """
        for instructor in instructors:
            instructor_table.insert("", "end", text=instructor.instructor_id, values=(instructor.name, instructor.age, instructor.get_email()))

    update_instructor_table()

    # COURSES TABLE
    course_tab = ttk.Frame(tab_control)
    tab_control.add(course_tab, text="Courses")
    course_table = ttk.Treeview(course_tab)
    course_table.pack()

    course_table["columns"] = ("Course ID", "Course Name", "Instructor", "Enrolled Students")
    course_table.column("#0", width=50)
    course_table.column("Course ID", anchor="w", width=100)
    course_table.column("Course Name", anchor="w", width=100)
    course_table.column("Instructor", anchor="w", width=100)
    course_table.column("Enrolled Students", anchor="w", width=100)

    course_table.heading("#0", text="ID")
    course_table.heading("Course ID", text="Course ID")
    course_table.heading("Course Name", text="Course Name")
    course_table.heading("Instructor", text="Instructor")
    course_table.heading("Enrolled Students", text="Enrolled Students")

    def update_course_table():
        """
        Updates the course table with the current list of courses.
        """
        for course in courses:
            course_table.insert("", "end", text=course.course_id, values=(course.course_name, course.instructor, course.enrolled_students))

    update_course_table()

    update_button = tk.Button(tab_control, text="Update Record", command=update_row)
    update_button.grid(row=0, column=0)
    delete_button = tk.Button(tab_control, text="Delete Record", command=delete_row)
    delete_button.grid(row=0, column=1)

    save_button = tk.Button(root, text="Save Data", command=update_data)
    save_button.pack()
    load_button = tk.Button(root, text="Load Data", command=load_data)
    load_button.pack()

    root.mainloop()


connection = connect("students.db")
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    student_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    age INTEGER NOT NULL,
    email TEXT NOT NULL
)
""")
connection.commit()


cursor.execute("""
CREATE TABLE IF NOT EXISTS instructors (
    instructor_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    age INTEGER NOT NULL,
    email TEXT NOT NULL
)
""")
connection.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS courses (
    course_id INTEGER PRIMARY KEY,
    course_name TEXT NOT NULL,
    instructor_id INTEGER NOT NULL,
    FOREIGN KEY (instructor_id) REFERENCES instructors (instructor_id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS registrations (
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students (student_id),
    FOREIGN KEY (course_id) REFERENCES courses (course_id)
)
""")
connection.commit()

connection.close()


class DatabaseManager:
    """
    Manages database operations for students, instructors, courses, and registrations.

    :param database: The database file name.
    :type database: str
    """

    def __init__(self, database):
        self.connection = connect(database)
        self.cursor = self.connection.cursor()

    def create_student(self, name, age, email):
        """
        Creates a new student in the database.

        :param name: The name of the student.
        :type name: str
        :param age: The age of the student.
        :type age: int
        :param email: The email address of the student.
        :type email: str
        """
        self.cursor.execute("INSERT INTO students (name, age, email) VALUES (?, ?, ?)", (name, age, email))
        self.connection.commit()

    def read_students(self):
        """
        Reads all students from the database.

        :return: A list of student records.
        :rtype: list
        """
        self.cursor.execute("SELECT * FROM students")
        return self.cursor.fetchall()

    def update_student(self, student_id, name, age, email):
        """
        Updates a student's information.

        :param student_id: The ID of the student to update.
        :type student_id: int
        :param name: The new name.
        :type name: str
        :param age: The new age.
        :type age: int
        :param email: The new email address.
        :type email: str
        """
        self.cursor.execute("UPDATE students SET name = ?, age = ?, email = ? WHERE student_id = ?", (name, age, email, student_id))
        self.connection.commit()

    def delete_student(self, student_id):
        """
        Deletes a student from the database.

        :param student_id: The ID of the student to delete.
        :type student_id: int
        """
        self.cursor.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
        self.connection.commit()

    def create_instructor(self, name, age, email):
        """
        Creates a new instructor in the database.

        :param name: The name of the instructor.
        :type name: str
        :param age: The age of the instructor.
        :type age: int
        :param email: The email address of the instructor.
        :type email: str
        """
        self.cursor.execute("INSERT INTO instructors (name, age, email) VALUES (?, ?, ?)", (name, age, email))
        self.connection.commit()

    def read_instructors(self):
        """
        Reads all instructors from the database.

        :return: A list of instructor records.
        :rtype: list
        """
        self.cursor.execute("SELECT * FROM instructors")
        return self.cursor.fetchall()

    def update_instructor(self, instructor_id, name, age, email):
        """
        Updates an instructor's information.

        :param instructor_id: The ID of the instructor to update.
        :type instructor_id: int
        :param name: The new name.
        :type name: str
        :param age: The new age.
        :type age: int
        :param email: The new email address.
        :type email: str
        """
        self.cursor.execute("UPDATE instructors SET name = ?, age = ?, email = ? WHERE instructor_id = ?", (name, age, email, instructor_id))
        self.connection.commit()

    def delete_instructor(self, instructor_id):
        """
        Deletes an instructor from the database.

        :param instructor_id: The ID of the instructor to delete.
        :type instructor_id: int
        """
        self.cursor.execute("DELETE FROM instructors WHERE instructor_id = ?", (instructor_id,))
        self.connection.commit()

    def create_course(self, course_name, instructor_id):
        """
        Creates a new course in the database.

        :param course_name: The name of the course.
        :type course_name: str
        :param instructor_id: The ID of the instructor teaching the course.
        :type instructor_id: int
        """
        self.cursor.execute("INSERT INTO courses (course_name, instructor_id) VALUES (?, ?)", (course_name, instructor_id))
        self.connection.commit()

    def read_courses(self):
        """
        Reads all courses from the database.

        :return: A list of course records.
        :rtype: list
        """
        self.cursor.execute("SELECT * FROM courses")
        return self.cursor.fetchall()

    def update_course(self, course_id, course_name, instructor_id):
        """
        Updates a course's information.

        :param course_id: The ID of the course to update.
        :type course_id: int
        :param course_name: The new course name.
        :type course_name: str
        :param instructor_id: The new instructor ID.
        :type instructor_id: int
        """
        self.cursor.execute("UPDATE courses SET course_name = ?, instructor_id = ? WHERE course_id = ?", (course_name, instructor_id, course_id))
        self.connection.commit()

    def delete_course(self, course_id):
        """
        Deletes a course from the database.

        :param course_id: The ID of the course to delete.
        :type course_id: int
        """
        self.cursor.execute("DELETE FROM courses WHERE course_id = ?", (course_id,))
        self.connection.commit()

    def create_registration(self, student_id, course_id):
        """
        Registers a student for a course.

        :param student_id: The ID of the student.
        :type student_id: int
        :param course_id: The ID of the course.
        :type course_id: int
        """
        self.cursor.execute("INSERT INTO registrations (student_id, course_id) VALUES (?, ?)", (student_id, course_id))
        self.connection.commit()

    def read_registrations(self):
        """
        Reads all registrations from the database.

        :return: A list of registration records.
        :rtype: list
        """
        self.cursor.execute("SELECT * FROM registrations")
        return self.cursor.fetchall()

    def update_registration(self, student_id, course_id):
        """
        Updates a registration.

        :param student_id: The student ID.
        :type student_id: int
        :param course_id: The course ID.
        :type course_id: int
        """
        self.cursor.execute("UPDATE registrations SET student_id = ?, course_id = ? WHERE student_id = ? AND course_id = ?", (student_id, course_id, student_id, course_id))
        self.connection.commit()

    def delete_registration(self, student_id, course_id):
        """
        Deletes a registration.

        :param student_id: The student ID.
        :type student_id: int
        :param course_id: The course ID.
        :type course_id: int
        """
        self.cursor.execute("DELETE FROM registrations WHERE student_id = ? AND course_id = ?", (student_id, course_id))
        self.connection.commit()

    def close(self):
        """
        Closes the database connection.
        """
        self.connection.close()

    def backup(self, filename):
        """
        Creates a backup of the database.

        :param filename: The backup file name.
        :type filename: str
        """
        with open(filename, "w") as file:
            for line in self.connection.iterdump():
                file.write("%s\n" % line)

    def restore(self, filename):
        """
        Restores the database from a backup file.

        :param filename: The backup file name.
        :type filename: str
        """
        with open(filename, "r") as file:
            script = file.read()
        self.cursor.executescript(script)
        self.connection.commit()
