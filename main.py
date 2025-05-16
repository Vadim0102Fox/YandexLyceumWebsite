import os
from flask import Flask, abort, jsonify, make_response, redirect, render_template, send_from_directory, request
from flask_login import LoginManager, current_user, login_user, login_required, logout_user
from werkzeug.utils import secure_filename
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import func

from models import db_session
from models.users import User
from models.posts import Post
from models.comments import Comment

from forms.login_form import LoginForm
from forms.register_form import RegisterForm
from forms.add_post_form import PostForm
from forms.comment_form import CommentForm
from forms.confirm_action_form import ConfirmForm
from forms.edit_profile_form import EditUserForm


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
csrf = CSRFProtect(app)

UPLOAD_FOLDER = 'static/uploaded'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('db', exist_ok=True)

login_manager = LoginManager()
login_manager.init_app(app)


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
    search = request.args.get('search', None)
    if search:
        title = f'Поиск по "{search}"'
        posts = db_sess.query(Post).filter(func.lower(Post.text).like(f"%{search.lower()}%")).all()[::-1]
    else:
        title = "Добро пожаловать!"
        posts = db_sess.query(Post).all()[::-1]
    users = {}
    for user in db_sess.query(User).all():
        users[user.id] = {
            'id': user.id,
            'name': user.name,
            'avatar_path': user.avatar_path
        }

    form = CommentForm()

    return render_template('index.html', title=title, posts=posts, users=users, form=form)


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


@app.route('/delete_comment/<int:comment_id>', methods=['GET', 'POST'])
@login_required
def delete_comment(comment_id):
    form = ConfirmForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        comment = db_sess.query(Comment).filter(Comment.id == comment_id).first()
        db_sess.delete(comment)
        db_sess.commit()
        return redirect('/')
    return render_template('confirm_action.html', title="Подтверждение удаления комментария", type="danger", form=form)


@app.route('/edit_comment/<int:comment_id>', methods=['GET', 'POST'])
@login_required
def edit_comment(comment_id):
    db_sess = db_session.create_session()
    comment = db_sess.query(Comment).filter(Comment.id == comment_id).first()
    form = CommentForm(data={'text': comment.text})
    if form.validate_on_submit():
        comment.text = form.text.data
        
        db_sess.commit()
        return redirect('/')
    return render_template('edit_comment.html', form=form)


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


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    form = ConfirmForm()
    if form.validate_on_submit():
        logout_user()
        return redirect("/")
    return render_template('confirm_action.html', title="Подтверждение выхода из аккаунта", type="warning", form=form)


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
        return render_template('profile.html', title='Профиль ' + user.name, user=user)
    return abort(404)


@app.route('/edit_profile/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_profile(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    form = EditUserForm(data={"name": user.name, "description": str(user.description), 
                              "email": user.email, "role": user.role})
    if form.validate_on_submit():
        if form.name.data:
            user.name = form.name.data
        if form.description.data:
            user.description = form.description.data
        if form.avatar.data:
            filename = secure_filename(form.avatar.data.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            form.avatar.data.save(filepath)
            user.avatar_path = '/' + filepath.replace('\\', '/')
        if form.email.data:
            user.email = form.email.data
        if form.password.data:
            user.password = form.password.data
        if form.role.data:
            user.role = form.role.data

        db_sess.commit()
        return redirect('/')
    return render_template('edit_profile.html', title="Редактирование профиля", form=form)
    

@app.route('/add_post', methods=['GET', 'POST'])
@login_required
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        post = Post()
        post.text = form.text.data
        post.author_id = current_user.id

        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            form.image.data.save(filepath)
            post.image_path = '/' + filepath.replace('\\', '/')

        db_sess.add(post)
        db_sess.commit()
        return redirect('/')
    return render_template('add_post.html', title='Создать пост', form=form)


@app.route('/delete_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def delete_post(post_id):
    form = ConfirmForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        post = db_sess.query(Post).filter(Post.id == post_id).first()
        db_sess.delete(post)
        db_sess.commit()
        return redirect('/')
    return render_template('confirm_action.html', title="Подтверждение удаления поста", type="danger", form=form)


@app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    db_sess = db_session.create_session()
    post = db_sess.query(Post).filter(Post.id == post_id).first()
    form = PostForm(data={"text": post.text})
    if form.validate_on_submit():
        post.text = form.text.data
        # post.author_id = current_user.id

        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            form.image.data.save(filepath)
            post.image_path = '/' + filepath.replace('\\', '/')

        db_sess.commit()
        return redirect('/')
    return render_template('edit_post.html', title='Редактирование поста', form=form)


def main():
    db_session.global_init("db/database.db")
    app.run(port=5734, host='127.0.0.1', debug=True)


if __name__ == '__main__':
    main()
    