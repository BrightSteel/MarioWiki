from flask import *
import db, utils

bp = Blueprint("search", __name__, url_prefix="/search")
@bp.route("/", methods=["GET"])
def get_search():
  all_posts = db.get_all_posts()
  a_z_dicts = utils.get_a_to_z_dicts(all_posts)

  tags = utils.get_unique_tags()

  data = {
    "post_url": request.url_root + "categories/",
    "a_z_dicts": a_z_dicts,
    "tags": tags
  }

  return render_template("search.html", data=data, logo_url=utils.logo_url ,favicon_url=utils.favicon_url, error_url=utils.error_url, loading_url=utils.loading_url)

@bp.route("/results", methods=["GET"])
def search_results():
  page = int(request.args.get('page', '0'))
  query = request.args.get('search_query', '')
  post_type = request.args.get('post_type', '')
  category = request.args.get('category', '')

  all_posts = db.get_all_posts()
  a_z_dicts = utils.get_a_to_z_dicts(all_posts)

  tags = utils.get_unique_tags()

  filter = request.args.get('filter', '')
  if not filter:
    filter = "all posts"
  search_data = []
  if filter == "post" or filter == "discussion":
    search_results = db.search_post_type_full_text_content(query, filter, page=page)
    page_count = utils.get_total_pages(db.get_post_type_full_text_search_count(query, filter)[0])
  elif filter == "characters" or filter == "games" or filter == "content":
    search_results = db.search_category_full_text_content(query, filter, page=page)
    page_count = utils.get_total_pages(db.get_category_full_text_search_count(query, filter)[0])
  elif filter == "profiles":
    search_results = db.search_user_name_and_bio(query, page=page)
    page_count = utils.get_total_pages(db.get_user_name_and_bio_search_count(query)[0])
    for result in search_results:
      cur_entry = {
        "username": result[1],
        "bio": result[3],
      }

      search_data.append(cur_entry)

    data = {
      "search_results": search_data,
      "is_search": True,
      "page_count": page_count,
      "page": page,
      "query": query,
      "filter": filter,
      "post_url": request.url_root + "categories/",
      "a_z_dicts": a_z_dicts,
      "tags": tags
    }
  else:
    search_results = db.search_full_text_content(query, page=page)
    page_count = utils.get_total_pages(db.get_full_text_search_count(query)[0])

  if filter != "profiles":
    for result in search_results:
      cur_entry = {
        "id": result[0],
        "user_id": result[1],
        "title": result[2],
        "content": result[3],
        "category": result[4],
        "post_date": utils.get_elapsed_time(result[5]),
        "post_type": result[6],
        "likes": result[7],
        "raw_text": result[8]
      }

      search_data.append(cur_entry)

    data = {
      "search_results": search_data,
      "is_search": True,
      "page_count": page_count,
      "page": page,
      "query": query,
      "post_url": request.url_root + "categories/",
      "post_type": post_type,
      "category": category,
      "filter": filter,
      "a_z_dicts": a_z_dicts,
      "tags": tags
    }
  return render_template("search.html", data=data, logo_url=utils.logo_url ,favicon_url=utils.favicon_url, error_url=utils.error_url, loading_url=utils.loading_url)