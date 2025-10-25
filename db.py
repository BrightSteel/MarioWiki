""" database access
docs:
* http://initd.org/psycopg/docs/
* http://initd.org/psycopg/docs/pool.html
* http://initd.org/psycopg/docs/extras.html#dictionary-like-cursor
"""
# Database startup code taken from 5117 kluver's session 07
from contextlib import contextmanager
import logging
import os

from flask import current_app, g

import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import DictCursor

pool = None

def setup():
  global pool
  DATABASE_URL = os.environ['DATABASE_URL']
  current_app.logger.info(f"creating db connection pool")
  pool = ThreadedConnectionPool(1, 10, dsn=DATABASE_URL, sslmode='require')

  make_table()


@contextmanager
def get_db_connection():
  try:
    connection = pool.getconn()
    yield connection
  finally:
    pool.putconn(connection)


@contextmanager
def get_db_cursor(commit=False):
  with get_db_connection() as connection:
    cursor = connection.cursor(cursor_factory=DictCursor)
    try:
      yield cursor
      if commit:
        connection.commit()
    finally:
      cursor.close()

def make_table():
  with get_db_cursor(True) as cur:
    cur.execute("""CREATE TABLE IF NOT EXISTS posts(
                    id SERIAL, 
                    user_id VARCHAR(128) NOT NULL, 
                    title VARCHAR(64) NOT NULL, 
                    content TEXT NOT NULL, 
                    category VARCHAR(64) NOT NULL, 
                    post_date TIMESTAMP NOT NULL default CURRENT_TIMESTAMP, 
                    post_type VARCHAR(16) NOT NULL, 
                    likes INT NOT NULL DEFAULT 0, 
                    raw_text TEXT NOT NULL,
                    thumbnail VARCHAR(128) NOT NULL,
                    PRIMARY KEY (id),
                    FOREIGN KEY (user_id) REFERENCES users(user_id))""")
        
    cur.execute("""CREATE TABLE IF NOT EXISTS post_comments(
                    id SERIAL NOT NULL, 
                    user_id VARCHAR(128) NOT NULL, 
                    post_id INT NOT NULL, 
                    content TEXT NOT NULL, 
                    post_date TIMESTAMP NOT NULL default CURRENT_TIMESTAMP,
                    revision_date TIMESTAMP, 
                    likes INT NOT NULL DEFAULT 0, 
                    PRIMARY KEY (id))""")
        
    cur.execute("""CREATE TABLE IF NOT EXISTS category(
                    title VARCHAR(64) NOT NULL, 
                    description TEXT, 
                    photo VARCHAR(256), 
                    PRIMARY KEY (title))""")
        
    cur.execute("""CREATE TABLE IF NOT EXISTS users(
                    user_id VARCHAR(128) NOT NULL, 
                    username VARCHAR(32) NOT NULL, 
                    photo_url VARCHAR(256), 
                    bio TEXT, 
                    PRIMARY KEY (user_id))""")
        
    cur.execute("""CREATE TABLE IF NOT EXISTS user_followers(
                    user_id VARCHAR(128) NOT NULL, 
                    follower_id VARCHAR(128) NOT NULL, 
                    PRIMARY KEY (user_id, follower_id), 
                    FOREIGN KEY (user_id) REFERENCES users(user_id))""")
        
    cur.execute("""CREATE TABLE IF NOT EXISTS post_likes(
                    post_id INT NOT NULL, 
                    user_id VARCHAR(128) NOT NULL, 
                    PRIMARY KEY (post_id, user_id), 
                    FOREIGN KEY (post_id) REFERENCES posts(id),
                    FOREIGN KEY (user_id) REFERENCES users(user_id))""")

    cur.execute("""CREATE TABLE IF NOT EXISTS tags(
                    tag VARCHAR(64),
                    post_id INT,
                    PRIMARY KEY (tag, post_id),
                    FOREIGN KEY (post_id) REFERENCES posts(id))""")

def get_category_titles():
  with get_db_cursor(True) as cur:
    cur.execute("SELECT title FROM category")
    return cur.fetchall()
    
def add_post(title, content, category, user_id, post_type, raw_text, thumbnail=None):
  with get_db_cursor(True) as cur:
    cur.execute("""INSERT INTO posts (title, content, category, user_id, post_type, raw_text, thumbnail) 
                   values (%s, %s, %s, %s, %s, %s, %s)""", 
                   (title, content, category, user_id, post_type, raw_text, thumbnail))
        
def get_post_count():
  with get_db_cursor(True) as cur:
    cur.execute("SELECT COUNT(*) FROM posts WHERE post_type = 'POST'")
    return cur.fetchone()
    
