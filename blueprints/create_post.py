from flask import *
import db
import utils
import boto3
from os import environ as env
s3 = boto3.client('s3',
                  aws_access_key_id=env['AWS_ACCESS_KEY_ID'],
                  aws_secret_access_key=env['AWS_SECRET_ACCESS_KEY'])

bp = Blueprint("create_post", __name__, url_prefix="/post")
@bp.route("/create", methods=["POST", "GET"])
def create_post():
  if request.method == 'POST':
    return add_post()
  elif session.get("user") != None:
    categories = db.get_category_titles()

    all_posts = db.get_all_posts()
    a_z_dicts = utils.get_a_to_z_dicts(all_posts)

    tags = utils.get_unique_tags()

    all_tags = db.get_all_unique_tags()

    data = {
      "categories": categories,
      "post_url": request.url_root + "categories/",
      "a_z_dicts": a_z_dicts,
      "tags": tags, # This is a dictionary containing unique tags for each category.
      "all_tags": all_tags # This is a list of every unique tag, regardless of category.
    }
    return render_template("create_post.html", data=data, logo_url=utils.logo_url ,favicon_url=utils.favicon_url, error_url=utils.error_url, loading_url=utils.loading_url, default_url=env['DEFAULT_THUMBNAIL_URL'])
  else:
    return redirect("/login")

def add_post():
  if session.get("user") != None:
    data = request.form
    title = data.get("title")
    content = data.get("content")

    # Remove leading whitespace from the title
    title = title.strip()
    # Sanitize the content
    content = utils.sanitizer.sanitize(content)

    if db.get_post_by_title(title):
      return redirect(url_for("create_post.alreadyExists", title=title))

    ## thumbnail stuff
    thumbnail = request.files["thumbnail"]
    if thumbnail:
      filename = "thumbnail/"+thumbnail.filename
      s3.upload_fileobj(thumbnail, env['BUCKET'], filename)
      photo_url = f"https://{env['BUCKET']}.s3.us-east-2.amazonaws.com/{filename}"
    else: 
      photo_url = env['DEFAULT_THUMBNAIL_URL'] 

    parser = utils.MyHTMLParser()
    parser.feed(content)
    raw_text = parser.rawText

    category = data.get("category")
    user_id = session["user"]["userinfo"]["sub"]

    # Utilized this website to discover the data.getlist() attribute to get all checked checkbox links:
    # https://stackoverflow.com/questions/44600601/get-a-list-of-values-from-checkboxes-using-flask-through-python
    tags = data.getlist('tags_check')
    db.add_post(title, content, category, user_id, "POST", raw_text, photo_url)

    post_id = db.get_post_id_by_info(user_id, title, raw_text, category)[0]
    for tag in tags:
      db.add_post_to_tags(tag, post_id)
  return redirect("/")

@bp.route("/detail/<post_id>", methods=["POST", "GET"])
def detail(post_id):
  if (request.form.get('hidden')):
    if request.method == "POST":
      form = request.form
      id = form.get('hidden', '')
      updatedDiscussion = form.get('update', '')
      db.update_post(updatedDiscussion, id)
            
  postId = post_id
  post = db.get_post_by_id(postId)
  post_data = {
    "post_title": post[2],
    "post_content": post[3],
    "post_category":post[4].lower(),
    "post_time":post[5].strftime("%m/%d/%Y, %H:%M:%S"),
    "post_id":post_id,
  }

  category = db.get_category_by_name(post[4])
  category_data={
    "category_description": category[1],
    "category_icon" : category[2]
  }

  author_id = post[1]
  author = db.get_user_by_id(author_id)[0]
  author_post = db.get_post_count_by_user(author_id)
  author_data = {
    "author_img": author[2],
    "author_bio": author[3],
    "author_name": author[1],
    "author_fan": db.get_follower_count(author_id)[0],
    "author_post":author_post[0],
  }
    
  comments = db.get_comments_by_post_id(post_id)
  if comments:
    for comment in comments:
      comment_user= db.get_user_by_id(comment[1])[0]
      comment[1]=comment_user
      comment[4] = utils.get_elapsed_time(comment[4])

  all_posts = db.get_all_posts()
  a_z_dicts = utils.get_a_to_z_dicts(all_posts)

  tags = utils.get_unique_tags()

  data = {
    "comments": comments,
    "post_data": post_data,
    "author_data": author_data,
    "author_id": author_id,
    "category_data": category_data,
    "post_id": postId,
    "post_url": request.url_root + "categories/",
    "a_z_dicts": a_z_dicts,
    "tags": tags
  }

  if session.get("user") != None:
    if (request.form.get('content')):
      if request.method == "POST":
        return create_comment(post_id)
    
  return render_template('details.html', data=data, logo_url=utils.logo_url ,favicon_url=utils.favicon_url, error_url=utils.error_url, loading_url=utils.loading_url)

### API for getting discussion info and check if loggin in user is same as post creater
@bp.route("/postDetail/<int:post_id>/",methods=["GET"])
def getPostDetails(post_id):
  post = db.get_post_by_id(post_id)
  author_id = post[1]
  author = db.get_user_by_id(author_id)[0]
  author_name = author[0]
  post_author = session["user"]["userinfo"]["sub"]
  if (author_name == post_author):
    post_content = post[3]
  else:
    abort(401)
  return jsonify({"post_content":post_content})

### API for getting wiki_post info and check if user is logged in
@bp.route("/wikipostDetail/<int:post_id>/",methods=["GET"])
def getWikiPostDetails(post_id):
  post = db.get_post_by_id(post_id)
  if (session.get("user")):
    post_content = post[3]
  else:
    abort(401)
  return jsonify({"post_content":post_content})

### API for just checking if loggin in user is same as post creater
@bp.route("/isLoggedInAuthor/<int:post_id>/",methods=["GET"])
def checkLoggedIn(post_id):
  post = db.get_post_by_id(post_id)
  author_id = post[1]
  author = db.get_user_by_id(author_id)[0]
  author_name = author[0]
  post_author = session["user"]["userinfo"]["sub"]
  if (author_name == post_author):
    return '', 204
  else:
    abort(401)

### API for deleting post and check if loggin in user is same as post creater
@bp.route("/deleteDiscussion/<int:post_id>/",methods=["GET"])
def deletePost(post_id):
  post = db.get_post_by_id(post_id)
  author_id = post[1]
  author = db.get_user_by_id(author_id)[0]
  author_name = author[0]
  post_author = session["user"]["userinfo"]["sub"]
  if (author_name == post_author):
    db.delete_all_likes(post_id)
    db.delete_tags(post_id)
    db.delete_post(post_id)
  else:
    abort(401)
  return '', 204

def create_comment(post_id):
  content = request.form.get("content")
  content = utils.sanitizer.sanitize(content)
  user_id = session["user"]["userinfo"]["sub"]
  db.add_comment(user_id, post_id, content)
  return redirect(f"/post/detail/{post_id}")

@bp.route("/alreadyExists")
def alreadyExists():
  title = request.args.get("title")
  post = db.get_post_by_title(title)

  tags = utils.get_unique_tags()

  all_posts = db.get_all_posts()
  a_z_dicts = utils.get_a_to_z_dicts(all_posts)

  data = {
    "title": post[0],
    "category": post[2],
    "tags": tags,
    "a_z_dicts": a_z_dicts,
    "post_url": request.url_root + "categories/"
  }

  return render_template("already_exists.html", data=data, logo_url=utils.logo_url ,favicon_url=utils.favicon_url, error_url=utils.error_url, loading_url=utils.loading_url)
