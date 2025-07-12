from blog import db,login_manager,app
from datetime import datetime
from flask_login import UserMixin
from itsdangerous import URLSafeSerializer as safe
import time, datetime,jwt
from datetime import timezone

@login_manager.user_loader
def load_user(user_id):
    return user.query.get(int(user_id))

class PostVote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    vote_type = db.Column(db.String(10), nullable=False)  # 'upvote' or 'downvote'
    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='unique_user_post_vote'),)

class user(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(20),unique=True,nullable=False)
    email=db.Column(db.String(120),unique=True,nullable=False)
    image=db.Column(db.String(20),nullable=False, default='default.jpg')
    password=db.Column(db.String(60),nullable=False)
    posts=db.relationship('post',backref='author',lazy=True)

    def get_reset_token(self,expires_sec=600):
        payload = {
                "exp": datetime.datetime.now(tz=timezone.utc) + datetime.timedelta(seconds=expires_sec),
                'user_id':self.id
            }
        token = jwt.encode(payload, app.config['SECRET_KEY'])
        return (token)
    
    @staticmethod
    def verify_reset_token(token):
        try:
            s=jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            user_id=s['user_id']
        except:
            return None
        return user.query.get(user_id)

    def __repr__(self):
        return f"User ('{self.username}','{self.email}','{self.image}')"

class post(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(100),nullable=False)
    date_posted=db.Column(db.DateTime,nullable=False,default=datetime.datetime.utcnow)
    content=db.Column(db.Text,nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    upvotes = db.Column(db.Integer, default=0)
    downvotes = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"Post('{self.title}','{self.date_posted}')"
