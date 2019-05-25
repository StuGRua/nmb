from models import User
from main import db,app
from flask_script import Manager
manager = Manager(app)
@manager.command
def