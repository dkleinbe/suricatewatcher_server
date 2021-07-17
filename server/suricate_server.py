import logging
from os import name
from flask import Flask, render_template, session, Response, request
from flask_socketio import SocketIO, emit
from watcher_video_cast_ns import WatcherVideoCastNS
from suricate_video_stream_ns import SuricateVideoStreamNS
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

@app.route('/debug')
def debug():
	return render_template('debug.html', async_mode=socketio.async_mode, connection_count=connection_count)

@socketio.on('connect', namespace='/debug')
def on_connect():
	app.logger.info("+ /debug: connect")

@socketio.on('connect', namespace='/cmd_suricate')
def on_connect():
	""" 
	We get a suricate so create video_cast namespace handlers class"
	"""
	app.logger.info("+ /cmd_suricate: connect with sid: " + str(request.sid))
	socketio.on_namespace(WatcherVideoCastNS('/video_cast', request.sid))

	socketio.emit('update', namespace='/debug')
		 
socketio.on_namespace(SuricateVideoStreamNS('/video_stream'))

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
	