from flask import Blueprint,render_template,request,flash,redirect,url_for,session
admin = Blueprint("admin",__name__)
from flask_login import login_required
from sqlalchemy.exc import IntegrityError
from datetime import datetime,date
from extension import db
from models import User,Subjects,Chapters,Mock,Question,Options,Student_details,scores
import base64

@login_required
@admin.route('/',methods=['GET','POST'])
def dashboard():
    search_query = request.args.get('search', '').strip()
    subject_filter = request.args.get('subjectfilter', '')
    chapter_filter = request.args.get('chapterfilter', '')
    date_filter = request.args.get('date', '')
    query = Mock.query.join(Chapters).join(Subjects)
    if search_query:
        query = query.filter((Subjects.name.ilike(f"%{search_query}%")) |(Chapters.name.ilike(f"%{search_query}%")))
    if subject_filter:
        query = query.filter(Subjects.name == subject_filter)
    if chapter_filter:
        query = query.filter(Chapters.name == chapter_filter)
    if date_filter:
        try:
            selected_date = datetime.strptime(date_filter, '%Y-%m-%d').date()  # Convert string to Date
            query = query.filter(db.func.date(Mock.date) == selected_date)  # Compare only the date part
        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD.", "danger")
    mocks = query.all()
    if not mocks:
        mocks = []
    subjects = Subjects.query.all()
    chapters = Chapters.query.all()
    search_query = request.args.get('usersearch', '').strip()  # Get search input

    query = Student_details.query  
    if search_query:
        query = query.filter(Student_details.full_name.ilike(f"%{search_query}%"))  
    users = query.all()  
    return render_template(
        '/admin/dashboard.html',
        mocks=mocks,
        subjects=subjects,
        chapters=chapters,  
        users=users
    )

@login_required
@admin.route('/manage_subject')
def manage_sub():
    search_subject = request.args.get('subject_search', '').strip()
    if search_subject:
        subjects = Subjects.query.filter(Subjects.name.ilike(f"%{search_subject}%")).all()
    else:
        subjects = Subjects.query.all()
    return render_template('admin/subject_management.html', subjects=subjects)

@login_required
@admin.route('/view_sub/<int:id>')
def view_sub(id):
    subject = Subjects.query.get_or_404(id)
    chapters = subject.chapters
    
    return render_template('admin/view_sub.html',chapters=chapters)

@login_required
@admin.route('/create_sub',methods=['GET', 'POST'])
def create_sub():
    if request.method=="POST":
        name = request.form.get('name')
        desc = request.form.get('desc')
        if not name:  
            flash('Subject name is required!','warning')
            return render_template('admin/new_sub.html')
        try:
            subject= Subjects(name=name,desc=desc)
            db.session.add(subject)
            db.session.commit()
            flash('New subject has been successfully added!','success')
            return redirect(url_for('admin.manage_sub'))
        except IntegrityError:
            db.session.rollback()
            flash('This subject already exists.Try another.','error')
            return redirect(url_for('admin.create_sub'))
    return render_template('admin/new_sub.html')

@login_required
@admin.route('/delete-subject/<int:id>', methods=['POST'])
def delete_sub(id):
    subject = Subjects.query.get_or_404(id)
    if subject:
        db.session.delete(subject)
        db.session.commit()
        flash("Subject deleted successfully!","danger")
    return redirect(url_for('admin.manage_sub'))

@login_required
@admin.route('/edit-subject/<int:id>', methods=['GET', 'POST'])
def edit_sub(id):
    subject = Subjects.query.get_or_404(id)

    if request.method == 'POST':
        new_name= request.form.get('name')
        new_desc = request.form.get('desc')
        if new_name or new_desc:
            try:
                subject.name = new_name 
                subject.desc = new_desc
                db.session.commit()
                flash("Subject updated successfully!","success")
                return redirect(url_for('admin.manage_sub'))
            except IntegrityError:
                db.session.rollback()
                flash('This subject already exists.Try another.','error')
                return redirect(url_for('admin.manage_sub'))
        return redirect(url_for('admin.manage_sub'))

    return render_template('admin/edit_sub.html',sub=subject)

@login_required
@admin.route('/create_chapter/<int:s_id>',methods=['GET','POST'])
def create_chapter(s_id):
    if request.method=="POST":
        name = request.form.get('name')
        desc = request.form.get('desc')
        existing_chapter = Chapters.query.filter_by(name=name).first()
        if existing_chapter:
            flash('chapter already exists','error')
            return render_template('admin/new_chapter.html')
        new_chap = Chapters(s_id=s_id,name =name,desc= desc)
        db.session.add(new_chap)
        db.session.commit()
        flash('Chapter added successfully!')
        return redirect(url_for('admin.manage_sub'))
    return render_template('admin/new_chapter.html',s_id=s_id)

