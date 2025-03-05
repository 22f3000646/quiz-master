from flask import Blueprint,render_template
user_blueprint = Blueprint("user_blueprint",__name__)

@user_blueprint.route('/dashboard')
def dashboard():
    return render_template('/user/dashboard.html')
@user_blueprint.route('/result')
def result():
    return render_template('/user/scores.html')