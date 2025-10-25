from flask import *
import db
import utils
from os import environ as env

bp = Blueprint("community", __name__, url_prefix="/community")
@bp.route("/")
def community():
  categories = db.get_category_titles()
  follow_btn_checked = False

  games_category_count = db.get_post_count_by_category(category="Games", type="DISCUSSION")[0]
  if (games_category_count >= 1):
    recent_games = db.get_recent_posts_by_category(category="Games", type="DISCUSSION")[0]
    recent_games[3] = utils.get_elapsed_time(recent_games[3])
  else:
    recent_games = {"status": "no posts"}
    
  character_category_count = db.get_post_count_by_category(category="Characters", type="DISCUSSION")[0]
  if (character_category_count >= 1):
    recent_character = db.get_recent_posts_by_category(category="Characters", type="DISCUSSION")[0]
    recent_character[3] = utils.get_elapsed_time(recent_character[3])
  else:
    recent_character = {"status": "no posts"}
    
  content_category_count = db.get_post_count_by_category(category="Content", type="DISCUSSION")[0]
  if (content_category_count >= 1):
    recent_content = db.get_recent_posts_by_category(category="Content", type="DISCUSSION")[0]
    recent_content[3] = utils.get_elapsed_time(recent_content[3])
  else:
    recent_content = {"status": "no posts"}

  page = request.args.get('page')
  if page == None:
    page = 0
  else:
    page = int(page)

  filter = request.args.getlist('categories_filter')
  if filter:
    if len(filter) == 1:
      recent_posts = db.get_recent_discussions_by_one_category(filter[0], page=page)
      page_count = utils.get_total_pages(db.get_post_count_by_one_category(filter[0])[0])
      next_page_url = request.url_root + "community/?categories_filter=" + filter[0]
    elif len(filter) == 2:
      recent_posts = db.get_recent_discussions_by_two_categories(filter[0], filter[1], page=page)
      page_count = utils.get_total_pages(db.get_post_count_by_two_categories(filter[0], filter[1])[0])
      next_page_url = request.url_root + "community/?categories_filter=" + filter[0] + "&categories_filter="+filter[1]
    elif len(filter) == 3:
      recent_posts = db.get_recent_discussions_by_three_categories(filter[0], filter[1], filter[2], page=page)
      page_count = utils.get_total_pages(db.get_post_count_by_three_categories(filter[0], filter[1], filter[2])[0])
      next_page_url = request.url_root + "community/?categories_filter=" + filter[0] + "&categories_filter="+filter[1] + "&categories_filter="+filter[2]
  else:
    recent_posts = db.get_recent_posts(type="DISCUSSION", page=page)
    page_count = utils.get_total_pages(db.get_post_count(type="DISCUSSION")[0])
    next_page_url = request.url_root + "community"
    
  for post in recent_posts:
    post[3] = utils.get_elapsed_time(post[3]) # convert timestamp to elapsed time
    if post[6] == None:
      post[6] = env['DEFAULT_AVATAR']
    post.append(db.get_num_comments_by_post_id(post[7])[0])

  if session.get("user"):
    user_id = session["user"]["userinfo"]["sub"]
    user = db.get_user_by_id(user_id)
    if user[0]['photo_url'] is None:
      user_img = env['DEFAULT_AVATAR']
    else:
      user_img = user[0]['photo_url']
  else: 
    user_img = env['DEFAULT_AVATAR']

  all_posts = db.get_all_posts()
  a_z_dicts = utils.get_a_to_z_dicts(all_posts)

  tags = utils.get_unique_tags()

  data = {
    "games_category_count": games_category_count,
    "character_category_count": character_category_count,
    "content_category_count": content_category_count,
    "recent_games": recent_games,
    "recent_character": recent_character,
    "recent_content": recent_content,
    "categories": categories,
    "recent_posts": recent_posts,
    "page_count": page_count,
    "page": page,
    "user_img": user_img,
    "post_url": request.url_root + "categories/",
    "a_z_dicts": a_z_dicts,
    "tags": tags,
    "follow_btn_checked": follow_btn_checked,
    "next_page_url": next_page_url,
    "filters": filter
  }
        
  return render_template("community_feed.html", data=data, logo_url=utils.logo_url ,favicon_url=utils.favicon_url, error_url=utils.error_url, loading_url=utils.loading_url)