def remove_comments(post_id):
  with get_db_cursor(True) as cur:
    cur.execute("DELETE FROM post_comments WHERE post_id = %s", post_id)

def get_recent_posts(limit=5, page=0, type="POST"):
  with get_db_cursor(True) as cur:
    cur.execute("""select posts.title, posts.content, posts.category, posts.post_date, count(post_likes.post_id) as likes, 
                   users.username, users.photo_url, posts.id 
                   FROM posts left outer join users on users.user_id = posts.user_id  
                   left outer join post_likes on post_likes.post_id = posts.id 
                   WHERE posts.post_type = %s group by posts.id, username, photo_url 
                   order by posts.id desc limit %s offset %s""", 
                   (type, limit, page*limit))
    return cur.fetchall()
    
def get_recent_discussions_by_one_category(category1, limit=5, page=0, type="DISCUSSION"):
  with get_db_cursor(False) as cur:
    cur.execute("""select posts.title, posts.content, posts.category, posts.post_date, count(post_likes.post_id) as likes, 
                   users.username, users.photo_url, posts.id 
                   FROM posts left outer join users on users.user_id = posts.user_id 
                   left outer join post_likes on post_likes.post_id = posts.id 
                   WHERE posts.post_type = %s and posts.category=%s group by posts.id, username, photo_url 
                   order by posts.id desc limit %s offset %s""",
                   (type, category1, limit, page*limit))
    return cur.fetchall()
    
def get_recent_discussions_by_two_categories(category1, category2, limit=5, page=0, type="DISCUSSION"):
  with get_db_cursor(False) as cur:
    cur.execute("""select posts.title, posts.content, posts.category, posts.post_date, count(post_likes.post_id) as likes, 
                   users.username, users.photo_url, posts.id 
                   FROM posts left outer join users on users.user_id = posts.user_id  
                   left outer join post_likes on post_likes.post_id = posts.id 
                   WHERE posts.post_type = %s and (posts.category=%s or posts.category=%s) group by posts.id, username, photo_url 
                   order by posts.id desc limit %s offset %s""",
                   (type, category1, category2, limit, page*limit))
    return cur.fetchall()
    
def get_recent_discussions_by_three_categories(category1, category2, category3, limit=5, page=0, type="DISCUSSION"):
  with get_db_cursor(False) as cur:
    cur.execute("""select posts.title, posts.content, posts.category, posts.post_date, count(post_likes.post_id) as likes, 
                   users.username, users.photo_url, posts.id 
                   FROM posts left outer join users on users.user_id = posts.user_id 
                   left outer join post_likes on post_likes.post_id = posts.id 
                   WHERE posts.post_type = %s and (posts.category=%s or posts.category=%s or posts.category=%s) group by posts.id, username, photo_url 
                   order by posts.id desc limit %s offset %s""",
                   (type, category1, category2, category3, limit, page*limit))
    return cur.fetchall()
    
def get_post_count_by_one_category(category1, type="DISCUSSION"):
  with get_db_cursor(True) as cur:
    cur.execute("SELECT COUNT(*) FROM posts WHERE post_type = %s and category=%s", (type, category1))
    return cur.fetchone()
    
def get_post_count_by_two_categories(category1, category2, type="DISCUSSION"):
  with get_db_cursor(True) as cur:
    cur.execute("SELECT COUNT(*) FROM posts WHERE post_type = %s and (category=%s or category=%s)", (type, category1, category2))
    return cur.fetchone()
    
def get_post_count_by_three_categories(category1, category2, category3, type="DISCUSSION"):
  with get_db_cursor(True) as cur:
    cur.execute("SELECT COUNT(*) FROM posts WHERE post_type = %s and (category=%s or category=%s or category=%s)", (type, category1, category2, category3))
    return cur.fetchone()

#gets posts by category
def get_recent_posts_by_category(category, limit=1, page=0, type="POST"):
  with get_db_cursor(True) as cur:
    cur.execute("""select posts.title, posts.content, posts.category, posts.post_date, count(post_likes.post_id) as likes, 
                   users.username, users.photo_url
                   FROM posts left outer join users on users.user_id = posts.user_id 
                   left outer join post_likes on post_likes.post_id = posts.id 
                   WHERE posts.category = %s and posts.post_type = %s group by posts.id, username, photo_url 
                   order by posts.id desc limit %s offset %s""", 
                   (category, type, limit, page*limit))
    return cur.fetchall()
    
