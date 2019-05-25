from  wtforms.fields import core
from wtforms.fields import html5
from wtforms.fields import simple
from wtforms import Form
from wtforms import validators
from wtforms import widgets
from wtforms import SubmitField
from wtforms import StringField,TextAreaField
from wtforms.validators import DataRequired,Email
from flask_wtf import FlaskForm
from flask_wtf import Form
class loginform(FlaskForm):
    name = StringField('账号', validators=[DataRequired()])
    password = StringField('密码',validators=[DataRequired()])
class signinform(FlaskForm):
    name = StringField('用户名',validators=[DataRequired()])
    password1 = StringField('密码',validators=[DataRequired()])
    password2 = StringField('确认密码',validators=[DataRequired()])
    email = StringField('确认邮箱',validators=[DataRequired(),Email()])
class new_post_form(FlaskForm):
    title = StringField('标题',validators=[DataRequired()])
    content = TextAreaField('内容',validators=[DataRequired()])
    section = StringField('分区',validators=[DataRequired()])
    submit = SubmitField('提交')
class comment_form(FlaskForm):
    content = TextAreaField('内容',validators=[DataRequired()])
    submit = SubmitField('提交')
