from flask import Blueprint,render_template
from blueprints.nmsllist import getnmsllocal
extension = Blueprint('xtension', __name__, subdomain='xtension')

@extension.route('/')
def home():
    return 'xtensions'

@extension.route('/unmaintainable')
def unmaintainable():
    return render_template('view/gg.html')

@extension.route('/nmsl')
def nmsl():
    return str(getnmsllocal())
