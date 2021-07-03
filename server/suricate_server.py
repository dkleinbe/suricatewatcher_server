from os import name
from flask import Flask, render_template, session, Response
from flask_socketio import SocketIO, emit
import base64
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
toto = 0
img = ''

@app.route('/')
def index():
	return render_template('index.html', async_mode=socketio.async_mode)

@socketio.on('connect', namespace='/test')
def on_connect():
	print("+ session test")

@socketio.on('connect', namespace='/video')
def on_connect():
	print("+ session video")

@socketio.on('my_event', namespace='/video')
def test_message(message):
	print("my_event recieved")
	session['receive_count'] = session.get('receive_count', 0) + 1
	emit('my_response',
		 {'data': message['data'], 'count': session['receive_count']})
		 
@socketio.on('aaa')
def test_connect():
	print("Welcome, aaa received")
	emit('aaa_response', {'data': 'Server'})

@socketio.on('frame', namespace='/test')
def frame_received(frame):
	#print("frame received" + base64.b64encode(frame).decode("utf-8"))
	global toto
	global img
	
	print("+ Frame received " + str(toto))
	img = frame
	toto = toto + 1
	socketio.emit('frame', {'frame' : base64.b64encode(frame).decode("utf-8") }, namespace='/video')
	print("+ Frame sent ")

if __name__ == '__main__':
	print("Launching server...")
	socketio.run(app, host="192.168.0.10", port=8000, debug=True)
	#app.run(host='0.0.0.0', threaded=True)
