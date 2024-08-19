from flask import Flask, Blueprint, request, jsonify
from flask_mail import Mail, Message
from config import mail

app = Flask(__name__)

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = ''
app.config['MAIL_PASSWORD'] = ''
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

contact_bp = Blueprint('contact', __name__)

@contact_bp.route('/api/contact', methods=['POST'])
def contact():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    message_body = data.get('message')

    msg = Message(subject=f"New Message from {name}",
                  sender=app.config['MAIL_DEFAULT_SENDER'],
                  recipients=["recipient-email@example.com"])  # Update recipient email
    msg.body = f"Name: {name}\nEmail: {email}\nPhone: {phone}\nMessage: {message_body}"

    try:
        mail.send(msg)
        return jsonify({'status': 'Message sent successfully!'}), 200
    except Exception as e:
        return jsonify({'status': 'Failed to send message!'}), 500

