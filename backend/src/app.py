from flask import Flask
from models import db
from routes import auth
from config import Config
from models import User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///biblioshare.db'
app.config.from_object(Config)

db.init_app(app)

app.register_blueprint(auth)

@app.route('/')
def index():
  return ""

with app.app_context():
    db.create_all()

if __name__ == '__main__':
	app.run(debug=True)
