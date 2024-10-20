from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from routes import auth
from config import Config

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///biblioshare.db'
db = SQLAlchemy(app)
app.config.from_object(Config)

app.register_blueprint(auth)
@app.route('/')
def index():
  return ""

if __name__ == '__main__':
	app.run(debug=True)
