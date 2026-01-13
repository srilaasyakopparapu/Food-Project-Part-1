from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
DATABASE = 'food.db'



def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS food (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                food_name TEXT,
                ingredients TEXT,
                expiry_date TEXT,
                packed_status TEXT,
                allergy_info TEXT,
                is_free INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                email TEXT
            )
        ''')


@app.route('/', methods=["GET", "POST"])
def login():
    if request.method=="POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if username=="admin" and password=="123456":
            return redirect(url_for("index"))
        else:
            flash("Invalid Username/Password!")
            return redirect(url_for("login"))
    return render_template('login.html')

@app.route('/index')
def index():
    with sqlite3.connect(DATABASE) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM food ORDER BY timestamp DESC")
        items = cur.fetchall()
        today = datetime.now().replace(hour = 0, minute = 0, second = 0, microsecond= 0)
        valid_items = []

    for item in items:
        expiry_dt = datetime.strptime(item[3], "%Y-%m-%d")

        if expiry_dt > today: #if expiry date is greater than today 
            valid_items.append(item) #only add valid items into the append items (only store those records)
 
    return render_template("index.html",items=valid_items) 
        
@app.route('/submit', methods=['GET', 'POST'])
def submit():
    min_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    print(min_date)
    if request.method == 'POST':
        expiry_date = request.form['expiry_date']
        today = datetime.today().date()
        expiry = datetime.strptime(expiry_date, '%Y-%m-%d').date()
        if expiry <= today:
            flash("Expiry Date must be a future date")
            return redirect(url_for("submit"))
        
        data = {
            'food_name': request.form['food_name'],
            'ingredients': request.form['ingredients'],
            'expiry_date': request.form['expiry_date'],
            'packed_status': request.form['packed_status'],
            'allergy_info': request.form['allergy_info'],
            'is_free': 1 if request.form.get('is_free') == 'on' else 0,
            'email': request.form['email']
            }
        with sqlite3.connect(DATABASE) as conn:
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO food (food_name, ingredients, expiry_date, packed_status,
                                allergy_info, is_free, email)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', tuple(data.values()))
            print("Record Added", request.form['food_name'] )
        return redirect('/')
    return render_template('submit.html', min_date = min_date)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
