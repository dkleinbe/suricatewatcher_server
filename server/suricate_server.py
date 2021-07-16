import logging
from os import name
from flask import Flask, render_template, session, Response, request
from flask_socketio import SocketIO, emit
from video_cast_namespace import VideoCastNamespace
import base64
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

logging.config.fileConfig('logger.conf',disable_existing_loggers=False)
my_logger = logging.getLogger('suricate_server')
my_logger.info('Logger init done')

socketio = SocketIO(app, logger = True)

connection_count = 0
toto = 0
img = ''

@app.route('/')
def index():
	return render_template('index.html', async_mode=socketio.async_mode, connection_count=connection_count)

@socketio.on('connect', namespace='/video_stream')
def on_connect():
	app.logger.info("+ /video_stream: connect")
	

@socketio.on('connect', namespace='/cmd')
def on_connect():
	app.logger.info("+ /cmd: connect")

@socketio.on('connect', namespace='/cmd_suricate')
def on_connect():
	""" 
	We get a suricate so create video_cast namespace handlers class"
	"""
	app.logger.info("+ /cmd_suricate: connect with sid: " + str(request.sid))
	socketio.on_namespace(VideoCastNamespace('/video_cast', request.sid))

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
	