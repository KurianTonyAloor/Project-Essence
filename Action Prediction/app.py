from flask import Flask, render_template, request, redirect, url_for, jsonify
from user_details import UserDetails, get_next_user_id
import os

app = Flask(__name__)

# Global variable to store the user session (can be improved with session management)
user_data = None

# Welcome page: New or Existing User
@app.route('/')
def index():
    return render_template('welcome.html')

# Route to handle new user creation page
@app.route('/new_user')
def new_user():
    return render_template('new_user.html')

# Route to handle creating a new user and advancing to the main app
@app.route('/create_new_user', methods=['POST'])
def create_new_user():
    global user_data
    user_id = get_next_user_id()
    user_data = UserDetails(user_id)
    return redirect(url_for('main_app', user_id=user_id))

# Route to handle existing user page
@app.route('/existing_user')
def existing_user():
    return render_template('existing_user.html')

# Route to load existing user and advance to the main app
@app.route('/load_existing_user', methods=['POST'])
def load_existing_user():
    global user_data
    user_id = int(request.form['user_id'])
    if os.path.exists(f"user{user_id}.txt"):
        user_data = UserDetails(user_id)
        return redirect(url_for('main_app', user_id=user_id))
    else:
        return render_template('existing_user.html', error="User ID not found.")

# Main app interface after user selection (new or existing)
@app.route('/main_app/<int:user_id>')
def main_app(user_id):
    return render_template('main_app.html', user_id=user_id)

# Adding new detail route
@app.route('/add_detail', methods=['POST'])
def add_detail():
    global user_data
    if not user_data:
        return jsonify({"error": "No user loaded."}), 400

    detail = request.json['detail']
    topics = request.json['topics']
    time = request.json['time']

    user_data.add_detail(detail, topics, time)
    return jsonify({"message": "Detail added successfully."})

# Route to generate insights
@app.route('/generate_insights', methods=['GET'])
def generate_insights():
    global user_data
    if not user_data:
        return jsonify({"error": "No user loaded."}), 400

    insights = user_data.generate_insights()
    return jsonify(insights)

# Route to predict next action at a specific time
@app.route('/predict_next_action_at_time', methods=['POST'])
def predict_next_action_at_time():
    global user_data
    if not user_data:
        return jsonify({"error": "No user loaded."}), 400

    input_time = request.json['time']
    prediction = user_data.predict_next_action_at_time(input_time)
    return jsonify({"prediction": prediction})

if __name__ == '__main__':
    app.run(debug=True)


