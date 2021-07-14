import logging
from os import name
from flask import Flask, render_template, session, Response
from flask_socketio import SocketIO, emit
import base64
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, logger = False)
connection_count = 0
toto = 0
img = ''

@app.route('/')
def index():
	return render_template('index.html', async_mode=socketio.async_mode)

@socketio.on('connect', namespace='/video_stream')
def on_connect():
	app.logger.info("+ /video_stream: connect")
	


@socketio.on('connect', namespace='/video_cast')
def on_connect():
	global connection_count
	app.logger.info("+ /video_cast: connection: Starting video stream " + str(connection_count))
	socketio.emit('start_video_stream', {'payload' : 'aze'}, namespace='/cmd_suricate')
	connection_count += 1

@socketio.on('disconnect', namespace='/video_cast')
def on_disconnect():
	global connection_count
	connection_count -= 1
	app.logger.info("+ /video_stream disconnect " + str(connection_count))
	if connection_count == 0:
		socketio.emit('stop_video_stream', {'payload' : 'aze'}, namespace='/cmd_suricate')


@socketio.on('connect', namespace='/cmd')
def on_connect():
	app.logger.info("+ /cmd: connect")

@socketio.on('connect', namespace='/cmd_suricate')
def on_connect():
	app.logger.info("+ /cmd_suricate: connect")

@socketio.on('cmd_1', namespace='/cmd')
def test_message(message):
	
	app.logger.info("+ /cmd: cmd_1 recieved")

	session['receive_count'] = session.get('receive_count', 0) + 1
	emit('cmd_1_ack',
		 {'data': message['data'], 'count': session['receive_count']})
	socketio.emit('start_video_stream', {'payload' : 'aze'}, namespace='/cmd_suricate')
		 

@socketio.on('frame', namespace='/video_stream')
def frame_received(frame):
	#print("frame received" + base64.b64encode(frame).decode("utf-8"))
	global toto
	global img
	
	app.logger.info("+ /video_stream: Frame received " + str(toto))
	img = frame
	toto = toto + 1
	socketio.emit('frame', {'frame' : base64.b64encode(frame).decode("utf-8") }, namespace='/video_cast')
	app.logger.info("+ /video_cast: Frame sent ")

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

if __name__ == '__main__':

	#logging.basicConfig(encoding='utf-8', level=logging.DEBUG)
	logging.getLogger('suricate_server').setLevel(logging.DEBUG)
	
	#logging.getLogger('socketio').setLevel(logging.ERROR)
	#logging.getLogger('engineio').setLevel(logging.ERROR)

	app.logger.info("Launching server...")
	
	socketio.run(app, host="0.0.0.0", debug=True)
	