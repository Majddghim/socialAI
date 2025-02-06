from flask import Flask, render_template, redirect, request, jsonify, url_for, flash
from app.artif.assembly import AssemblyAI
import pymysql
import bcrypt
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

from app.artif.llama import extract
from app.artif.stabledefusion import generate_image

app = Flask(__name__)

app.secret_key = "secret-key"

def get_connection():
    con = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="social"
    )
    return con, con.cursor()


@app.route('/')
def home_template():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login_template():
    if request.method == 'POST':
        print("form submitted")
        # Get form data
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash("Email and password are required!", "danger")
            return render_template('login.html')

        try:
            con, cursor = get_connection()
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            con.close()

            if not user:
                flash("User not found", "danger")
                return render_template('login.html')

            # Check if the password is correct
            stored_password = user[2]  # Assuming password is the 3rd column in the table
            if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                flash("Login successful!", "success")
                return redirect(url_for('features_template'))  # Replace with your actual dashboard page
            else:
                flash("Invalid password", "danger")
                return render_template('login.html')

        except Exception as e:
            flash(f"An error occurred: {str(e)}", "danger")
            return render_template('login.html')

    # For GET request, just render the login page
    return render_template('login.html')


@app.route('/register', methods=['GET'])
def register_templates():
    return render_template('signup.html')

@app.route('/register-request', methods=['POST'])
def register_request():
    try:
        data = request.form  # Get form data
        email = data.get('email')
        password = data.get('password')
        descr = data.get('descr')

        if not email or not password or not descr:
            return jsonify({"error": "Missing fields"}), 400

        # Hash the password before saving it
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        con, cursor = get_connection()
        cursor.execute("INSERT INTO users (email, password, description) VALUES (%s, %s, %s)", (email, hashed_password, descr))
        con.commit()
        con.close()

        # ✅ After successful registration, redirect to login page
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login_template'))  # Make sure 'login_page' exists

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/features', methods=['GET'])
def features_template():
    con, cursor = get_connection()
    # Correcting how we execute and fetch the query result
    cursor.execute("SELECT link, image FROM posts")  # Execute the query
    posts_data = cursor.fetchall()  # Fetch all rows
    return render_template('features.html', posts=posts_data)

@app.route('/contacts', methods=['GET'])
def contacts_template():
    return render_template('contacts.html')
@app.route('/contacts_request', methods=['POST'])
def contacts_request():
    try:
        data = request.form  # Get form data
        link = data.get('link')  # This seems to be used as a link, maybe update the name?
        nbr = int(data.get('nbr'))  # Assuming 'nbr' is a number (e.g., for selecting description number)
        print(link)
        print(nbr)
        a = AssemblyAI()
        if not link or not nbr:
            return jsonify({"error": "Missing fields"}), 400

        # Download the audio from the YouTube link
        audio = a.download_youtube_audio(link, output_path="audio.mp3")
        print("audio")

        # Transcribe the downloaded audio
        transcriptions = a.transcribe(audio)
        print(transcriptions)
        # Extract the description(s) using Llama's extract function
        descriptions = extract(transcriptions, nbr)
        print("descriptions done")

        # Process each description
        for description in descriptions:
            # Generate an image based on the description
            image = generate_image(f"generate a suitable image for {description}")
            print("image")

            # Insert each description with its generated image into the database
            con, cursor = get_connection()
            cursor.execute("INSERT INTO posts (link,  image) VALUES ( %s, %s)",
                           (description,  image))
            print("saved")
            con.commit()
            con.close()

        flash("Message sent successfully!", "success")
        return redirect(url_for('contacts_template'))

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run()
