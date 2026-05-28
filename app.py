from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///okroshka.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'super_secret_key_123'

db = SQLAlchemy(app)

with app.app_context():
    db.create_all()

    try:
        from sqlalchemy import text

        db.session.execute(text("ALTER TABLE past ADD COLUMN date DATETIME"))
        db.session.commit()
        print("Столбец date добавлен в таблицу")
    except:
        print("Столбец date уже есть, всё нормально")

class Past(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.now)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<User {self.email}>'

with app.app_context():
    db.create_all()

@app.route('/index')
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/posts')
def posts():
    posts = Past.query.all()
    return render_template('posts.html', posts=posts)

@app.route('/create', methods=['POST', 'GET'])
def create():
    if request.method == 'POST':
        title = request.form['title']
        text = request.form['text']
        post = Past(title=title, text=text)
        try:
            db.session.add(post)
            db.session.commit()
            return redirect('/index')
        except Exception as e:
            return str(e)
    else:
        return render_template('create.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user:
            return "Ошибка! Такой email уже существует."

        new_user = User(username=username, email=email, password=password)

        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect('/login')
        except Exception as e:
            return str(e)
    else:
        return render_template('register.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and user.password == password:
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect('/index')
        else:
            return "Неправильный email или пароль!"

    else:
        return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect('/login')


@app.route('/posts/<int:id>')
def post_detail(id):
    post = Past.query.get(id)
    if post is None:
        return "Пост не найден", 404
    return render_template('post_detail.html', post=post)


if __name__ == '__main__':
    app.run(debug=True)