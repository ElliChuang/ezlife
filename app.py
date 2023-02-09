from flask import *
from controller.user_auth import user_auth
from controller.account_books import account_books
from controller.account_book_id import account_book_id
from controller.collaborator import collaborator
from controller.account_book_auth import account_book_auth
from controller.chart import chart
from controller.csv_file import csv_file
from controller.account_settlement import account_settlement
from config import SECRET_KEY, JSON_AS_ASCII, TEMPLATES_AUTO_RELOAD, JSON_SORT_KEYS
from flask_socketio import SocketIO, join_room, leave_room


app = Flask(__name__, static_folder = "static", static_url_path = "/static")
socketio = SocketIO(app)
app.config["JSON_AS_ASCII"] = JSON_AS_ASCII
app.config["TEMPLATES_AUTO_RELOAD"] = TEMPLATES_AUTO_RELOAD
app.config["JSON_SORT_KEYS"] = JSON_SORT_KEYS
app.config['SECRET_KEY'] = SECRET_KEY


# 註冊Flask Blueprint
app.register_blueprint(user_auth)
app.register_blueprint(account_books)
app.register_blueprint(account_book_id)
app.register_blueprint(collaborator)
app.register_blueprint(account_book_auth)
app.register_blueprint(chart)
app.register_blueprint(csv_file)
app.register_blueprint(account_settlement)

# Pages
@app.route("/")
def index():
    return render_template("index.html")
@app.route("/home")
def homPage():
    return render_template("home.html")
@app.route("/account_book/<id>")
def book(id):
    return render_template("account_book.html")
@app.route("/account_book/<id>/chart")
def chart(id):
    return render_template("chart.html")
@app.route("/account_book/<id>/account_settlement")
def settlement(id):
    return render_template("account_settlement.html")

# @socketio.on('send_message')
# def handle_send_message_event(data):
#     print(f"{data['username']} has sent the {data['message']} to the room {data['room']}")
#     socketio.emit('receive_message', data, room=data['room'])

@socketio.on('join_room')
def handle_join_room_event(data):
    print(f"{data['username']} has joined the room")
    join_room(data["roomId"])
    socketio.emit("join_room_announcement", data)

@socketio.on('leave_room',)
def handle_leave_room_event(data):
    print(f"{data['collaboratorName']} has leaved the room")
    leave_room(data["roomId"])
    socketio.emit("leave_room_announcement", data)

@socketio.on('add_collaborator',)
def handle_invited_event(data):
    print(f"{data['collaboratorName']} has invited into the room")
    join_room(data["roomId"])
    socketio.emit("add_collaborator_announcement", data)

@socketio.on('add_journal_list')
def add_journal_list_event(data):
    socketio.emit("add_journal_list_announcement", data)

@socketio.on('delete_journal_list')
def delete_journal_list_event(data):
    socketio.emit("delete_journal_list_announcement", data)

if __name__ == '__main__':
    socketio.run(app, host = '0.0.0.0', port = 3000)
    # app.run( host = '0.0.0.0', port = 3000)