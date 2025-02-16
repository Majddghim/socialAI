from flask import Flask, render_template, redirect, request, jsonify, url_for, flash, session
from app.artif.localLlama import generate_post_description
from app.artif.assembly import AssemblyAI
from app.artif.videoApi import generate_video
from app.artif.posting import post_to_instagram, post_to_facebook, post_to_x
import pymysql
import bcrypt
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from app.artif.googleAPI import get_google_image
from app.artif.llama import extract
from app.artif.stabledefusion import generate_image
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import random
from apscheduler.schedulers.background import BackgroundScheduler


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



def post_content():
    con, cursor = get_connection()
    user_id = 1


    cursor.execute("SELECT link, image FROM posts WHERE user_id = %s ORDER BY timestamp ASC LIMIT 1", (user_id,))
    post = cursor.fetchone()

    if post:
        description = post[0]
        image_url = post[1]


        post_to_instagram(description, image_url)
        post_to_facebook(description, image_url)
        post_to_x(description, image_url)


        cursor.execute("DELETE FROM posts WHERE link = %s AND image = %s", (description, image_url))
        con.commit()

    con.close()


def start_scheduler():
    scheduler = BackgroundScheduler()

    scheduler.add_job(features_request, 'interval', hours=24)
    scheduler.add_job(generate_video_post, 'interval', hours=24)

    scheduler.add_job(post_content, 'interval', hours=24)

    scheduler.start()

@app.route('/')
def home_template():
    if 'user_id' not in session:
        return redirect(url_for('login_template'))
    return redirect('/features')


@app.route('/login', methods=['GET', 'POST'])
def login_template():
    if request.method == 'POST':

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


            stored_password = user[2]
            if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):

                session['user_id'] = user[0]
                flash("Login successful!", "success")
                return redirect(url_for('features_template'))
            else:
                flash("Invalid password", "danger")
                return render_template('login.html')

        except Exception as e:
            flash(f"An error occurred: {str(e)}", "danger")
            return render_template('login.html')

    return render_template('login.html')


@app.route('/register', methods=['GET'])
def register_templates():
    return render_template('signup.html')


@app.route('/register-request', methods=['POST'])
def register_request():
    try:
        data = request.form
        email = data.get('email')
        password = data.get('password')
        descr = data.get('descr')

        if not email or not password or not descr:
            return jsonify({"error": "Missing fields"}), 400


        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        con, cursor = get_connection()
        cursor.execute("INSERT INTO users (email, password, description) VALUES (%s, %s, %s)", (email, hashed_password, descr))
        con.commit()
        con.close()


        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login_template'))

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/features', methods=['GET'])
def features_template():
    if 'user_id' not in session:
        flash("You need to log in first!", "danger")
        return redirect(url_for('login_template'))  # Redirect to login page if not logged in

    user_id = session['user_id']

    con, cursor = get_connection()
    cursor.execute("SELECT link, image FROM posts WHERE user_id = %s", (user_id,))
    posts_data = cursor.fetchall()
    con.close()

    return render_template('features.html', posts=posts_data)

@app.route('/features_request', methods=['POST'])
def features_request():
    if 'user_id' not in session:
        flash("You need to log in first!", "danger")
        return redirect(url_for('login_template'))

    con, cursor = get_connection()
    user_id = session['user_id']


    cursor.execute("SELECT description FROM users WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()

    if not user_data or not user_data[0]:
        return jsonify({"error": "User description not found"}), 400

    user_description = user_data[0]


    description = generate_post_description(user_description, "http://127.0.0.1:11434/api/generate")
    print("description")
    if not description:
        return jsonify({"error": "Failed to generate description"}), 500


    image_url = get_google_image(description)
    print("image")
    if not image_url:
        print("no image")
        return jsonify({"error": "Failed to generate image"}), 500
    print("image2")

    cursor.execute("INSERT INTO posts (user_id, link, image) VALUES (%s, %s, %s)", (user_id, description, image_url))
    con.commit()
    con.close()
    print("saved")
    return jsonify({"message": "Post added successfully"})

@app.route('/generate_video_post', methods=['POST'])
def generate_video_post():
    con, cursor = get_connection()
    user_id = session['user_id']


    cursor.execute("SELECT description FROM users WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()

    if not user_data or not user_data[0]:
        return jsonify({"error": "User description not found"}), 400

    user_description = user_data[0]


    description = generate_post_description(user_description, "http://127.0.0.1:11434/api/generate")
    print("description")
    if not description:
        return jsonify({"error": "Failed to generate description"}), 500


    video_url = generate_video(description)
    if not video_url:
        print("no image")
        return jsonify({"error": "Failed to generate image"}), 500
    print("image2")

    cursor.execute("INSERT INTO posts (user_id, link, image) VALUES (%s, %s, %s)", (user_id, description, video_url))
    con.commit()
    con.close()
    print("saved")
    return jsonify({"message": "Post added successfully"})

@app.route('/contacts', methods=['GET'])
def contacts_template():
    if 'user_id' not in session:
        flash("You need to log in first!", "danger")
        return redirect(url_for('login_template'))
    return render_template('contacts.html')


@app.route('/contacts_request', methods=['POST'])
def contacts_request():
    if 'user_id' not in session:
        flash("You need to log in first!", "danger")
        return redirect(url_for('login_template'))

    try:
        user_id = session['user_id']
        data = request.form
        link = data.get('link')
        nbr = int(data.get('nbr'))
        print(link)
        print(nbr)
        a = AssemblyAI()
        if not link or not nbr:
            return jsonify({"error": "Missing fields"}), 400


        audio = a.download_youtube_audio(link, output_path="audio.mp3")
        print("audio")


        transcriptions = a.transcribe(audio)
        print(transcriptions)

        descriptions = extract(transcriptions, nbr)
        print("descriptions done")


        con, cursor = get_connection()
        for description in descriptions:

            image = get_google_image(f"generate a suitable image for {description}")
            print(image)


            cursor.execute("INSERT INTO posts (user_id, link, image) VALUES (%s, %s, %s)", (user_id, description, image))
            print("saved")

        con.commit()
        con.close()

        flash("Message sent successfully!", "success")
        return redirect(url_for('contacts_template'))

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/post_to_social_media', methods=['POST'])
def post_to_social_media():
    data = request.json
    description = data.get('description')
    image_url = data.get('image')
    platform = data.get('platform')

    if not description or not image_url or not platform:
        return jsonify({"message": "Invalid data"}), 400

    try:
        if platform == "instagram":
            response_message = post_to_instagram(description, image_url)
        elif platform == "facebook":
            response_message = post_to_facebook(description, image_url)
        elif platform == "x":
            response_message = post_to_x(description, image_url)
        elif platform == "all":
            post_to_instagram(description, image_url)
            post_to_facebook(description, image_url)
            post_to_x(description, image_url)
            response_message = "Posted to all platforms successfully"


        connection = get_connection()  # Ensure you have a function that connects to your DB
        cursor = connection.cursor()
        cursor.execute("DELETE FROM posts WHERE description = %s AND image_url = %s", (description, image_url))
        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({"message": f"{response_message}. Post deleted from database."})

    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500


@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove user_id from session
    flash("Logged out successfully!", "success")
    return redirect(url_for('login_template'))  # Redirect to login page


if __name__ == '__main__':
    app.run()