@bp.route("/following")
def community_following():
  categories = db.get_category_titles()
  follow_btn_checked = True

  games_category_count = db.get_post_count_by_category(category="Games", type="DISCUSSION")[0]
  if (games_category_count >= 1):
    recent_games = db.get_recent_posts_by_category(category="Games", type="DISCUSSION")[0]
    recent_games[3] = utils.get_elapsed_time(recent_games[3])
  else:
    recent_games = {"status": "no posts"}
    
  character_category_count = db.get_post_count_by_category(category="Characters", type="DISCUSSION")[0]
  if (character_category_count >= 1):
    recent_character = db.get_recent_posts_by_category(category="Characters", type="DISCUSSION")[0]
    recent_character[3] = utils.get_elapsed_time(recent_character[3])
  else:
    recent_character = {"status": "no posts"}
    
  content_category_count = db.get_post_count_by_category(category="Content", type="DISCUSSION")[0]
  if (content_category_count >= 1):
    recent_content = db.get_recent_posts_by_category(category="Content", type="DISCUSSION")[0]
    recent_content[3] = utils.get_elapsed_time(recent_content[3])
  else:
    recent_content = {"status": "no posts"}

  page = request.args.get('page')
  if page == None:
    page = 0
  else:
    page = int(page)

  if session.get("user"):
    user_id = session["user"]["userinfo"]["sub"]
    user = db.get_user_by_id(user_id)
    if user[0]['photo_url'] is None:
      user_img = env['DEFAULT_AVATAR']
    else:
      user_img = user[0]['photo_url']
  else: 
    user_img = env['DEFAULT_AVATAR']

  following = db.get_following(user_id)
  posts_by_following = []
  for user in following:
    following_post = db.get_recent_discussion_by_user_id(user[0], page=page)
    if len(following_post) >= 1:
      posts_by_following.append(following_post)

  total_posts = 0
  for users_posts in posts_by_following:
    for post in users_posts:
      post[3] = utils.get_elapsed_time(post[3]) # convert timestamp to elapsed time
      post.append(db.get_num_comments_by_post_id(post[7])[0])
      total_posts += 1

  page_count = utils.get_total_pages(total_posts)

  all_posts = db.get_all_posts()
  a_z_dicts = utils.get_a_to_z_dicts(all_posts)

  tags = utils.get_unique_tags()

  data = {
    "games_category_count": games_category_count,
    "character_category_count": character_category_count,
    "content_category_count": content_category_count,
    "recent_games": recent_games,
    "recent_character": recent_character,
    "recent_content": recent_content,
    "categories": categories,
    "posts_by_following": posts_by_following,
    "page_count": page_count,
    "page": page,
    "user_img": user_img,
    "post_url": request.url_root + "categories/",
    "a_z_dicts": a_z_dicts,
    "tags": tags,
    "follow_btn_checked": follow_btn_checked,
    "next_page_url": request.url_root + "community/following"
  }
        
  return render_template("community_feed.html", data=data, logo_url=utils.logo_url ,favicon_url=utils.favicon_url, error_url=utils.error_url, loading_url=utils.loading_url)

@bp.route("/discussion/create", methods=["POST"])
def add_discussion():
  if session.get("user") != None:
    data = request.form
    title = data.get("title")
    content = data.get("content")

  # Remove leading and trailing whitespace from the title.
    title = title.strip()

  # Sanitize the content
  content = utils.sanitizer.sanitize(content)

  parser = utils.MyHTMLParser()
  parser.feed(content)
  raw_text = parser.rawText
        
  category = data.get("category")
  user_id = session["user"]["userinfo"]["sub"]
  db.add_post(title, content, category, user_id, "DISCUSSION", raw_text)
  return redirect("/community")