from flask import Flask, request
from templates.posts_blueprint import posts_blueprint
from flask_cors import CORS
import logging 

app = Flask(__name__)
CORS(app)
app.register_blueprint(posts_blueprint, url_prefix='/posts')

if __name__ == '__main__':
    app.run(debug=True) 