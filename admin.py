from flask import Blueprint,render_template,request,flash,redirect,url_for
admin = Blueprint("admin",__name__)

@admin.route('/')
def dashboard():
    return render_template('/admin/dashboard.html')

@admin.route('/manage_subject')
def manage_sub():
    from models import db,Subjects
    subjects = Subjects.query.all()
    return render_template('/admin/subject_management.html',subjects=subjects)
@admin.route('/view_sub/<int:id>')
def view_sub(id):
    from models import db,Chapters,Subjects
    subject = Subjects.query.filter_by(s_id = id).first()
    chapters = subject.chapters
    
    return render_template('admin/view_sub.html',chapters=chapters)

@admin.route('/create_sub',methods=['GET', 'POST'])
def create_sub():
    from models import db,Subjects
    if request.method=="POST":
        name = request.form.get('name')
        desc = request.form.get('desc')
        existing_subject = Subjects.query.filter_by(name=name).first()
        if existing_subject:
            flash('Subject already exists','error')
            return render_template('admin/new_sub.html')
        new_sub = Subjects(name = name,desc = desc)
        db.session.add(new_sub)
        db.session.commit()
        flash('Subject added successfully!')
        return redirect(url_for('admin.create_sub'))
    return render_template('admin/new_sub.html')

@admin.route('/delete-subject/<int:id>', methods=['POST'])
def delete_sub(id):
    from models import db,Subjects
    subject = Subjects.query.get(id)
    if subject:
        db.session.delete(subject)
        db.session.commit()
        flash("Subject deleted successfully!", "success")
    return redirect(url_for('admin.manage_sub'))

@admin.route('/edit-subject/<int:s_id>', methods=['GET', 'POST'])
def edit_sub(s_id):
    from models import Subjects,db
    subject = Subjects.query.get(s_id)

    if request.method == 'POST':
        subject.name = request.form['name']
        subject.desc = request.form['desc']
        db.session.commit()
        flash("Subject updated successfully!", "success")
        return redirect(url_for('admin.manage_sub'))

    return render_template('admin/edit_sub.html',sub=subject)

@admin.route('/create_chapter/<int:s_id>',methods=['GET', 'POST'])
def create_chapter(s_id):
    from models import db,Chapters
    if request.method=="POST":
        name = request.form.get('name')
        desc = request.form.get('desc')
        existing_chapter = Chapters.query.filter_by(name=name).first()
        if existing_chapter:
            flash('chapter already exists','error')
            return render_template('admin/new_chapter.html')
        new_chap = Chapters(s_id = s_id, name = name,desc = desc)
        db.session.add(new_chap)
        db.session.commit()
        flash('Chapter added successfully!')
        return redirect(url_for('admin.manage_sub'))
    return render_template('admin/new_chapter.html',id=s_id)

@admin.route('/delete-chapter/<int:id>', methods=['POST'])
def delete_chapter(id):
    from models import db,Chapters
    chapter = Chapters.query.get(id)
    if chapter:
        db.session.delete(chapter)
        db.session.commit()
        flash("Chapter deleted successfully!", "success")
    return redirect(url_for('admin.view_sub',id=chapter.s_id))


@admin.route('/edit-chapter/<int:c_id>', methods=['GET', 'POST'])
def edit_chap(c_id):
    from models import Chapters,db
    chapter = Chapters.query.get(c_id)

    if request.method == 'POST':
        chapter.name = request.form['name']
        chapter.desc = request.form['desc']
        db.session.commit()
        flash("chapter updated successfully!", "success")
        return redirect(url_for('admin.edit_chap',c_id=c_id))
    return render_template('/admin/edit_chapter.html',chap=chapter)

@admin.route('/add_quiz', methods=['GET', 'POST'])
def add_quiz():
    from models import db, Mock, Subjects, Chapters
    subjects = Subjects.query.all()  # Fetch all subjects from the database
    selected_subject = request.form.get("subject")  # Get selected subject from form
    chapters = []  # Empty chapter list by default

    if selected_subject:  # If a subject is selected, fetch its chapters
        subject = Subjects.query.filter_by(name=selected_subject).first()
        if subject:
            chapters = subject.chapters  # Assuming a relationship exists

    if request.method == 'POST' and request.form.get("chapter"):  # Ensure a chapter is selected
        chapter_id = request.form.get("chapter")
        date = request.form.get("date")
        duration = request.form.get("duration")
        marks = request.form.get("marks")
        questions = request.form.get("questions")
        remarks = request.form.get("remarks")

        # Create new Mock quiz entry
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

        flash("Quiz added successfully!", "success")
        return redirect(url_for('admin.add_quiz'))  # Redirect to refresh form

    return render_template('admin/new_quiz.html', subjects=subjects, selected_subject=selected_subject, chapters=chapters)
