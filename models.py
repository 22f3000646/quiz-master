from werkzeug.security import generate_password_hash
from extension import db


class User(db.Model):
    __tablename__ ="user"
    id = db.Column(db.Integer,primary_key=True,autoincrement =True)
    Email = db.Column(db.String(20),unique=True,nullable = False)
    password = db.Column(db.String(128),nullable=False)
    role = db.Column(db.String(20),default = "student")
    
    def set_password(self,password):
        self.password = generate_password_hash(password)

class Student_details(db.Model):
    __tablename__="student_details"
    u_id = db.Column(db.Integer,db.ForeignKey('user.id'),primary_key = True,autoincrement = True)
    full_name = db.Column(db.String(50),nullable = False)
    qualification = db.Column(db.String(20),nullable = False)
    dob = db.Column(db.DateTime)
    profile_picture_name = db.Column(db.String(50))
    profile_picture = db.Column(db.LargeBinary)
    phone = db.Column(db.Integer)
    
    scores = db.relationship('scores', backref='user', lazy=True)

class Subjects(db.Model):
    __tablename__ ="subjects"
    s_id = db.Column(db.Integer,primary_key=True,autoincrement =True)
    name = db.Column(db.String(20),nullable = False , unique = True)
    desc = db.Column(db.String(50))
    
    chapters = db.relationship('Chapters',backref="subjects",lazy=True)

class Chapters(db.Model):
    __tablename__="chapters"
    c_id = db.Column(db.Integer,primary_key=True,autoincrement =True)
    s_id = db.Column(db.Integer,db.ForeignKey('subjects.s_id'))
    name = db.Column(db.String(20),nullable = False , unique = True)
    desc = db.Column(db.String(50))
    
    Mock = db.relationship('Mock',backref='chapters', lazy=True)

    
class Mock(db.Model):
    __tablename__="mock"
    m_id = db.Column(db.Integer,primary_key=True,autoincrement =True)
    c_id = db.Column(db.Integer,db.ForeignKey('chapters.c_id'))
    date = db.Column(db.DateTime)
    duration = db.Column(db.Integer)
    total_marks = db.Column(db.Float)
    no_of_ques = db.Column(db.Integer)
    remarks = db.Column(db.String(100))
    
    questions = db.relationship('Question',backref='mock', lazy=True)
    
class Question(db.Model):
    __tablename__="question"
    q_id = db.Column(db.Integer,primary_key=True,autoincrement =True)
    m_id = db.Column(db.Integer,db.ForeignKey('mock.m_id'))
    statement_text = db.Column(db.String(50))
    statement_pic_name = db.Column(db.String(50))
    statement_pic = db.Column(db.LargeBinary)
    statement_type = db.Column(db.String(10))
    o_id = db.Column(db.Integer)
    marks = db.Column(db.Float)
    neg_marking = db.Column(db.Float)
    
class Options(db.Model):
    __tablename__="options"
    q_id = db.Column(db.Integer,db.ForeignKey('question.q_id'))
    o_id = db.Column(db.Integer,primary_key=True,autoincrement =True)
    statement_text = db.Column(db.String(50))
    statement_pic_name = db.Column(db.String(50))
    statement_pic = db.Column(db.LargeBinary)
    statement_type = db.Column(db.String(10))
    correctness = db.Column(db.Boolean(10),default = False)
    
class scores(db.Model):
    __tablename__="scores"
    sc_id = db.Column(db.Integer,primary_key=True,autoincrement =True)
    m_id = db.Column(db.Integer,db.ForeignKey('mock.m_id'))
    u_id = db.Column(db.Integer,db.ForeignKey('student_details.u_id'))
    score = db.Column(db.Integer)
    positive_score = db.Column(db.Integer)
    time_req = db.Column(db.Integer)
    remark = db.Column(db.String(100))
    
def create_database():

    db.create_all()
    if not User.query.filter_by(Email="admin@123.gmail.com").first():
        admin = User(Email="admin@123.gmail.com",role="admin")
        admin.set_password("adminASDqwe123#") 
        db.session.add(admin)
        db.session.commit()