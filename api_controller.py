from flask import Flask, jsonify
from app import app, db  # Import the initialized app and db
from models import Subjects, Chapters, Mock, scores


with app.app_context():
    @app.route('/subjects',methods=['GET'])
    def get_subjects():
        subjects = Subjects.query.all()
        return jsonify([{'id': sub.s_id,'name': sub.name,'description': sub.desc} for sub in subjects])

    @app.route('/subjects/<int:subject_id>/chapters', methods=['GET'])
    def get_chapters(subject_id):
        chapters = Chapters.query.filter_by(s_id=subject_id).all()
        if not chapters:
            return jsonify({'message': 'No chapters found for this subject'}), 404
        return jsonify([{'id': ch.c_id, 'name': ch.name, 'description': ch.desc} for ch in chapters])

    @app.route('/chapters/<int:chapter_id>/quizzes', methods=['GET'])
    def get_mock_tests(chapter_id):
        mocks = Mock.query.filter_by(c_id=chapter_id).all()
        if not mocks:
            return jsonify({'message': 'No mock tests found for this chapter'}), 404
        return jsonify([
            {'id': mock.m_id, 'date': mock.date, 'duration': mock.duration,
             'total_marks': mock.total_marks, 'no_of_questions': mock.no_of_ques,
             'remarks': mock.remarks}
            for mock in mocks
        ])

    @app.route('/users/<int:user_id>/scores', methods=['GET'])
    def get_user_scores(user_id):
        user_scores = scores.query.filter_by(u_id=user_id).all()
        if not user_scores:
            return jsonify({'message': 'No scores found for this user'}), 404
        return jsonify([
            {'mock_id': score.m_id, 'score': score.score, 'positive_score': score.positive_score,
             'time_required': score.time_req, 'remark': score.remark}
            for score in user_scores
        ])


if __name__ == '__main__':
    app.run(debug=True)
