from flask import *
import db
import utils
from functools import wraps

bp = Blueprint("home", __name__, url_prefix="/")
@bp.route("/")
@bp.route("/home")
def home():
  page = request.args.get('page')
  if page == None:
    page = 0
  else:
    page = int(page)
  recent_posts = db.get_recent_posts(page=page)

  for post in recent_posts:
    post[3] = utils.get_elapsed_time(post[3]) # convert timestamp to elapsed time
    
  page_count = utils.get_total_pages(db.get_post_count()[0])

  post_count = db.get_post_count()

  trending_tags = db.get_trending_tags()

  all_posts = db.get_all_posts()
  a_z_dicts = utils.get_a_to_z_dicts(all_posts)

  tags = utils.get_unique_tags()

  data = {
    "recent_posts": recent_posts,
    "page_count": page_count,
    "page": page,
    "trending_tags": trending_tags,
    "post_url": request.url_root + "categories/",
    "a_z_dicts": a_z_dicts, 
    "tags": tags,
    "post_count": post_count
  }

  return render_template("home.html", data=data, logo_url=utils.logo_url ,favicon_url=utils.favicon_url, error_url=utils.error_url, loading_url=utils.loading_url)

# https://flask.palletsprojects.com/en/2.2.x/patterns/viewdecorators/
def login_required(f):
  @wraps(f)
  def decorated_function(*args, **kwargs):
    if session.get('user') is None:
      return redirect(url_for('login', next=request.url_root))
    return f(*args, **kwargs)
  return decorated_function

### API for getting likes
@bp.route("/post/<int:post_id>/like",methods=["GET"])
def get_post_likes(post_id):
  if (session.get("user")):
    return jsonify({'likes': db.get_likes(post_id), 'you_like': db.get_does_like(post_id, session["user"]["userinfo"]["sub"])})
  else:
    return jsonify({'likes': db.get_likes(post_id),'you_like':False})
        

@bp.route("/post/<int:post_id>/like1",methods=["POST"])
@login_required
def like_post(post_id):
  db.like_post(post_id, session["user"]["userinfo"]["sub"])
  db.increment_likes(post_id)
  return jsonify({'likes': db.get_likes(post_id), 'you_like': True})

@bp.route("/post/<int:post_id>/like1",methods=["DELETE"])
@login_required
def unlike_post(post_id):
  db.unlike_post(post_id, session["user"]["userinfo"]["sub"])
  db.decrement_likes(post_id)
  return jsonify({'likes': db.get_likes(post_id), 'you_like': False})