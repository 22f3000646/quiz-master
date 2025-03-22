from flask import Blueprint,render_template,session,request,flash,redirect,url_for
user_blueprint = Blueprint("user_blueprint",__name__)
from models import Student_details,User,Subjects,Chapters,Mock,Question,Response,db,Options,scores
from sqlalchemy import or_
import base64

from datetime import datetime, timedelta
@user_blueprint.route('/dashboard')
def dashboard():
    user = User.query.filter_by(Email=session['user']).first()
    student = Student_details.query.filter_by(u_id=user.id).first()
    subjects = Subjects.query.all()
    chapters = Chapters.query.all()
    quizzes = Mock.query

    subject_id = request.args.get('subject_id')
    chapter_id = request.args.get('chapter_id')
    search_query = request.args.get('query')

    # Apply filters based on user input
    if subject_id:
        quizzes = quizzes.join(Chapters).filter(Chapters.s_id == subject_id)

    if chapter_id:
        quizzes = quizzes.filter(Mock.c_id == chapter_id)

    if search_query:
        quizzes = quizzes.join(Chapters).join(Subjects).filter(
            db.or_(
                Mock.remarks.ilike(f"%{search_query}%"),
                Chapters.name.ilike(f"%{search_query}%"),
                Subjects.name.ilike(f"%{search_query}%")
            )
        )

    quizzes = quizzes.all()

    # Handle profile picture
    image = None
    if student and student.profile_picture:
        image = base64.b64encode(student.profile_picture).decode('utf-8')

    return render_template('/user/dashboard.html', user=student,
                           image=image,
                           subjects=subjects, chapters=chapters,
                           quizzes=quizzes)

    
@user_blueprint.route('/test/<int:qid>/<int:sid>')
def start_test(qid, sid):
    student = Student_details.query.get(sid)
    quiz = Mock.query.get(qid)
    questions = Question.query.filter_by(m_id=qid).all()
    subject = Subjects.query.get(quiz.chapters.subjects.s_id)
    current_time = datetime.now() 
    
    if current_time > quiz.date:  
        flash("The quiz submission deadline has passed!","error")
        return redirect(url_for('dashboard'))

    # Fetch previously submitted responses
    responses = {resp.q_id: resp.selected_o_id for resp in Response.query.filter_by(u_id=sid).all()}

    if student and student.profile_picture:
        image = base64.b64encode(student.profile_picture).decode('utf-8')
    else:
        image = None  # No image available

    return render_template('/user/quiz.html', image=image, user=student, quiz=quiz, subject=subject, questions=questions, responses=responses)

@user_blueprint.route('/response/<int:q_id>/<int:qu_id>/<int:u_id>', methods=['GET', 'POST'])
def response(q_id, qu_id, u_id):
    if request.method == 'POST':
        try:
            form_u_id = request.form.get('u_id')  # Get user ID from form if provided
            if form_u_id:
                u_id = int(form_u_id)  # Ensure user ID remains valid
            
            for key, value in request.form.items():
                if key.startswith("option_"):  # Process only option selections
                    question_id = int(key.split("_")[1])  # Convert to integer
                    selected_o_id = int(value)  # Convert selected option to integer
                    
                    new_response = Response(u_id=u_id, q_id=question_id, selected_o_id=selected_o_id)
                    db.session.add(new_response)

            db.session.commit()
            flash("Responses submitted successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}", "danger")
        
        return redirect(url_for('some_view_function'))  # Redirect to an appropriate page

    return render_template('/user/quiz.html')

@user_blueprint.route('/submit_quiz/<int:m_id>/<int:u_id>', methods=['GET', 'POST'])
def submit_quiz(m_id, u_id):
    """Handles quiz submission, stores responses, and calculates the score."""
    
    # Get all user responses from the request form
    responses = {key: request.form[key] for key in request.form}

    # Fetch the quiz object
    quiz = Mock.query.get(m_id)
    if not quiz:
        flash("Quiz not found!", "danger")
        return redirect(url_for('dashboard'))

    # Store responses in the database
    for q_id, o_id in responses.items():
        user_response = Response(
            quiz_id=m_id,
            user_id=u_id,
            question_id=q_id.split("_")[1],  # Extract question ID
            selected_option=o_id
        )
        db.session.add(user_response)
    
    db.session.commit()  # Save to DB

    flash("Quiz submitted successfully!", "success")
    return "submitted"

@user_blueprint.route('/result', methods=['GET'])
def result():
    user = User.query.filter_by(Email=session['user']).first()
    student = Student_details.query.filter_by(u_id=user.id).first()

    # Get user-selected filter (default to 'all')
    time_filter = request.args.get('time_filter', 'all')

    query = (
        db.session.query(
            Mock.m_id,
            Mock.no_of_ques,
            Mock.date,
            Mock.duration,
            Mock.total_marks,
            scores.score,
            scores.remark
        )
        .join(scores, scores.m_id == Mock.m_id)
        .filter(scores.u_id == student.u_id)
    )

    if time_filter != 'all':
        days = int(time_filter)
        date_limit = datetime.now() - timedelta(days=days)
        query = query.filter(Mock.date >= date_limit)

    quiz_results = query.order_by(Mock.date.desc()).all()

    return render_template('user/scores.html', user=student, quiz_results=quiz_results)

@user_blueprint.route('/response/<int:q_id>', methods=['GET'])
def responsed(q_id):
    user = User.query.filter_by(Email=session['user']).first()
    student = Student_details.query.filter_by(u_id=user.id).first()

    # Fetch quiz details
    quiz = Mock.query.filter_by(m_id=q_id).first()
    
    if not quiz:
        return "Quiz not found", 404

    # Fetch questions and options
    questions = (
        db.session.query(
            Question.q_id,
            Question.statement_text,
            Question.statement_pic_name,
            Question.statement_type,
            Options.o_id,
            Options.statement_text.label("option_text"),
            Options.statement_pic_name.label("option_pic"),
            Options.correctness,
            Response.selected_o_id
        )
        .join(Options, Options.q_id == Question.q_id)
        .outerjoin(Response, (Response.q_id == Question.q_id) & (Response.u_id == student.u_id))
        .filter(Question.m_id == q_id)
        .order_by(Question.q_id)
        .all()
    )

    return render_template(
        'user/response.html',
        user=student,
        quiz=quiz,
        questions=questions
    )