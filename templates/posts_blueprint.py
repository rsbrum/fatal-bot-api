from flask import Blueprint, Response, request
from jinja2 import TemplateNotFound
from flask_cors import CORS, cross_origin
import db as database
import json, logging

logger = logging.getLogger('root')
db = None
posts_blueprint = Blueprint('posts_blueprint', __name__)
CORS(posts_blueprint, resources={r"/api/*": {"origins": "*"}})

def before():
    """
        Creates database connection
    """
    CORS(posts_blueprint)
    global db
    db = database.get_db()

def after(f):
    """
        Closes database connection
    """
    global db
    database.close_db()
    return f

posts_blueprint.before_request(before)
posts_blueprint.after_request(after)

@posts_blueprint.route('/', methods=['GET'])
def get_posts():
    """
        Returns list of posts that have likes pending
    """
    logger.info('Getting list of posts that have likes pending...')
    sql = ''' SELECT * FROM posts WHERE n_likes > 0 '''

    try:
        db.execute(sql)
        posts = []
        for post in db.fetchall():
            posts.append(
                {
                    "id": post[0],
                    "link": post[1],
                    "n_likes": post[2]
                }
            )

    except Exception as e:
        logger.error('Failed to get list of pending posts!')
        logger.exception(e)

        json_res = json.dumps(
            {'error': 'Failed to get posts!'})
        res = Response(json_res, status=500,
                       mimetype='application/json')
        return res

    posts = {'posts': posts}
    res = Response(json.dumps(posts), status=200,
                   mimetype='application/json')
    logger.info('List of posts returned successfully!')
    return res


@posts_blueprint.route('/<post_id>', methods=['PUT'])
def decrement_post_likes(post_id):
    """
        Updates post's pending likes 
    """
    logger.info('Updating post {} likes'.format(post_id))

    sql = ''' SELECT n_likes FROM posts WHERE id=%s'''
    try:
        db.execute(sql, (post_id,))
        n_likes = db.fetchone()
        n_likes = int(n_likes[0])

        if n_likes == 0:
            sql = "DELETE FROM posts WHERE id=%s"
            db.execute(sql, post_id)

        else:
            n_likes = n_likes - 1
            sql = "UPDATE posts SET n_likes = %s WHERE id=%s"
            db.execute(sql, (n_likes, post_id,))

    except Exception as e:
        logger.error('Failed to decrement post likes!')
        logger.exception(e)

        json_res = json.dumps({'message': 'Failed to update likes!'})
        res = Response(json_res, status=500, mimetype='application/json')

        return res

    json_res = json.dumps({'message': 'Post likes updated!'})
    res = Response(json_res, status=200, mimetype='application/json')

    return res


@posts_blueprint.route('/', methods=['POST'])
def add_post():
    """
        Adds posts to teh queue
        if post is already in the database
        the number of pending likes will be updated
    """
    data = json.loads(request.data)
    data = [data["postLink"], data["nCurtidas"]]
    
    logger.info('Adding post {} to the database!'.format(data))

    # increments likes of post thats already in the list
    try:
        if check_if_posts_exists(data[0]):
            update_existent_post_likes(data[0], data[1])

            json_res = json.dumps({'message': 'Post updated'})
            res = Response(json_res, status=200,
                        mimetype='application/json')

            return res
    
    except Exception as e:
        logger.error('Failed to update post!')
        logger.exception(e)

        json_res = json.dumps(
            {'error': 'Failed to increment post likes!'})
        res = Response(json_res, status=500,
            mimetype='application/json')

        return res

    sql = ''' INSERT INTO posts(link, n_likes) VALUES(%s,%s)'''

    try:
        logger.info('Creating new post {}'.format(data))
        db.execute(sql, data)

    except:
        logger.error('Failed to create new post!')
        json_res = json.dumps({'error': 'Failed to add post!'})
        res = Response(json_res, status=500, mimetype='application/json')

        return res

    logger.info('Post created successfully!')
    json_res = json.dumps({'message': 'Post added'})
    res = Response(json_res, status=200, mimetype='application/json')
     
    return res

def check_if_posts_exists(post_link):
    logger.info('Checking if post already exists...')

    sql = ''' SELECT id, n_likes FROM posts WHERE link=%s '''
    db.execute(sql, (post_link,))
    post = db.fetchall()

    if not len(post) == 0:
        logger.debug('Post does exist!')
        return True
    
    logger.debug('Post does not exist!')
    return False

def update_existent_post_likes(n_likes, post_link):
    logger.debug('Updating existent post {}'.format(post_link))
    sql = ''' SELECT id, n_likes FROM posts WHERE link=%s '''
    db.execute(sql, (post_link,))
    post = db.fetchall()

    n_likes = int(post[0][1]) + int(n_likes)
    post_id = post[0][0]

    sql = ''' UPDATE posts SET n_likes=%s WHERE id=%s '''

    db.execute(sql, (n_likes, post_id))
