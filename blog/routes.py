from flask import render_template,url_for,flash,redirect,request,abort
from blog.models import user,post,Reply,ReplyVote
from blog.forms import (RegistrationForm,LoginForm,UpdateAccountForm,
                        PostForm,RequestResetForm,ResetPasswordForm)
# Reply to a post

from blog import app,db,bcrypt,mail
from blog.forms import (RegistrationForm,LoginForm,UpdateAccountForm,
                        PostForm,RequestResetForm,ResetPasswordForm)
from flask_login import login_user,current_user,logout_user,login_required
import secrets
import os
from PIL import Image
from flask_mail import Message

# Voting routes
from blog.models import PostVote

@app.route('/post/<int:post_id>/reply', methods=['POST'])
@login_required
def reply_post(post_id):
    pst = post.query.get_or_404(post_id)
    content = request.form.get('reply_content')
    if not content:
        flash('Reply cannot be empty.', 'warning')
        return redirect(request.referrer or url_for('post_show', post_id=post_id))
    reply = Reply(content=content, user_id=current_user.id, post_id=post_id)
    db.session.add(reply)
    db.session.commit()
    flash('Reply added!', 'success')
    return redirect(url_for('post_show', post_id=post_id))

# Upvote a reply
@app.route('/reply/<int:reply_id>/upvote', methods=['POST'])
@login_required
def upvote_reply(reply_id):
    reply = Reply.query.get_or_404(reply_id)
    if reply.user_id == current_user.id:
        flash('You cannot vote on your own reply.', 'warning')
        return redirect(request.referrer or url_for('post_show', post_id=reply.post_id))
    existing_vote = ReplyVote.query.filter_by(user_id=current_user.id, reply_id=reply_id).first()
    if existing_vote:
        flash('You have already voted on this reply.', 'warning')
        return redirect(request.referrer or url_for('post_show', post_id=reply.post_id))
    vote = ReplyVote(user_id=current_user.id, reply_id=reply_id, vote_type='upvote')
    reply.upvotes = (reply.upvotes or 0) + 1
    db.session.add(vote)
    db.session.commit()
    flash('You upvoted the reply!', 'success')
    return redirect(request.referrer or url_for('post_show', post_id=reply.post_id))

# Downvote a reply
@app.route('/reply/<int:reply_id>/downvote', methods=['POST'])
@login_required
def downvote_reply(reply_id):
    reply = Reply.query.get_or_404(reply_id)
    if reply.user_id == current_user.id:
        flash('You cannot vote on your own reply.', 'warning')
        return redirect(request.referrer or url_for('post_show', post_id=reply.post_id))
    existing_vote = ReplyVote.query.filter_by(user_id=current_user.id, reply_id=reply_id).first()
    if existing_vote:
        flash('You have already voted on this reply.', 'warning')
        return redirect(request.referrer or url_for('post_show', post_id=reply.post_id))
    vote = ReplyVote(user_id=current_user.id, reply_id=reply_id, vote_type='downvote')
    reply.downvotes = (reply.downvotes or 0) + 1
    db.session.add(vote)
    db.session.commit()
    flash('You downvoted the reply!', 'info')
    return redirect(request.referrer or url_for('post_show', post_id=reply.post_id))

@app.route('/post/<int:post_id>/upvote', methods=['POST'])
@login_required
def upvote_post(post_id):
    pst = post.query.get_or_404(post_id)
    if pst.author.id == current_user.id:
        flash('You cannot vote on your own post.', 'warning')
        return redirect(request.referrer or url_for('home'))
    existing_vote = PostVote.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    if existing_vote:
        flash('You have already voted on this post.', 'warning')
        return redirect(request.referrer or url_for('home'))
    vote = PostVote(user_id=current_user.id, post_id=post_id, vote_type='upvote')
    pst.upvotes = (pst.upvotes or 0) + 1
    db.session.add(vote)
    db.session.commit()
    flash('You upvoted the post!', 'success')
    return redirect(request.referrer or url_for('home'))

@app.route('/post/<int:post_id>/downvote', methods=['POST'])
@login_required
def downvote_post(post_id):
    pst = post.query.get_or_404(post_id)
    if pst.author.id == current_user.id:
        flash('You cannot vote on your own post.', 'warning')
        return redirect(request.referrer or url_for('home'))
    existing_vote = PostVote.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    if existing_vote:
        flash('You have already voted on this post.', 'warning')
        return redirect(request.referrer or url_for('home'))
    vote = PostVote(user_id=current_user.id, post_id=post_id, vote_type='downvote')
    pst.downvotes = (pst.downvotes or 0) + 1
    db.session.add(vote)
    db.session.commit()
    flash('You downvoted the post!', 'info')
    return redirect(request.referrer or url_for('home'))

