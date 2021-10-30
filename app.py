from server import create_app

app, socketio = create_app()
app.logger.info("Launching server....")

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0") # , debug=True, use_reloader=True)
