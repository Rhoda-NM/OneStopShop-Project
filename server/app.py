from flask import Flask
from config import app, db, api
from flask_migrate import Migrate  #  imported Migrate

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False


# Initialize database and migration
db.init_app(app)
migrate = Migrate(app, db)
# Initialize Flask-Restful Api
api.init_app(app)

@app.route('/')
def index():
    return '<h1>Project Server</h1>'

if __name__ == '__main__':
    app.run(port=5555, debug=True)