@app.route("/")
@app.route("/home")
def home():
    page=request.args.get('page', 1, type=int)
    posts=post.query.order_by(post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template("home.html",posts=posts)
@app.route("/about")
def about():
    return render_template("about.html",title='About')

@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form=RegistrationForm()
    if form.validate_on_submit():
        hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        usr=user(username=form.username.data,email=form.email.data,password=hashed_password)
        db.session.add(usr)
        db.session.commit()
        flash(f"Account created for {form.username.data}!, you can login",'success')
        return redirect(url_for('login'))
    return render_template('register.html',title='register',form=form)

@app.route('/login', methods=['GET','POST'])
def login():
    form=LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if form.validate_on_submit():
        em=user.query.filter_by(email=form.email.data).first()
        if em and bcrypt.check_password_hash(em.password,form.password.data):
            login_user(em,remember=form.remember.data)
            next_page=request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('home'))
        else:
            flash(f"Incorrect email or password",'danger')
    return render_template('login.html',title='login',form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    random_hex=secrets.token_hex(8)
    _,f_ext=os.path.splitext(form_picture.filename)
    picture_fn=random_hex+f_ext
    picture_path=os.path.join(app.root_path,'static/profile_pics',picture_fn)
    output_size=(125,125)
    i=Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

@app.route('/account',methods=['GET','POST'])
@login_required
def account():
    form=UpdateAccountForm()
    if form.validate_on_submit():
        if form.pic.data:
            picture_f=save_picture(form.pic.data)
            current_user.image=picture_f
        current_user.username=form.username.data
        current_user.email=form.email.data
        db.session.commit()
        flash('Your account has been updated!','success')
        redirect(url_for('account'))
    elif request.method=='GET':
        form.username.data=current_user.username
        form.email.data=current_user.email
    image_file=url_for('static',filename=f'profile_pics/{current_user.image}')
    return render_template('account.html',title='Account',image_file=image_file,form=form)

@app.route('/post/new',methods=['GET','POST'])
@login_required
def new_post():
    form=PostForm()
    if form.validate_on_submit():
        pst=post(title=form.title.data,content=form.content.data,author=current_user)
        db.session.add(pst)
        db.session.commit()
        flash('Post is created','success')
        return redirect(url_for('home'))
    return render_template('create_post.html',title='New Post',form=form,legend='New Post')

@app.route('/post/<int:post_id>')
def post_show(post_id):
    pst=post.query.get_or_404(post_id)
    return render_template('post.html',title=pst.title,post=pst)

@app.route('/post/<int:post_id>/update',methods=['GET','POST'])
@login_required
def update_post(post_id):
    pst=post.query.get_or_404(post_id)
    if pst.author!=current_user:
        abort(403)
    form=PostForm()
    if form.validate_on_submit():
        pst.title=form.title.data
        pst.content=form.content.data 
        db.session.commit()
        flash("Your post has been updated",'success')
        return redirect(url_for('post_show',post_id=pst.id))
    elif request.method=='GET':
        form.title.data=pst.title
        form.content.data=pst.content
    return render_template('create_post.html',title='Update Post',form=form,legend='Update Post')

@app.route('/post/<int:post_id>/delete',methods=['POST'])
@login_required
def delete_post(post_id):
    pst=post.query.get_or_404(post_id)
    if pst.author!=current_user:
        abort(403)
    db.session.delete(pst)
    db.session.commit()
    flash("Your post has been deleted!",'success')
    return redirect(url_for('home'))

@app.route('/user/<string:username>')
def user_posts(username):
    page=request.args.get('page',1,type=int)
    usr=user.query.filter_by(username=username).first_or_404()
    pst=post.query.filter_by(author=usr).order_by(post.date_posted.desc()).paginate(page=page,per_page=5)
    return render_template('user_posts.html',posts=pst,user=usr,title=username)

def send_reset_email(usr):
    token=usr.get_reset_token()
    msg=Message('Password Reset Request',sender='noreply@flaskblog.com',
                recipients=[usr.email])
    msg.body=f'''To reset your password, visit the following link:
{url_for('reset_token',token=token,_external=True)}

If you did not make this request then ignore this email and no changes will be processed
'''
    mail.send(msg)

@app.route('/reset_password',methods=['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form=RequestResetForm()
    if form.validate_on_submit():
        usr=user.query.filter_by(email=form.email.data).first()
        if usr:
            send_reset_email(usr)
            flash('An email with instructions has been sent to reset your password.','info')
            return redirect(url_for('login'))
    return render_template('reset_request.html',title='Reset Password',form=form)

@app.route('/reset_password/<token>',methods=['GET','POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    usr=user.verify_reset_token(token=token)
    if usr is None:
        flash('Invalid or expired token','warning')
        return redirect(url_for('reset_request'))
    form=ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        usr.password=hashed_password
        db.session.commit()
        flash(f"Your password has been updated, you can login",'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html',title='Reset Password',form=form)
