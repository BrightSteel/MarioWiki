from flask import *
import db
import utils

bp = Blueprint("games", __name__, url_prefix="/categories/games")

@bp.route("/", methods=["GET", "POST"])
def games():
  if (request.form.get('hidden')):
    if request.method == "POST":
      form = request.form
      id = form.get('hidden', '')
      updatedPost = form.get('update', '')
      db.update_post(updatedPost, id)

  args = request.args
  title = args.get('page') # Referencing the title of a page
  tag = args.get('tag')

  if tag:
    page = request.args.get('page') # Referencing the current page for pagination
    if not page:
      page = 0
    else:
      page = int(page)

    posts = db.get_posts_by_tag_and_category(tag, "games", page=page)
    page_count = utils.get_total_pages(db.get_count_by_tag_and_category(tag, "games")[0])

    all_posts = db.get_all_posts_by_category("games")
    a_z_dicts = utils.get_a_to_z_dicts(all_posts)

    tags = utils.get_unique_tags()
    tag_posts = []
    for post in posts:
      cur_entry = {
        "title": post[0],
        "raw_text": post[1]
      }
      tag_posts.append(cur_entry)
    
    data = {
      "tag_posts": tag_posts,
      "tag": tag,
      "category": "Games",
      "tags": tags,
      "a_z_dicts": a_z_dicts,
      "post_url": request.url_root + "categories/",
      "page": page,
      "page_count": page_count
    }
    return render_template("tags.html", data=data, logo_url=utils.logo_url ,favicon_url=utils.favicon_url, error_url=utils.error_url, loading_url=utils.loading_url)
  
  if title:
    database = db.get_post_by_title(title=title)
    try:
      content = database[1]
    except Exception as e:
      abort(404)
    headers = utils.get_list_of_headers(content)
    content = headers[0]
    headers = headers[1]

    title = database[0]
    category = database[2]
    author = database[3]
    id = database[4]

    author_id = db.get_post_by_id(id)[1]

    content = utils.add_class_to_imgs(content)

    all_posts = db.get_all_posts_by_category("games")
    a_z_dicts = utils.get_a_to_z_dicts(all_posts)

    tags = utils.get_unique_tags()

    data = {
      "title": title,
      "content": content,
      "category": category,
      "author": author,
      "author_id": author_id,
      "headers": headers,
      "post_id": id,
      "post_url": request.url_root + "categories/",
      "a_z_dicts": a_z_dicts,
      "tags": tags
    }
    return render_template("wiki-post.html", data=data, logo_url=utils.logo_url ,favicon_url=utils.favicon_url, error_url=utils.error_url, loading_url=utils.loading_url)

  trending_posts = db.get_trending_posts("games")
  trending = []
  for post in trending_posts:
    cur = {
      "title": post[0],
      "thumbnail": post[1],
      "likes": post[2]
    }
    trending.append(cur)

  all_posts = db.get_all_posts_by_category("games")
  a_z_dicts = utils.get_a_to_z_dicts(all_posts)

  tags = utils.get_unique_tags()

  user_ids = db.get_top_contributors_by_category("games")
  top_contributors = []
  for id in user_ids:
    user = db.get_user_by_id(id[0])
    if user:
      contributor = {
        "username": user[0][1],
        "photo": user[0][2],
      }
      top_contributors.append(contributor)

  data = {
    "category": "Games",
    "trending": trending,
    "post_url": request.url_root + "categories/",
    "a_z_dicts": a_z_dicts,
    "tags": tags,
    "top_contributors": top_contributors
  }
  return render_template("categories.html", data=data, logo_url=utils.logo_url ,favicon_url=utils.favicon_url, error_url=utils.error_url, loading_url=utils.loading_url)
