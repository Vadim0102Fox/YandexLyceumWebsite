from flask import Flask, render_template, send_from_directory

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'



@app.route("/")
@app.route("/index")
def index():
    return render_template('index.html', title='Добро пожаловать!')

@app.route("/favicon.ico")
def favicon():
    return send_from_directory('static/img', 'icon.jpg')


def main():
    app.run(port=5734, host='127.0.0.1', debug=True)


if __name__ == '__main__':
    main()
    