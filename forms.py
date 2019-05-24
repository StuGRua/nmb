from  wtforms.fields import core
from wtforms.fields import html5
from wtforms.fields import simple
from wtforms import Form
from wtforms import validators
from wtforms import widgets
from wtforms import StringField
from wtforms.validators import DataRequired,Email
from flask_wtf import FlaskForm
class loginform(FlaskForm):
    name = StringField('账号', validators=[DataRequired(),Email()])
    password = StringField('密码',validators=[DataRequired()])
class signinform(FlaskForm):
    name = StringField('用户名',validators=[DataRequired()])
    password1 = StringField('密码',validators=[DataRequired()])
    password2 = StringField('确认密码',validators=[DataRequired()])
    email = StringField('确认邮箱',validators=[DataRequired(),Email()])
