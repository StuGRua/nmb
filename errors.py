from flask import Flask,request,render_template,redirect,url_for
def return404():
    return '<h1>404 not found</h1>'
def return500():
    return '<h1>500 error</h1>'