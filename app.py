import os
import pika
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configure the app with environment variables
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{os.getenv('MYSQL_USER', 'default_user')}:{os.getenv('MYSQL_PASSWORD', 'default_password')}@"
    f"{os.getenv('MYSQL_HOST', 'localhost')}/{os.getenv('MYSQL_DB', 'default_db')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)

def init_db():
    with app.app_context():
        db.create_all()

def send_message_to_rabbitmq(message):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=os.getenv('RABBITMQ_HOST', 'localhost')))
        channel = connection.channel()

        # Declare a queue
        channel.queue_declare(queue='flask_messages')

        # Publish the message
        channel.basic_publish(exchange='',
                              routing_key='flask_messages',
                              body=message)
    except Exception as e:
        app.logger.error(f"Error sending message to RabbitMQ: {e}")
    finally:
        connection.close()

@app.route('/')
def index():
    try:
        messages = Message.query.all()
    except Exception as e:
        app.logger.error(f"Error fetching messages: {e}")
        return render_template('error.html', error="Error fetching messages.")
    return render_template('index.html', messages=messages)

@app.route('/submit', methods=['POST'])
def submit():
    new_message = request.form.get('new_message')

    if not new_message:
        return jsonify({'error': 'Message cannot be empty'}), 400

    try:
        message = Message(message=new_message)
        db.session.add(message)
        db.session.commit()

        # Fetch all messages from the database
        messages = Message.query.all()
        message_list = [msg.message for msg in messages]

        # Send message to RabbitMQ
        send_message_to_rabbitmq(new_message)
    except Exception as e:
        app.logger.error(f"Error submitting message: {e}")
        return jsonify({'error': 'Internal server error'}), 500

    return jsonify({'message': new_message, 'messages': message_list})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
