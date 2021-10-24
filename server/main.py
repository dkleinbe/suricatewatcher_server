from flask import Blueprint, render_template
from flask_login import login_required, current_user
from . import db, socketio, server


main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    #return render_template('index4.html', name=current_user.name)   # type: ignore
    return render_template('index4.html', async_mode=socketio.async_mode, suricate_server=server)