@login_required
@admin.route('/delete-chapter/<int:id>', methods=['POST'])
def delete_chapter(id):
    chapter = Chapters.query.get(id)
    if chapter:
        db.session.delete(chapter)
        db.session.commit()
        flash("Chapter deleted successfully!", "success")
    return redirect(url_for('admin.view_sub',id=chapter.s_id))

@login_required
@admin.route('/edit-chapter/<int:c_id>', methods=['GET', 'POST'])
def edit_chap(c_id):
    chapter = Chapters.query.get(c_id)

    if request.method == 'POST':
        chapter.name = request.form['name']
        chapter.desc = request.form['desc']
        db.session.commit()
        flash("chapter updated successfully!", "success")
        return redirect(url_for('admin.view_sub',id=chapter.subjects.s_id))
    return render_template('/admin/edit_chapter.html',chap=chapter)

@login_required
@admin.route('/add_quiz', methods=['GET', 'POST'])
def add_quiz():
    subjects = Subjects.query.all()  
    selected_subject = request.form.get("subject") 
    chapters = [] 

    if selected_subject: 
        subject = Subjects.query.filter_by(name=selected_subject).first()
        if subject:
            chapters = subject.chapters  

    if request.method == 'POST' and request.form.get("chapter"):  
        chapter_id = request.form.get("chapter")
        date =datetime.strptime(request.form['date'],"%Y-%m-%dT%H:%M")
        duration = request.form.get("duration")
        marks = request.form.get("marks")
        questions = request.form.get("questions")
        remarks = request.form.get("remarks") 
        if date<date.today():
            flash("date should be of today or future","warning")
            return render_template('admin/new_quiz.html',subjects=subjects,selected_subject=selected_subject,chapters=chapters)
        new_mock = Mock(
            c_id=chapter_id,
            date=date,
            duration=duration,
            total_marks=marks,
            no_of_ques=questions,
            remarks=remarks
        )
        db.session.add(new_mock)
        db.session.commit()
        flash("Quiz added successfully!","success")
        return redirect(url_for('admin.dashboard'))  

    return render_template('admin/new_quiz.html',subjects=subjects,selected_subject=selected_subject,chapters=chapters)

@login_required
@admin.route('/live_quiz/<int:m_id>')
def live_quiz(m_id):
    mock = Mock.query.get_or_404(m_id)
    mock.live=True
    db.session.commit()
    flash('Quiz lived successfully!','danger')
    return redirect(url_for('admin.dashboard'))

@login_required
@admin.route('/quiz/edit/<int:m_id>',methods=['GET','POST'])
def edit_quiz(m_id):
    today=date.today().isoformat()
    mock=Mock.query.get_or_404(m_id)
    chapter =Chapters.query.get_or_404(mock.c_id)
    chapters = Chapters.query.all()
    subject= Subjects.query.filter_by(s_id=chapter.s_id).first()
    subjects = Subjects.query.all()
    if request.method=='POST':
        mock.date=datetime.strptime(request.form['date'],"%Y-%m-%d").date()
        mock.duration= request.form.get("duration")
        mock.remarks = request.form['remarks']
        mock.total_marks = request.form['marks']
        mock.no_of_ques= request.form['questions']        
        db.session.commit()
        flash('Quiz updated successfully!','success')
        return redirect(url_for('admin.dashboard'))    
    return render_template('admin/edit_quiz.html',mock=mock,
                           chapters=chapters,
                           chapter=chapter,
                           subject=subject,
                           subjects = subjects,
                           today=today,
                           m_id=m_id)

@login_required
@admin.route('/quiz/delete/<int:m_id>')
def delete_quiz(m_id):
    mock = Mock.query.get_or_404(m_id)
    db.session.delete(mock)
    db.session.commit()
    flash('Quiz deleted successfully!','danger')
    return redirect(url_for('admin.dashboard'))

# crud functionalites for questions
@login_required
@admin.route('/quiz/<int:q_id>/questions',methods=['GET','POST'])
def manage_questions(q_id):
    quiz = Mock.query.get_or_404(q_id)
    questions = Question.query.filter_by(m_id=q_id).all()
    for question in questions:
        if question.statement_pic:
            question.image_base64 = base64.b64encode(question.statement_pic).decode('utf-8')

    if request.method == 'POST':
        statement = request.form.get('statement')
        marks = float(request.form.get('marks', 0))
        image = request.files.get('statement_pic')

        statement_pic_name = image.filename if image else None
        statement_pic = image.read() if image else None

        total_existing_questions = len(questions)
        total_marks = sum(q.marks for q in questions)

        if total_existing_questions >= quiz.no_of_ques:
            flash("Cannot add more questions. Limit reached.", "danger")
        elif total_marks + marks > quiz.total_marks:
            flash("Cannot exceed total marks for quiz.", "danger")
        else:
            new_question = Question(
                m_id=q_id,
                statement_text=statement,
                statement_pic_name=statement_pic_name,
                statement_pic=statement_pic,
                marks=marks
            )
            db.session.add(new_question)
            db.session.commit()
            flash("Question added successfully!", "success")

        return redirect(url_for('admin.manage_questions', q_id=q_id))

    return render_template('admin/question_form.html', quiz=quiz, questions=questions)