#gets posts by user
def get_recent_posts_by_user(username, limit=5, page=0):
  with get_db_cursor(True) as cur:
    cur.execute("""select posts.title, posts.content, posts.category, posts.post_date, count(post_likes.post_id) as likes, 
                   users.username, users.photo_url, posts.id, posts.post_type
                   FROM posts left outer join users on users.user_id = posts.user_id 
                   left outer join post_likes on post_likes.post_id = posts.id 
                   WHERE users.username = %s group by posts.id, username, photo_url 
                   order by posts.post_type desc limit %s offset %s""", 
                   (username, limit, page*limit))
    return cur.fetchall()
    
def get_recent_discussion_by_user_id(user_id, limit=5, page=0, type="DISCUSSION"):
  with get_db_cursor(True) as cur:
    cur.execute("""select posts.title, posts.content, posts.category, posts.post_date, count(post_likes.post_id) as likes, 
                   users.username, users.photo_url, posts.id 
                   FROM posts left outer join users on users.user_id = posts.user_id 
                   left outer join post_likes on post_likes.post_id = posts.id 
                   WHERE posts.post_type = %s and users.user_id = %s group by posts.id, username, photo_url 
                   order by posts.id desc limit %s offset %s""", 
                   (type, user_id, limit, page*limit))
    return cur.fetchall()
    
def get_post_count(type="POST"):
  with get_db_cursor(True) as cur:
    cur.execute("SELECT COUNT(*) FROM posts WHERE post_type = %s", (type,))
    return cur.fetchone()

def get_post_count_by_category(category, type="DISCUSSION"):
  with get_db_cursor(True) as cur:
    cur.execute("SELECT COUNT(*) FROM posts WHERE category= %s and post_type = %s", (category, type))
    return cur.fetchone()
  
def get_post_count_by_user(user_id):
  with get_db_cursor(True) as cur:
    cur.execute("SELECT COUNT(*) FROM posts WHERE user_id= %s", (user_id, ))
    return cur.fetchone()    
    
def add_user(user_id, username):
  with get_db_cursor(True) as cur:
    cur.execute("INSERT INTO users (user_id, username) values (%s, %s)", (user_id, username))

def get_user_by_id(user_id):
  with get_db_cursor(True) as cur:
    cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    return cur.fetchall()

def get_user_by_username(username):
  with get_db_cursor(True) as cur:
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    return cur.fetchall()

def get_post_by_title(title, type="POST"):
  with get_db_cursor(True) as cur:
    cur.execute("""SELECT posts.title, posts.content, posts.category, users.username, posts.id
                   FROM posts
                   INNER JOIN users ON posts.user_id = users.user_id
                   WHERE post_type=%s AND title=%s""",
                   (type, title))
    return cur.fetchone()
    
def update_user_bio(user_id, bio):
  with get_db_cursor(True) as cur:
    cur.execute('UPDATE users SET bio=%s where user_id=%s',(bio, user_id,))

def update_user_img(photo_url, user_id):
  with get_db_cursor(True) as cur:
    cur.execute("UPDATE users SET photo_url = %s WHERE user_id = %s", (photo_url, user_id))

def add_follower(user_id, follower_id):
  with get_db_cursor(True) as cur:
    cur.execute("""insert into user_followers (user_id, follower_id) values (%s, %s) 
                   on conflict do nothing""" ,
                   (user_id,follower_id,))
        
def remove_follower(user_id, follower_id):
  with get_db_cursor(True) as cur:
    cur.execute("""delete from user_followers where user_id=%s and follower_id = %s""" , (user_id, follower_id,))

#this gets people who are following you or another user
def get_followers(user_id):
  with get_db_cursor(True) as cur:
    cur.execute("select follower_id from user_followers where user_id = %s;", (user_id,))
    return cur.fetchall()

#this gets who you are following (used for community feed )
def get_following(user_id):
  with get_db_cursor(True) as cur:
    cur.execute("select user_id from user_followers where follower_id = %s;", (user_id,))
    return cur.fetchall()
    
def get_follower_count(user_id):
  with get_db_cursor(True) as cur:
    cur.execute("select count(follower_id) from user_followers where user_id = %s;", (user_id,))
    return cur.fetchone()
    
def get_following_count(user_id):
  with get_db_cursor(True) as cur:
    cur.execute("select count(user_id) from user_followers where follower_id = %s;", (user_id,))
    return cur.fetchone()
        
#db functions for getting likes
def get_likes(post_id):
  with get_db_cursor(False) as cur:
    cur.execute("select count(*) from post_likes where post_id = %s", (post_id,))
    counts = cur.fetchone()
    return counts[0]

def get_does_like(post_id, user_id):
  with get_db_cursor(False) as cur:
    cur.execute("select count(*) from post_likes where post_id = %s and user_id=%s", (post_id,user_id))
    counts = cur.fetchone()
    return counts[0]!=0

