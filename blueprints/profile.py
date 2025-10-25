from flask import *
import db, boto3
import utils
from os import environ as env

s3 = boto3.client('s3',
                  aws_access_key_id=env['AWS_ACCESS_KEY_ID'],
                  aws_secret_access_key=env['AWS_SECRET_ACCESS_KEY'])

bp = Blueprint("profile", __name__, url_prefix="/profile")

@bp.route("/", methods=["GET", "POST"])
def profile():
  if session.get("user"):
    if request.method == "POST":
      return update()
    user_id = session["user"]["userinfo"]["sub"]
    user = db.get_user_by_id(user_id)
    if user[0]['photo_url'] is None:
      user_img = env['DEFAULT_AVATAR']
    else:
      user_img = user[0]['photo_url']
    user_bio = user[0]['bio']
    user_name = session["user"]["userinfo"]["nickname"]
    post_count = db.get_post_count_by_user(user_id)[0]
    is_follower = False

    follower_count = db.get_following_count(user_id)[0]

    following_id = db.get_following(user_id)
    following = []
    if (len(following_id) >= 1):
      if (following_id):
        for following_id in following_id:
          following.append(db.get_user_by_id(following_id[0]))
    else:
      following = ""

    page = request.args.get('page')
    if page == None:
      page = 0
    else:
      page = int(page)

    recent_posts = db.get_recent_posts_by_user(user_name, page=page)
    for post in recent_posts:
      post[3] = utils.get_elapsed_time(post[3])
      post.append(db.get_num_comments_by_post_id(post[7])[0])

    page_count = utils.get_total_pages(db.get_post_count_by_user(user_id)[0])

    all_posts = db.get_all_posts()
    a_z_dicts = utils.get_a_to_z_dicts(all_posts)

    tags = utils.get_unique_tags()

    data = {
      "user_img": user_img,
      "user_bio": user_bio,
      "user_name": user_name,
      "post_count": post_count,
      "following": following,
      "follower_count": follower_count,
      "is_follower": is_follower,
      "user_id": user_id,
      "recent_posts": recent_posts,
      "page_count": page_count,
      "page": page,
      "post_url": request.url_root + "categories/",
      "own_profile": True,
      "a_z_dicts": a_z_dicts,
      "tags": tags
    }
    return render_template("profile.html", data=data, logo_url=utils.logo_url ,favicon_url=utils.favicon_url, error_url=utils.error_url, loading_url=utils.loading_url)
  else:
    return redirect("/")
    
@bp.route("/<username>")
def get_profile_page(username):
  user = db.get_user_by_username(escape(username))
  try:
    user_id = user[0]['user_id']
  except Exception as e:
    abort(404)
  if user[0]['photo_url'] is None:
    user_img = env['DEFAULT_AVATAR']
  else:
    user_img = user[0]['photo_url']
  user_bio = user[0]['bio']
  user_name = user[0]['username']
  is_follower = False
    
  if (session.get("user")):
    if (user_id == session["user"]["userinfo"]["sub"]):
      return redirect("/profile")

  post_count = db.get_post_count_by_user(user_id)[0]

  session_user = session.get("user", "")

  follower_id = db.get_followers(user_id)
  followers = []
  if (len(follower_id) >= 1):
    if (follower_id):
      for follower_id in follower_id:
        followers.append(db.get_user_by_id(follower_id[0]))
        if session_user:
          if (session["user"]["userinfo"]["sub"] == follower_id[0]):
            is_follower = True
  else:
    followers = ""
    
  follower_count = db.get_follower_count(user_id)[0]

  own_profile = False
  if session_user:
    own_profile = (session["user"]["userinfo"]["sub"] == user_id)

  page = request.args.get('page')
  if page == None:
    page = 0
  else:
    page = int(page)

  recent_posts = db.get_recent_posts_by_user(user_name, page=page)
  for post in recent_posts:
    post[3] = utils.get_elapsed_time(post[3]) # convert timestamp to elapsed time
    post.append(db.get_num_comments_by_post_id(post[7])[0])

  page_count = utils.get_total_pages(db.get_post_count_by_user(user_id)[0])

  all_posts = db.get_all_posts()
  a_z_dicts = utils.get_a_to_z_dicts(all_posts)

  tags = utils.get_unique_tags()

  data = {
    "user_img": user_img,
    "user_bio": user_bio,
    "user_name": user_name,
    "post_count": post_count,
    "user_id" : user_id,
    "followers": followers,
    "follower_count": follower_count,
    "recent_posts": recent_posts,
    "page_count": page_count,
    "page": page,
    "post_url": request.url_root + "categories/",
    "own_profile": own_profile,
    "is_follower": is_follower,
    "a_z_dicts": a_z_dicts,
    "tags": tags
  }
  return render_template("profile.html", data=data, logo_url=utils.logo_url ,favicon_url=utils.favicon_url, error_url=utils.error_url, loading_url=utils.loading_url)

def update():
  content = request.form.get("content")
  user_id = session["user"]["userinfo"]["sub"]
  bio = utils.sanitizer.sanitize(content)
  db.update_user_bio(user_id, bio)
  return redirect("/profile")
 
@bp.route('/follow/<profile_id>', methods=['POST'])
def follow_user(profile_id):
  profile = db.get_user_by_id(profile_id)
  url = "/profile/" + profile[0]['username']
  user_id = session["user"]["userinfo"]["sub"]
  db.add_follower(profile_id,user_id)
  return redirect(url)

@bp.route('/unfollow/<profile_id>', methods=['POST'])
def unfollow(profile_id):
  profile = db.get_user_by_id(profile_id)
  url = "/profile/" + profile[0]['username']
  user_id = session["user"]["userinfo"]["sub"]
  db.remove_follower(profile_id,user_id)
  return redirect(url)

@bp.route('/remove/<username>', methods=['GET', 'POST'])
def unfollow_username(username):
  following = db.get_user_by_username(username)[0][0]
  user_id = session["user"]["userinfo"]["sub"]
  db.remove_follower(following,user_id)
  return '', 204

@bp.route('/upload', methods=['POST'])
def upload():
  file = request.files['photo']
  user_id = session["user"]["userinfo"]["sub"]
  filename = f"{user_id}/profile_photo"
  s3.upload_fileobj(file, env['BUCKET'], filename)
  photo_url = f"https://{env['BUCKET']}.s3.us-east-2.amazonaws.com/{filename}"
  db.update_user_img(photo_url,user_id)
  return '', 204