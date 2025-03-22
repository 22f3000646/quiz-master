from flask import Blueprint,render_template,session,request,flash,redirect,url_for
user_blueprint = Blueprint("user_blueprint",__name__)
from models import Student_details,User,Subjects,Chapters,Mock,Question,Response,db,Options
import io
import base64

from datetime import datetime, timedelta

@user_blueprint.route('/dashboard')
def dashboard():
    user= User.query.filter_by(Email=session['user']).first()
    student = Student_details.query.filter_by(u_id = user.id).first()
    subjects = Subjects.query.all()
    chapters = Chapters.query.all()
    quizzes = Mock.query.all()
    if student and student.profile_picture:
        image = base64.b64encode(student.profile_picture).decode('utf-8')
    else:
        image = None  # No image available
    return render_template('/user/dashboard.html',user=student,
                           image=image,
                           subjects=subjects,chapters=chapters
                           ,quizzes=quizzes)
    
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

@user_blueprint.route('/quiz_result/<int:m_id>/<int:u_id>')
def quiz_result(m_id, u_id):
    """Fetches quiz results and provides feedback."""
    
    # Fetch quiz details
    quiz = Mock.query.get(m_id)
    user = Student_details.query.get(u_id)
    
    if not quiz or not user:
        flash("Invalid quiz or user.", "danger")
        return redirect(url_for('dashboard'))

    # Fetch user's responses for the quiz
    responses = Response.query.filter_by(u_id=u_id).all()

    # Prepare result data
    results = []
    correct_count = 0
    total_questions = len(quiz.questions)

    for response in responses:
        question = Question.query.get(response.q_id)
        correct_option = Options.query.filter_by(q_id=question.q_id, correctness=True).first()
        selected_option = Options.query.get(response.selected_o_id)

        is_correct = correct_option.o_id == response.selected_o_id if selected_option else False
        if is_correct:
            correct_count += 1
        
        results.append({
            "question_text": question.statement_text,
            "selected_answer": selected_option.statement_text if selected_option else "Not Answered",
            "correct_answer": correct_option.statement_text if correct_option else "No correct option",
            "is_correct": is_correct
        })

    # Calculate score
    score = (correct_count / total_questions) * 100 if total_questions > 0 else 0

    return render_template("quiz_result.html", user=user, quiz=quiz, results=results, score=score)

@user_blueprint.route('/result')
def result():
    return render_template('/user/scores.html')