import base64
from flask import Flask, abort, jsonify, make_response, redirect, render_template, send_from_directory
from flask_login import LoginManager, login_user, login_required, logout_user

from models import db_session
from models.users import User

from forms.login_form import LoginForm
from forms.register_form import RegisterForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)

with open('static/img/user_icon.png', 'rb') as f:
    default_user_icon = base64.b64encode(f.read()).decode('utf-8')


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
    return render_template('index.html', title='Добро пожаловать!')


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


def main():
    db_session.global_init("db/database.db")
    app.run(port=5734, host='127.0.0.1', debug=True)


if __name__ == '__main__':
    main()
    