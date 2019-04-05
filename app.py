from flask import Flask, request
from templates.posts_blueprint import posts_blueprint
from flask_cors import CORS
import logging 


def setup_logger():
    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
    s_handler = logging.StreamHandler()
    s_handler.setFormatter(formatter)
    f_handler = logging.FileHandler('./config/file.log')   
    f_handler.setFormatter(formatter)
    logger = logging.getLogger('root')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(f_handler)
    logger.addHandler(s_handler)
    return logger

logger = setup_logger()
app = Flask(__name__)

logger.info('API has started...')

CORS(app)
app.register_blueprint(posts_blueprint, url_prefix='/posts')

if __name__ == '__main__':
    app.run(debug=True) 