from flask import Flask, render_template, url_for, request, redirect, flash, session
import sqlite3

app = Flask(__name__, static_folder='static')
app.secret_key = 'your_secret_key'  # Change this to a random secret key
#session["authenticated"] = False

# Create a SQLite database and a table for users
conn = sqlite3.connect('users.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL
    )
''')
conn.commit()
conn.close()

@app.route("/")
def index():
    return render_template("welcome.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username exists in the database
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()

        if user and user[2] == password:  # Assuming the password is stored in the third column
            # Store user information in the session
            session['username'] = username
            session["authenticated"] = True
            # Redirect to the bookin.html template
            return redirect("/booking")
        else:
            flash('Incorrect username or password', 'error')
            return render_template('index.html', error_message=request.args.get('error'))
    else:
        return render_template('index.html')
    
@app.route('/booking')
def booking():
    if session["authenticated"]:
        return render_template('bookin.html')
    else:
        return redirect("/login")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html', error_message=request.args.get('error'))

        # Save the user in the database (plaintext password)
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        conn.close()

        flash('Registration successful. You can now log in.', 'success')
        return redirect(url_for('index'))
    else:
        return render_template('register.html')

@app.route('/successful_booking', methods=['GET', 'POST'])
def successful_booking():
    # Check if the user is logged in
    if 'username' in session:
        return render_template('successful_booking.html')
    else:
        # If not logged in, redirect to the login page
        flash('Please log in to make a booking.', 'error')
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    # Clear the session data
    session["authenticated"] = False
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
