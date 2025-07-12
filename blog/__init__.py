import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

app=Flask(__name__)
app.config['SECRET_KEY']='c374eee07655cad6'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///site.db'
db=SQLAlchemy(app)
app.app_context().push()
bcrypt=Bcrypt()
login_manager=LoginManager(app)
login_manager.login_view='login'
login_manager.login_message_category='info'
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_USERNAME']='mailsblog57@gmail.com'
app.config['MAIL_PASSWORD']=''
app.config['PORT']=587
app.config['MAIL_USE_TLS']=True
mail=Mail(app)

from blog import routes