def like_post(post_id, user_id):
  with get_db_cursor(True) as cur:
    cur.execute("""insert into post_likes (post_id, user_id) values (%s, %s) 
                   on conflict do nothing""" , (post_id, user_id,))
        
def increment_likes(post_id):
  with get_db_cursor(True) as cur:
    cur.execute("""update posts 
                   set likes = likes+1
                   where id=%s""",
                   (post_id,))

def unlike_post(post_id, user_id):
  with get_db_cursor(True) as cur:
    cur.execute("""delete from post_likes where post_id=%s and user_id = %s""" , (post_id, user_id,))

def decrement_likes(post_id):
  with get_db_cursor(True) as cur:
    cur.execute("""update posts
                   set likes = likes-1
                   where id=%s""",
                   (post_id,))

def get_post_by_id(post_id):
  with get_db_cursor(True) as cur:
    cur.execute("SELECT * FROM posts WHERE id = %s", (post_id,))
    return cur.fetchone()
    
def delete_post(post_id):
  with get_db_cursor(True) as cur:
    cur.execute("delete from posts where id = %s", (post_id,))

def delete_all_likes(post_id):
  with get_db_cursor(True) as cur:
    cur.execute("delete from post_likes where post_id=%s", (post_id,))
    
def search_full_text_content(query, page=0, limit=5):
  with get_db_cursor(False) as cur:
    cur.execute("""select * from posts 
                   WHERE to_tsvector('english', raw_text) @@ plainto_tsquery('english', %s)
                   order by ts_rank(to_tsvector('english', raw_text), plainto_tsquery('english', %s)) desc
                   limit %s offset %s""",
                   (query, query, limit, limit*page))
    return cur.fetchall()
    
def get_full_text_search_count(query):
  with get_db_cursor(False) as cur:
    cur.execute("""select count(*) from posts
                   where to_tsvector('english', raw_text) @@ plainto_tsquery('english', %s)""",
                   (query,))
    return cur.fetchone()
    
def search_post_type_full_text_content(query, post_type, page=0, limit=5):
  with get_db_cursor(False) as cur:
    cur.execute("""select * from posts
                   WHERE to_tsvector('english', raw_text) @@ plainto_tsquery('english', %s)
                   AND lower(post_type) = %s
                   order by ts_rank(to_tsvector('english', raw_text), plainto_tsquery('english', %s)) desc
                   limit %s offset %s""",
                   (query, post_type, query, limit, limit*page))
    return cur.fetchall()
    
def get_post_type_full_text_search_count(query, post_type):
  with get_db_cursor(False) as cur:
    cur.execute("""select count(*) from posts
                   WHERE to_tsvector('english', raw_text) @@ plainto_tsquery('english', %s)
                   AND lower(post_type) = %s""",
                   (query, post_type))
    return cur.fetchone()
    
def search_category_full_text_content(query, category, page=0, limit=5):
  with get_db_cursor(False) as cur:
    cur.execute("""select * from posts
                   WHERE to_tsvector('english', raw_text) @@ plainto_tsquery('english', %s)
                   AND lower(category) = %s
                   order by ts_rank(to_tsvector('english', raw_text), plainto_tsquery('english', %s)) desc
                   limit %s offset %s""",
                   (query, category, query, limit, limit*page))
    return cur.fetchall()
    
def get_category_full_text_search_count(query, category):
  with get_db_cursor(False) as cur:
    cur.execute("""select count(*) from posts
                   WHERE to_tsvector('english', raw_text) @@ plainto_tsquery('english', %s)
                   AND lower(category) = %s""",
                   (query, category))
    return cur.fetchone()
    
def search_user_name_and_bio(query, page=0, limit=5):
  with get_db_cursor(False) as cur:
    like_query = "%" + query + "%"
    cur.execute("""select * from users
                   WHERE to_tsvector('english', bio) @@ plainto_tsquery('english', %s)
                   OR lower(username) like %s
                   order by ts_rank(to_tsvector('english', bio), plainto_tsquery('english', %s)) desc
                   limit %s offset %s""",
                   (query, like_query, query, limit, limit*page))
    return cur.fetchall()
    
def get_user_name_and_bio_search_count(query):
  with get_db_cursor(False) as cur:
    like_query = "%" + query + "%"
    cur.execute("""select count(*) from users
                   WHERE to_tsvector('english', bio) @@ plainto_tsquery('english', %s)
                   OR lower(username) like %s""",
                   (query, like_query))
    return cur.fetchone()

