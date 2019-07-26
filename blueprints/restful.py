from flask import Blueprint,redirect,url_for,jsonify
import json
mb = Blueprint('m', __name__, subdomain='m')
@m.route('/')
def home():
    return 'home for m'

@m.route('/main')
def main():
    tenposts = posts.query.filter(posts.head==True).filter(posts.\
        topped==False).filter(posts.no_show==False).order_by(-posts.update_time).all()
    return tenposts