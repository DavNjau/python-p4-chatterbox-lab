from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.before_first_request
def seed_db():
    if Message.query.count() == 0:
        db.session.add(Message(body='Hello 👋', username='Liza'))
        db.session.commit()

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        messages = Message.query.all()
        messages_list = [m.to_dict() for m in messages]
        response = make_response(
            jsonify(messages_list),
            200
        )
        return response

    if request.method == 'POST':
        data = request.get_json() or {}
        new_message = Message(
            body=data.get("body"),
            username=data.get("username")
        )
        db.session.add(new_message)
        db.session.commit()

        new_message_dict = new_message.to_dict()
        response = make_response(
            jsonify(new_message_dict),
            200
        )
        return response

@app.route('/messages/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def messages_by_id(id):
    message = Message.query.get(id)

    if message is None:
        response_body = {
            "message": "Sorry the message does not exist."
        }
        response = make_response(
            jsonify(response_body),
            404
        )
        return response

    if request.method == 'GET':
        message_dict = message.to_dict()
        response = make_response(
            jsonify(message_dict),
            200
        )
        return response

    if request.method == 'PATCH':
        data = request.get_json() or {}
        for attr, value in data.items():
            setattr(message, attr, value)
        db.session.add(message)
        db.session.commit()
        message_dict = message.to_dict()
        response = make_response(
            jsonify(message_dict),
            200
        )
        return response

    if request.method == 'DELETE':
        db.session.delete(message)
        db.session.commit()
        response_body = {
            "message": "The message has been deleted."
        }
        response = make_response(
            jsonify(response_body),
            200
        )
        return response


if __name__ == '__main__':
    app.run(port=5555)
