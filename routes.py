from flask import Blueprint,render_template,session,request,flash,redirect,url_for,jsonify
user_blueprint = Blueprint("user_blueprint",__name__)
from flask_login import login_required,current_user
from models import Student_details,User,Subjects,Chapters,Mock,Question,Response,db,Options,scores
from sqlalchemy import or_,func
import base64
from datetime import datetime, timedelta

@login_required
@user_blueprint.route('/dashboard')
def dashboard():
    user = current_user
    student = Student_details.query.filter_by(u_id=user.id).first()
    subjects = Subjects.query.all()
    chapters = Chapters.query.all()
    quizzes = Mock.query
    now = datetime.now()
    start_date = now 
    end_date = now + timedelta(days=5)
    quizzes = Mock.query.filter(Mock.date >= start_date, Mock.date <= end_date)
    attempted_count = None
    total_mocks = Mock.query.count()
    attempted_mocks = db.session.query(scores.m_id).filter(scores.u_id == user.id).distinct().count()
    if total_mocks == 0:
        attempted_count = 0
    else:
        attempted_count = (attempted_mocks / total_mocks) * 100   
    subject_id = request.args.get('subject_id')
    chapter_id = request.args.get('chapter_id')
    search_query = request.args.get('query')
    if subject_id:
        quizzes = quizzes.join(Chapters).filter(Chapters.s_id == subject_id)
    if chapter_id:
        quizzes = quizzes.filter(Mock.c_id == chapter_id)
    if search_query:
        quizzes = quizzes.join(Chapters).join(Subjects).filter(or_(Mock.remarks.ilike(f"%{search_query}%"),Chapters.name.ilike(f"%{search_query}%"),Subjects.name.ilike(f"%{search_query}%")))
    quizzes = quizzes.all()
    image = None
    if student and student.profile_picture:
        image = base64.b64encode(student.profile_picture).decode('utf-8')

    return render_template('/user/dashboard.html', user=student,image=image,subjects=subjects,chapters=chapters,quizzes=quizzes,attempted_count=attempted_count)
def has_attempted_quiz(user_id,mock_id):
    attempted = scores.query.filter_by(u_id=user_id,m_id=mock_id).first()
    return attempted is not None
 
@login_required  
@user_blueprint.route('/test/<int:qid>/<int:sid>')
def start_test(qid,sid):
    student = Student_details.query.get(sid)
    quiz = Mock.query.get(qid)
    questions = Question.query.filter_by(m_id=qid).all()
    subject = Subjects.query.get(quiz.chapters.subjects.s_id)
    current_time = datetime.now()  
    if has_attempted_quiz(sid, qid):
        flash("The quiz is already attempted by you", "error")
        return redirect(url_for('user_blueprint.dashboard'))
    if quiz.live != True:
        flash("The quiz is not currently live", "error")
        return redirect(url_for('user_blueprint.dashboard'))
    if current_time > quiz.date:
        flash("The quiz submission deadline has passed!", "error")
        return redirect(url_for('user_blueprint.dashboard'))
    responses = {resp.q_id: resp.selected_o_id for resp in Response.query.filter_by(u_id=sid).all()}
    if student and student.profile_picture:
        image = base64.b64encode(student.profile_picture).decode('utf-8')
    else:
        image = None 
    for question in questions:
        if question.statement_pic:
            question.image_base64 = base64.b64encode(question.statement_pic).decode('utf-8')
    return render_template(
        '/user/quiz.html',image=image,user=student,quiz=quiz,subject=subject,questions=questions,responses=responses)

@login_required
@user_blueprint.route('/save_response', methods=['POST'])
def save_response():
    try:
        user_email = current_user.Email
        user = User.query.filter_by(Email=user_email).first()
        student = Student_details.query.filter_by(u_id=user.id).first()
        q_id = int(request.form.get('q_id'))
        selected_o_id = int(request.form.get('selected_o_id'))
        existing_response = Response.query.filter_by(u_id=student.u_id, q_id=q_id).first()
        if existing_response:
            existing_response.selected_o_id = selected_o_id  
        else:
            new_response = Response(u_id=student.u_id, q_id=q_id, selected_o_id=selected_o_id)
            db.session.add(new_response)
        db.session.commit()
        return jsonify({"message": "Response saved successfully!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}),400

@login_required
@user_blueprint.route('/submit_quiz/<int:m_id>')
def submit_quiz(m_id):
    try:
        user_email = current_user.Email
        user = User.query.filter_by(Email=user_email).first()
        student = Student_details.query.filter_by(u_id=user.id).first()
        quiz = Mock.query.get(m_id)
        if not quiz:
            flash("Quiz not submitted successfully!","danger")
            return redirect(url_for('user_blueprint.dashboard'))
        responses = Response.query.filter_by(u_id=student.u_id).all()
        score = 0
        for response in responses:
            correct_option = Options.query.filter_by(q_id=response.q_id, correctness=True).first()
            if correct_option and response.selected_o_id == correct_option.o_id:
                score += 1  
        new_score = scores(m_id=m_id, u_id=student.u_id, score=score, remark="Completed")
        db.session.add(new_score)
        db.session.commit()
        flash("Quiz submitted successfully!","success")
        return redirect(url_for('user_blueprint.dashboard'))
    except Exception as e:
        flash("Quiz not submitted successfully!","danger")
        return redirect(url_for('user_blueprint.dashboard'))

@login_required
@user_blueprint.route('/scores')
def scores_view():
    user = current_user
    student = Student_details.query.filter_by(u_id=user.id).first()
    user_scores = scores.query.filter_by(u_id=student.u_id).all()
    quiz_labels = [f"Quiz {s.m_id}" for s in user_scores]
    quiz_scores = [s.score for s in user_scores]    
    return render_template('user/scores.html',scores=user_scores,quiz_labels=quiz_labels,quiz_scores=quiz_scores)

@login_required
@user_blueprint.route('/score_details/<int:sc_id>')
def score_details(sc_id):
    score_record = scores.query.get_or_404(sc_id)
    quiz = Mock.query.get(score_record.m_id)
    user = current_user
    student = Student_details.query.filter_by(u_id=user.id).first()
    avg_marks = db.session.query(func.avg(scores.score)).filter(scores.m_id == quiz.m_id).scalar() or 0
    questions_data = []
    questions = Question.query.filter_by(m_id=quiz.m_id).order_by(Question.q_id).all()
    for q in questions:
        opts = Options.query.filter_by(q_id=q.q_id).all()
        user_response = Response.query.filter_by(u_id=student.u_id, q_id=q.q_id).first()
        user_selected = user_response.selected_o_id if user_response else None
        
        questions_data.append({"statement_text": q.statement_text,"options": opts,"user_selected": user_selected})    
    return render_template('user/score_details.html',quiz=quiz,score=score_record,questions=questions_data,avg_marks=avg_marks,user_marks=score_record.score)