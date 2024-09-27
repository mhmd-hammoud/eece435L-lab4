import json
import re

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





