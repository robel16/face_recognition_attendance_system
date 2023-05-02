from attendance import bcrypt
from attendance import db, login_manager, admin
from flask_login import UserMixin, current_user
from flask_admin.contrib.sqla import ModelView


class Stud(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=30), nullable=False, unique=True)
    email_address = db.Column(db.String(length=30), nullable=False, unique=True)
    barcode = db.Column(db.Integer(), nullable=False, default=113000)
    takes = db.relationship('Course', backref='takes', lazy='select')
    stud_attended = db.relationship('Attendancee', backref="attended", lazy=True)

    def __repr__(self):
        return f'{self.id}'


@login_manager.user_loader
def load_user(stuff_id):
    return Stuff.query.get(int(stuff_id))


class Stuff(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    email_address = db.Column(db.String(length=30), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    owned_stuff = db.relationship('Course', backref='owned_stuff', lazy=True)

    def __repr__(self):
        return f'{self.id}'

    @property
    def password(self):
        return self.password_hash

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)


class Course(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    c_name = db.Column(db.String(length=30), nullable=False)
    code = db.Column(db.String(length=30), nullable=False)
    credit_hour = db.Column(db.Integer(), nullable=False)
    academic_year = db.Column(db.Integer(), nullable=False)
    semester = db.Column(db.Integer(), nullable=False)
    class_r = db.Column(db.String(length=30), nullable=False)
    stud_id = db.Column(db.Integer(), db.ForeignKey('stud.id'))
    stuff_id = db.Column(db.Integer(), db.ForeignKey('stuff.id'))
    taken = db.relationship('Attendancee', backref="taken", lazy=True)
    

    def __repr__(self):
        return f'{self.c_name}'


class Attendancee(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    a_day = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(length=20), nullable=False)
    course_id = db.Column(db.Integer(), db.ForeignKey('course.id'))
    stud_id = db.Column(db.Integer(), db.ForeignKey('stud.id'))

    class MyModelView(ModelView):
        def is_accessible(self):
            return current_user.is_authenticated


admin.add_view(ModelView(Stud, db.session))
admin.add_view(ModelView(Stuff, db.session))
admin.add_view(ModelView(Course, db.session))
admin.add_view(ModelView(Attendancee, db.session))
