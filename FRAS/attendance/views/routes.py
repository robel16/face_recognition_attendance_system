from sre_constants import SUCCESS
from attendance import app,db
from flask import render_template, redirect, url_for, flash, request
from attendance.forms import LoginForms, RegisterForms, TakAttendForm, AttendReportForm
from attendance.models import Stuff, Course,Stud, Attendancee
from flask_login import login_user, login_required, current_user, logout_user

import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
import csv


@app.route('/')
@app.route("/home")
def home_page():
    return render_template('home.html')


@app.route("/stuff", methods=['GET', 'POST'])
@login_required
def stuff_page():
    attendForm = TakAttendForm()
    reportForm = AttendReportForm()
    if request.method == "POST":
        take_attend = request.form.get('take_attend')
        t_attend = Course.query.filter_by(c_name=take_attend).first()
        if t_attend:
            courseid=t_attend.id
            print(courseid)
            cap = cv2.VideoCapture(1)
           # t_attend.owned_stuff = Attendancee.id
            path = 'attendance\images'
            images = []
            personNames = []
            myList = os.listdir(path)
            print(myList)
            for cu_img in myList:
                current_Img = cv2.imread(f'{path}/{cu_img}')
                images.append(current_Img)
                personNames.append(os.path.splitext(cu_img)[0])
            print(personNames)

            def faceEncodings(images):
                encodeList = []
                for img in images:
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    encode = face_recognition.face_encodings(img)[0]
                    encodeList.append(encode)
                return encodeList

            def attendance(name):
                with open('attendance\Attendance.csv', 'r+') as f:
                    myDataList = f.readlines()
                    nameList = []
                    for line in myDataList:
                        entry = line.split(',')
                        nameList.append(entry[0])
                    if name not in nameList:
                        time_now = datetime.now()
                        tStr = time_now.strftime('%H:%M:%S')
                        dStr = time_now.strftime('%d/%m/%Y')
                        f.writelines(f'\n{name},{tStr},{dStr}')
                        at=Attendancee(a_day=time_now.date(),stud_id=name,course_id=courseid,time=time_now.time(),status='p')
                        db.session.add(at)
                        db.session.commit()
                      

            encodeListKnown = faceEncodings(images)
            print('All Encodings Complete!!!')

            cap = cv2.VideoCapture(0)

            while True:
                ret, frame = cap.read()
                faces = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
                faces = cv2.cvtColor(faces, cv2.COLOR_BGR2RGB)

                facesCurrentFrame = face_recognition.face_locations(faces)
                encodesCurrentFrame = face_recognition.face_encodings(faces, facesCurrentFrame)

                for encodeFace, faceLoc in zip(encodesCurrentFrame, facesCurrentFrame):
                    matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
                    faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
                    #print(faceDis)
                    matchIndex = np.argmin(faceDis)

                    if matches[matchIndex]:
                        name = personNames[matchIndex].upper()
                        # print(name)
                        y1, x2, y2, x1 = faceLoc
                        y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.rectangle(frame, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                        cv2.putText(frame, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                        attendance(name)

                cv2.imshow('Webcam', frame)
                if cv2.waitKey(1) == ord('q'):
                    break

            cap.release()
            cv2.destroyAllWindows()

   # course = Course.query.all()  # objects.filter_by(owned_stuff=).first
    course=Course.query.filter_by(stuff_id=current_user.id)
    owner=Course.query.filter_by(stuff_id=current_user.id)
    if request.method == "POST":
        report_attend = request.form.get('take_attend')
        r_attend = Attendancee.query.filter_by(id=report_attend).first()

        if r_attend:
            csv_file = open('attendance\Attendance.csv')
            fields = []
            rows = []
            with open('attendance', 'r') as csv_file:
                csvreader = csv.reader(csv_file)
                print(csvreader)
                fields = next("csvreader = ",csvreader)


            csv_reader = csv.reader(csv_file, delimiter=',')
            next(csv_reader)
            for row in csv_reader:
                print(row)
            csv_file.close()
            attend_taken ='attendance\Attendance.csv'
            db.session.add(attend_taken)
            db.session.commit()

    return render_template('stuff.html', attendForm=attendForm, course=course, reportForm=reportForm)


@app.route("/view_attend")
def view_attend_page():
    attend=Attendancee.query.filter_by(course_id=current_user.id)
    taken=Course.query.filter_by(stuff_id=current_user.id)
    if request.method == "GET":
        at=Attendancee.query.all()# Stud.query.filter_by( takes= current_course)
    return render_template('view_attend.html', at=at,attend=attend,taken=taken)


@app.route("/register", methods=['GET', 'POST'])
def register_page():
    form = RegisterForms()
    if form.validate_on_submit():
        user_to_create = Stuff(username=form.username.data,
                               email_address=form.email.data,
                               password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f'Account created successfully! you are now logged in as: {user_to_create.username}', category='success')
        return redirect(url_for('stuff_page'))
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'there was an error with creating a user:{err_msg}', category='danger')
    return render_template('register.html', form=form)


@app.route('/stuff_login', methods=['GET', 'POST'])
def login_page():
    form = LoginForms()
    if form.validate_on_submit():
        attempted_user = Stuff.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
            login_user(attempted_user)
            flash(f'success! you are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('stuff_page'))
        else:
            flash('username and password are not match please try again', category='danger')

    return render_template('login.html', form=form)


@app.route('/admin')
@login_required
def admin():
    user_id = current_user.id
    if user_id == 1:
        flash("sorry you have to be the admin to access the admin page")
        return redirect(url_for('login_page'))

    else:

        return render_template("admin.html")


@app.route('/logout')
def logout_page():
    logout_user()
    flash('you have been logged out!', category='info')
    return redirect(url_for("home_page"))
