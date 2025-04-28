import base64
import os
from flask import Flask, abort, jsonify, make_response, redirect, render_template, send_from_directory
from flask_login import LoginManager, current_user, login_user, login_required, logout_user
from werkzeug.utils import secure_filename
from flask_wtf.csrf import CSRFProtect

from models import db_session
from models.users import User
from models.posts import Post, Comment

from forms.login_form import LoginForm
from forms.register_form import RegisterForm
from forms.add_post_form import PostForm
from forms.comment_form import CommentForm


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
csrf = CSRFProtect(app)

UPLOAD_FOLDER = 'static/uploaded'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

login_manager = LoginManager()
login_manager.init_app(app)

with open('static/img/user_icon.png', 'rb') as f:
    default_user_icon = base64.b64encode(f.read()).decode('utf-8')


@app.template_filter('b64encode')
def b64encode_filter(data):
    if data is None:
        return ''
    return base64.b64encode(data).decode('utf-8')


@app.errorhandler(404)
def not_found(_):
    return make_response(jsonify({'error': 'Not found'}), 404)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
@app.route("/index")
def index():
    db_sess = db_session.create_session()
    posts = db_sess.query(Post).all()
    users = {}
    for user in db_sess.query(User).all():
        if user.avatar:
            avatar_base64 = base64.b64encode(user.avatar).decode('utf-8')
        else:
            avatar_base64 = default_user_icon
        users[user.id] = {
            'id': user.id,
            'name': user.name,
            'avatar_base64': avatar_base64
        }

    form = CommentForm()

    return render_template('index.html', title='Добро пожаловать!', posts=posts, users=users, form=form)


@app.route('/add_comment/<int:post_id>', methods=['POST'])
@login_required
def add_comment(post_id):
    form = CommentForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        post = db_sess.query(Post).filter(Post.id == post_id).first()
        if not post:
            return abort(404)

        comment = Comment(
            text=form.text.data,
            author_id=current_user.id,
            post_id=post_id
        )
        db_sess.add(comment)
        db_sess.commit()
        return redirect('/')
    return abort(400)


@app.route("/favicon.ico")
def favicon():
    return send_from_directory('static/img', 'icon.jpg')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/')
        return render_template('login.html', message="Неверный логин или пароль", form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже существует")
        user = User(
            name=form.name.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        login_user(user, remember=True)
        return redirect('/')
    return render_template('register.html', title='Регистрация', form=form)

@app.route('/profile/<int:user_id>')
def profile(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    if user:
        user_avatar_base64 = default_user_icon
        if user.avatar:
            user_avatar_base64 = base64.b64encode(user.avatar).decode('utf-8')
        return render_template('profile.html', title='Профиль ' + user.name, user=user, user_avatar_base64=user_avatar_base64)
    return abort(404)


@app.route('/add_post', methods=['GET', 'POST'])
@login_required
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        post = Post()
        post.text = form.text.data
        post.author_id = current_user.id  # <--- Важно

        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            form.image.data.save(filepath)
            post.image_path = '/' + filepath.replace('\\', '/')

        db_sess.add(post)
        db_sess.commit()
        return redirect('/')
    return render_template('add_post.html', title='Создать пост', form=form)


def main():
    db_session.global_init("db/database.db")
    app.run(port=5734, host='127.0.0.1', debug=True)


if __name__ == '__main__':
    main()
    