from flask import Flask, render_template, redirect, url_for, request, flash
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields.simple import PasswordField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from datetime import date
from credentials import MY_EMAIL, MY_PASSWORD, SECRET_KEY
import requests
import bleach

MY_EMAIL = MY_EMAIL
MY_PASSWORD = MY_PASSWORD
SECRET_KEY = SECRET_KEY

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
Bootstrap5(app)
ckeditor = CKEditor(app)

# Initialize Login Manager
login_manager = LoginManager()
login_manager.init_app(app)


# CREATE DATABASE
class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)


class BlogPost(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=True)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=True)


class CommentSection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('blog_post.id'), nullable=False)
    author = db.Column(db.String(250), nullable=True)
    body = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(250), nullable=False)


class CommentForm(FlaskForm):
    author = StringField("Your Name")
    body = StringField("Comment", validators=[DataRequired()])
    submit = SubmitField("Add Comment")



class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle")
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL")
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


# User Loader


# Login Form
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


with app.app_context():
    db.create_all()
    if not User.query.filter_by(email=MY_EMAIL).first():
        new_user = User(id=1, email=MY_EMAIL, password=MY_PASSWORD)
        db.session.add(new_user)
        db.session.commit()


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == MY_EMAIL and form.password.data == MY_PASSWORD:
            user = User.query.filter_by(email=MY_EMAIL).first()
            if not user:
                user = User(id=1, email=MY_EMAIL, password=MY_PASSWORD)
                db.session.add(user)
                db.session.commit()
            login_user(user)
            return redirect(url_for('get_all_posts'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', form=form)


@login_manager.user_loader
def load_user(user_id):
    if user_id and user_id.isdigit():
        return User.query.get(int(user_id))
    return None


@app.route("/new-post", methods=["GET", "POST"])
@login_required
def add_new_post():
    form = CreatePostForm(author="Kyle Porter")
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            date=date.today().strftime("%B %d, %Y"),
            body=form.body.data,
            author=form.author.data,
            img_url=form.img_url.data
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route('/index.html')
@app.route('/')
@app.route('/post/index.html')
def get_all_posts():
    # Query the database for all the posts. Convert the data to a python list.
    page = request.args.get('page', 1, type=int)
    posts = BlogPost.query.order_by(BlogPost.id.desc()).paginate(page=page, per_page=4)
    return render_template('index.html', all_posts=posts.items, pagination=posts)


@app.route('/about.html')
@app.route('/post/about.html')
def about():
    return render_template("about.html")


@app.route('/edit-post/<post_id>', methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = edit_form.author.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True)


@app.route('/contact.html')
@app.route('/post/contact.html')
def contact():
    return render_template("contact.html")


@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    form = CommentForm()
    if form.validate_on_submit():
        new_comment = CommentSection(
            post_id=post_id,
            author=form.author.data if form.author.data else 'Anonymous',
            body=form.body.data,
            date=date.today().strftime("%B %d, %Y")

        )
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for('show_post', post_id=post_id))
    comments = CommentSection.query.filter_by(post_id=post_id).order_by(CommentSection.date.desc()).all()

    # Retrieve a BlogPost from the database based on the post_id
    return render_template("post.html", post=post, form=form, comments=comments)


@app.route("/delete/<post_id>")
@login_required
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))

@app.route("/delete-comment/<comment_id>", methods=["POST"])
@login_required
def delete_comment(comment_id):
    comment= db.get_or_404(CommentSection, comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash("Comment deleted successfully", "success")
    return redirect(url_for('show_post', post_id=comment.post_id))

@app.route("/form-entry", methods= ["POST"])
def receive_data():
    data= request.form
    print(data.get("name", "Name not provided"))
    print(data.get("email", "Email not provided"))
    print(data.get("phone", "Phone not provided"))
    print(data.get("message", "Message not provided"))
    return "<h1>Successfully sent your message</h1>"





if __name__ == "__main__":
    app.run(debug=False)