@login_required
@admin.route('/edit_question/<int:que_id>', methods=['POST'])
def edit_question(que_id):
    question = Question.query.get_or_404(que_id)
    
    # Get new values from form
    question.statement_text = request.form['statement']
    question.marks = float(request.form['marks'])
    
    if 'statement_pic' in request.files:
        image = request.files['statement_pic']
        if image.filename:
            question.statement_pic_name = image.filename
            question.statement_pic = image.read()
    
    db.session.commit()
    flash("Question updated successfully", "success")
    
    return redirect(url_for('admin.manage_questions', q_id=question.m_id))

@login_required
@admin.route('/question/<int:que_id>/delete',methods=['POST'])
def delete_question(que_id):
    if request.method=='POST':
        question = Question.query.get_or_404(que_id)
        q_id = question.m_id
        db.session.delete(question)
        db.session.commit()
        flash("Question deleted successfully!","success")
        return redirect(url_for('admin.manage_questions',q_id=q_id))
    return redirect(url_for('admin.manage_questions',q_id = q_id))

@login_required
@admin.route('/question/<int:que_id>/options', methods=['GET','POST'])
def manage_options(que_id):
    question = Question.query.get_or_404(que_id)
    options = Options.query.filter_by(q_id=que_id).all()
    
    if question.statement_pic:
        question.image_base64 = base64.b64encode(question.statement_pic).decode('utf-8')


    if request.method == 'POST':
        statement = request.form.get('statement')
        correct = True if request.form.get('correct') == 'on' else False

        if correct:
            for option in options:
                option.correctness = False
        
        new_option = Options(statement_text=statement, correctness=correct,q_id=que_id)
        db.session.add(new_option)
        db.session.commit()
        flash("Option added successfully!","success")

        return redirect(url_for('admin.manage_options',que_id=que_id))

    return render_template('admin/manage_options.html', question=question, options=options)

@login_required
@admin.route('/option/<int:option_id>/delete',methods=['POST'])
def delete_option(option_id):
    option = Options.query.get_or_404(option_id)
    que_id = option.q_id
    db.session.delete(option)
    db.session.commit()
    flash("Option deleted successfully!","success")
    return redirect(url_for('admin.manage_options',que_id=que_id))

@login_required
@admin.route('/option/<int:option_id>/edit', methods=['POST'])
def edit_option(option_id):
    option = Options.query.get_or_404(option_id)
    question_id = option.q_id
    new_text = request.form.get('new_text')
    correctness = 'correctness' in request.form  
    if correctness:
        all_options = Options.query.filter_by(q_id=question_id).all()
        for opt in all_options:
            opt.correctness = False
    option.statement_text = new_text
    option.correctness = correctness
    db.session.commit()

    flash("Option updated successfully!","success")
    return redirect(url_for('admin.manage_options',que_id=question_id))

# to render user details

@login_required
@admin.route('/user/<int:id>', methods=['GET'])
def user_details(id):
    user = User.query.get_or_404(id)
    student = Student_details.query.get_or_404(id)
    quiz_scores = scores.query.filter_by(u_id=id).all()
    profile_pic = None
    if student.profile_picture:
        profile_pic = base64.b64encode(student.profile_picture).decode('utf-8')
    for score in quiz_scores:
        quiz_obj = Mock.query.get(score.m_id)
        score.quiz = quiz_obj  
        if quiz_obj:
            chapter = Chapters.query.get(quiz_obj.c_id)
            score.chapter_name = chapter.name if chapter else "N/A"
        else:
            score.chapter_name = "N/A"
    
    return render_template(
        'admin/user_details.html',user=user,Student_details=student,quiz_scores=quiz_scores,profile_pic=profile_pic)

@login_required
@admin.route('/summary')
def admin_summary():
    total_users = User.query.count()
    total_subjects = Subjects.query.count()
    total_chapters = Chapters.query.count()
    total_mocks = Mock.query.count()
    total_questions = Question.query.count()
    total_scores = scores.query.count()
    score_data = db.session.query(scores.m_id, db.func.avg(scores.score)).group_by(scores.m_id).all()
    mock_ids = [m_id for m_id, _ in score_data]
    avg_scores = [round(avg, 2) for _, avg in score_data]

    return render_template('admin/summary.html',
                           total_users=total_users,
                           total_subjects=total_subjects,
                           total_chapters=total_chapters,
                           total_mocks=total_mocks,
                           total_questions=total_questions,
                           total_scores=total_scores,
                           mock_ids=mock_ids,
                           avg_scores=avg_scores)

