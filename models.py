from main import db
class User(db.model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=True)
    password = db.Column(db.String, nullable=True)
    email = db.Column(db.String, nullable=True, unique=True)  
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String, nullable=True)
    confirmed = db.Column(db.Boolean, default=False)