def get_comments_by_post_id(post_id):
  with get_db_cursor(True) as cur:
    cur.execute("SELECT * FROM post_comments WHERE post_id = %s", (post_id,))
    return cur.fetchall()
    
def get_num_comments_by_post_id(post_id):
  with get_db_cursor(True) as cur:
    cur.execute("SELECT count(*) FROM post_comments WHERE post_id=%s", (post_id,))
    return cur.fetchone()

def get_category_by_name(name):
  with get_db_cursor(True) as cur:
    cur.execute("SELECT * FROM category WHERE title = %s", (name,))
    return cur.fetchone()   

def set_raw_text(post_id, raw_text):
  with get_db_cursor(True) as cur:
    cur.execute("update posts set raw_text = %s where id = %s",
                 (raw_text, post_id))   
 
def add_comment( user_id, post_id, content):
  with get_db_cursor(True) as cur:
    cur.execute("INSERT INTO post_comments (user_id, post_id, content) values (%s, %s, %s)", (user_id, post_id, content))

def update_post(updatedPost, id):
  with get_db_cursor(True) as cur:
    cur.execute('update posts set content=%s where id=%s',(updatedPost, id,))

def get_all_posts(type="POST"):
  with get_db_cursor(False) as cur:
    cur.execute("""select title, category, thumbnail FROM posts
                   WHERE post_type=%s order by title asc""", 
                   (type,))
    return cur.fetchall()
    
def get_all_posts_by_category(category, type="POST"):
  with get_db_cursor(False) as cur:
    cur.execute("""select title, category, thumbnail FROM posts
                   WHERE post_type=%s AND lower(category)=%s
                   ORDER by title asc""",
                   (type, category))
    return cur.fetchall()
    
def delete_tags(post_id):
  with get_db_cursor(True) as cur:
    cur.execute("delete from tags where post_id=%s",
                 (post_id,))

def add_post_to_tags(tag, post_id):
  with get_db_cursor(True) as cur:
    cur.execute("""insert into tags (tag, post_id) values (%s, %s)""",
                   (tag, post_id))

def get_all_unique_tags():
  with get_db_cursor(False) as cur:
    cur.execute("""select distinct tags.tag, posts.category
                   from posts
                   inner join tags on posts.id=tags.post_id
                   order by posts.category""")
    return cur.fetchall()

def get_unique_tags_by_category(category):
  with get_db_cursor(False) as cur:
    cur.execute("""select distinct tags.tag
                   from posts
                   inner join tags on posts.id=tags.post_id
                   where category=%s""",
                   (category,))
    return cur.fetchall()
    
def get_posts_by_tag_and_category(tag, category, limit=5, page=0):
  with get_db_cursor(False) as cur:
    cur.execute("""select posts.title, posts.raw_text, posts.thumbnail
                   from posts
                   inner join tags on posts.id=tags.post_id
                   where lower(tag)=%s and lower(category)=%s
                   limit %s offset %s""",
                   (tag, category, limit, limit*page))
    return cur.fetchall()
    
def get_count_by_tag_and_category(tag, category):
  with get_db_cursor(False) as cur:
    cur.execute("""select count(*) from posts
                   inner join tags on posts.id=tags.post_id
                   where lower(tag)=%s and lower(category)=%s""",
                   (tag, category))
    return cur.fetchone()
    
# This may be excessive, but I just want to make sure we get the correct id back.
def get_post_id_by_info(user_id, title, raw_text, category, post_type="POST"):
  with get_db_cursor(False) as cur:
    cur.execute("""select id from posts
                   where user_id=%s and title=%s and raw_text=%s and category=%s and post_type=%s""",
                   (user_id, title, raw_text, category, post_type))
    return cur.fetchone()
    
def get_top_contributors_by_category(category, limit=5):
  with get_db_cursor(False) as cur:
    cur.execute("""select user_id from posts
                   where lower(category)=%s
                   group by user_id order by count(user_id) desc limit %s""",
                   (category, limit))
    return cur.fetchall()
    
def get_trending_tags(type='POST', limit=5):
  with get_db_cursor(False) as cur:
    cur.execute("""select posts.category, tags.tag, count(*)
                   from posts
                   inner join tags on posts.id=tags.post_id
                   where posts.post_type=%s
                   group by posts.category, tags.tag order by count desc limit %s""",
                   (type, limit))
    return cur.fetchall()
    
def get_trending_posts(category, type='POST', limit=5):
  with get_db_cursor(False) as cur:
    cur.execute("""select title, thumbnail, likes
                   from posts
                   where lower(category)=%s and post_type=%s
                   order by likes desc limit %s""",
                   (category, type, limit))
    return cur.fetchall()