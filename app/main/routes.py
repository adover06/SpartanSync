from flask import render_template
from flask import redirect
from flask import flash
from app.forms import LoginForm
from app import myapp_obj

from flask import render_template
from . import bp



@myapp_obj.route("/")
@myapp_obj.route("/index.html")

@myapp_obj.route("/home")
def home():
    tempData = {
        'title': 'Home Page',
        'assignments': [
            {
                'title': 'Assignment 1',
                'description': 'Introduction to Python',
                'due_date': '2024-04-15',
                'status': 'Pending',
                'points': 100,
                'link': '/assignment/1',
                'index': 1
            },
            {
                'title': 'Assignment 2',
                'description': 'Data Structures in Java',
                'due_date': '2024-04-20',
                'status': 'Submitted',
                'points': 95,
                'link': '/assignment/2',
                'index': 2
            },
            {
                'title': 'Assignment 3',
                'description': 'Database Design',
                'due_date': '2024-04-25',
                'status': 'Graded',
                'points': 88,
                'link': '/assignment/3',
                'index': 3
            }
        ],
        'classes': [
            {
                'title': 'CMPE 131',
                'description': 'Introduction to Software Engineering',
                'color': "#2E5B8B",
                'link': '/class/cmpe131',
                'img_link': 'https://cdn.pixabay.com/photo/2016/11/30/20/58/programming-1873854_1280.png'
            },
            {
                'title': 'CMPE 102',
                'description': 'Assembly Language Programming',
                'color': "#36C0F7",
                'link': '/class/cmpe102',
                'img_link':'https://cdn.pixabay.com/photo/2025/11/05/19/29/faroe-islands-9939486_1280.jpg'
            },{
                'title': 'CMPE 120',
                'description': 'Introduction to Computer Organization and Architecture',
                'color': "#3A6EA5",
                'link': '/class/cmpe120',
                'img_link': 'https://cdn.pixabay.com/photo/2014/08/26/21/27/service-428540_1280.jpg'
            },{
                'title': 'CS 146',
                'description': 'Data Structures and Algorithms',
                'color': "#20B2AA",
                'link': '/class/cs146',
                'img_link': 'https://cdn.pixabay.com/photo/2014/12/30/05/42/source-code-583537_1280.jpg'

            },{
                'title': 'MATH 32',
                'description': 'Multivariable Calculus',
                'color': "#60BFB1",
                'link': '/class/math32',
                'img_link': 'https://cdn.pixabay.com/photo/2016/02/14/09/44/nebulae-1199180_1280.jpg'
            }
        ]
    }
    return render_template('home.html', classes=tempData['classes'], assignments=tempData['assignments'])



@myapp_obj.route("/assign")
def assign():
    return render_template('assignmentcreate.html')

@myapp_obj.route("/assignment")
def assignment():
    tempAssignment = {
        'title': 'Assignment 1: Introduction to Python',
        'description': 'This assignment covers the basics of Python programming including variables, data types, and control structures.',
        'due_date': '2024-04-15',
        'status': 'Pending',
        'points': 100,
        'created_by': 'Prof. Smith',
        'instructions': 'Complete the following exercises in Python.',
    }
    return render_template('assignment.html', assignment=tempAssignment)