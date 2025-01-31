from flask import Flask, render_template, request, redirect, url_for
from models import db, Subject, Chapter

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route("/")
def home():
    subjects = Subject.query.all()
    return render_template("progress.html", subjects=subjects)

@app.route("/add_subject", methods=["GET", "POST"])
def add_subject():
    if request.method == "POST":
        name = request.form.get("name")
        if name:
            subject = Subject(name=name)
            db.session.add(subject)
            db.session.commit()
        return redirect(url_for("home"))
    return render_template("add_subject.html")

@app.route("/add_chapter/<int:subject_id>", methods=["GET", "POST"])
def add_chapter(subject_id):
    subject = Subject.query.get(subject_id)
    if request.method == "POST":
        name = request.form.get("name")
        if name:
            chapter = Chapter(name=name, completed=False, subject_id=subject_id)
            db.session.add(chapter)
            db.session.commit()
        return redirect(url_for("home"))
    return render_template("add_chapter.html", subject=subject)

@app.route("/toggle_chapter/<int:chapter_id>")
def toggle_chapter(chapter_id):
    chapter = Chapter.query.get(chapter_id)
    if chapter:
        chapter.completed = not chapter.completed
        db.session.commit()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
