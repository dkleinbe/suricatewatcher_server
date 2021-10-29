from server import create_app, app, socketio

app.logger.info("Launching server...")
socketio.run(app, host="0.0.0.0", debug=False)