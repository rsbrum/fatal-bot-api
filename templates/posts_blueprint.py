from flask import Blueprint, Response, request
from jinja2 import TemplateNotFound
from flask_cors import CORS, cross_origin
import db as database
import json

posts_blueprint = Blueprint('posts_blueprint', __name__)
CORS(posts_blueprint, resources={r"/api/*": {"origins": "*"}})

db = None

# starts database connection


def before():
    CORS(posts_blueprint)
    global db
    db = database.get_db()

# closes database connection


def after(f):
    global db
    database.close_db()
    return f


posts_blueprint.before_request(before)
posts_blueprint.after_request(after)

# returns list of posts that have likes pending
@posts_blueprint.route('/', methods=['GET'])
def get_posts():
    sql = ''' SELECT * FROM posts WHERE n_likes > 0 '''
 
    try:
        posts = db.execute(sql)
        posts = json.dumps(db.fetchall())
    except Exception as e:
        print(e)
        json_res = json.dumps(
            {'error': 'Failed to get posts!'})
        res = Response(json_res, status=500,
                        mimetype='application/json')
        return res
        
    json_res = json.dumps(
        {'posts': posts})
    res = Response(json_res, status=200,
                   mimetype='application/json')
    return res

# adds posts to the queue
# if post is already in the database
# updates number of likes pending
@posts_blueprint.route('/', methods=['POST'])
def add_post():

    data = json.loads(request.data)
    data = [data["postLink"], data["nCurtidas"]]
    sql = ''' SELECT id, n_likes FROM posts WHERE link=%s ''' 
    strng = data[0]
    # increments likes of post thats already in the list
    try:
        db.execute(sql, (strng,)) 
        post_id = db.fetchall()
        if not len(post_id) == 0: 
            n_likes = int(post_id[0][1]) + int(data[1])
            post_id = post_id[0][0]
            sql = ''' UPDATE posts SET n_likes=%s WHERE id=%s '''
            try:
                db.execute(sql, (n_likes, post_id))
                json_res = json.dumps({'message': 'Post updated'})
                res = Response(json_res, status=200,
                               mimetype='application/json')
                return res
            except Exception as e:
                print(e)
                json_res = json.dumps(
                    {'error': 'Failed to increment post likes!'})
                res = Response(json_res, status=500,
                               mimetype='application/json')
                return res

    except Exception as e: 
        print(e)
        json_res = json.dumps({'error': 'Failed to verify post!'})
        res = Response(json_res, status=500, mimetype='application/json')
        return res

    sql = ''' INSERT INTO posts(link, n_likes) VALUES(%s,%s)'''
    try:
        db.execute(sql, data)
    except:
        json_res = json.dumps({'error': 'Failed to add post!'})
        res = Response(json_res, status=500, mimetype='application/json')
        return res

    json_res = json.dumps({'message': 'Post added'})
    res = Response(json_res, status=200, mimetype='application/json')
    return res

# updates post's likes once its been liked by the bot
@posts_blueprint.route('/<post_id>', methods=['GET'])
def post_countdown(post_id):
    sql = ''' SELECT n_likes FROM posts WHERE id=%s'''
    try:
        db.execute(sql, post_id)
        n_likes = db.fetchone()
        n_likes = int(n_likes[0])

        if n_likes == 0:
            sql = "DELETE * FROM posts WHERE id=%s"
            db.execute(sql, post_id)
        else:
            n_likes = n_likes - 1
            sql = "UPDATE posts SET n_likes = %s WHERE id=%s"
            db.execute(sql, (n_likes, post_id))

    except Exception as e:
        print(e)
        json_res = json.dumps({'message': 'Failed to update likes!'})
        res = Response(json_res, status=500, mimetype='application/json')
        return res

    json_res = json.dumps({'message': 'Post likes updated!'})
    res = Response(json_res, status=200, mimetype='application/json')
    return res
