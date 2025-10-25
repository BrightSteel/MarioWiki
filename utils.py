import datetime
import math
from html_sanitizer import *
from html.parser import HTMLParser
import db
from os import environ as env

# Retrieve the default sanitizer settings
my_settings = dict(sanitizer.DEFAULT_SETTINGS)

# Add the tags you are interested in allowing.
my_tags = {'h4', 'h5', 'h6', 'u', 's', 'blockquote', 'pre', 'span', 'img'}
my_settings['tags'].update(my_tags)

# Add the allowed attributes for each tag.
my_attributes = {
  'p': ('class', 'style',),
  'span': ('class', 'style',),
  'pre': ('class', 'spellcheck',),
  'img': ('src',),
}
my_settings['attributes'].update(my_attributes)

# Since img is an empty tag, as in it doesn't have a closing tag,
# you must add it to the 'empty' set. Similarly, the sanitizer combines
# sibling tags of the same attribute, which may cause problem for certain
# tags, such as span, so you have to tell the sanitizer to separate span
# tags.
my_settings['empty'].add('img')
my_settings['separate'].add('span')

# Create the sanitizer with our custom settings.
sanitizer = Sanitizer(my_settings)

def get_elapsed_time(timestamp):
  now = datetime.datetime.utcnow() # db stores stamps in UTC so we have to grab time as utc as well
  elapsed = now - timestamp
  d = elapsed.days
  if d > 0:
    return str(d)+"d"
    
  h = elapsed.seconds // 3600
  if h > 0:
    return str(h)+"h"
    
  m = elapsed.seconds // 60 % 60
  if m > 0:
    return str(m)+"m"
    
  s = elapsed.seconds
  return str(s)+"s"

def get_total_pages(post_size, page_size=5):
  pages = post_size/page_size
  pages = math.ceil(pages)
  return pages

# A function to get the next specified h tag.
def get_next_h_tag(src, start, end, h_tag):
  return src.find(h_tag, start, end)

def get_list_of_headers(src):
  h2_start = 0

  headers = []

  # Get the index of the first h2 tag.
  h2_index = get_next_h_tag(src, h2_start, len(src), "<h2>")
  # Loop until no more h2 tags are found.
  while h2_index != -1:
    # Initialize a dictionary for the h2 and nested h3 headers.
    cur_nested_h2 = {
      "h2": (),
      "h3s": []
    }

    # Find the start of the closing h2 tag.
    end_of_h2 = src.find("</h2>", h2_index)
    # Get the contents of the h tag.
    h2_header = src[h2_index:end_of_h2+5]

    # Parse the raw text from the html string h2_header.
    h2_parser = MyHTMLParser()
    h2_parser.feed(h2_header)
    h2_header = h2_parser.rawText

    # Create the id to represent the h tag.
    h2_id_label = h2_header
    if h2_header.find(" ") != -1:
      h2_id_label = h2_header.replace(" ", "_")
    h2_id = ' id="' + h2_id_label + '"'
    h2_class = ' class="h2_tag"'
    h2_id_class = h2_id + h2_class

    # Update the src content to include the id.
    src = src[:h2_index+3] + h2_id_class + src[h2_index+3:]
    h2_start = src.find("</h2>", h2_index)

    # Add the header data to the nested_h2 list.
    cur_h2 = (h2_header, h2_id_label, h2_index)
    cur_nested_h2["h2"] = cur_h2

    # Find the next h2 tag so that we know when to stop searching for nested h3 tags.
    next_h2 = get_next_h_tag(src, h2_start, len(src), "<h2>")
    if next_h2 == -1:
      next_h2 = len(src)

    # Start searching for nested h3 tags here.
    h3_index = get_next_h_tag(src, h2_index, next_h2, "<h3>")
    # Loop until no more h3 tags are found.
    while h3_index != -1:
      # Initialize a dictionary for the h3 and nested h4 headers.
      cur_nested_h3 = {
        "h3": (),
        "h4s": []
      }

      # Find the start of the closing h3 tag.
      end_of_h3 = src.find("</h3>", h3_index)
      # Get the contents of the h tag.
      h3_header = src[h3_index:end_of_h3+5]

      # Parse the raw text from the html string h3_header.
      h3_parser = MyHTMLParser()
      h3_parser.feed(h3_header)
      h3_header = h3_parser.rawText

      # Create the id to represent the h tag.
      h3_id_label = h3_header
      if h3_header.find(" ") != -1:
        h3_id_label = h3_header.replace(" ", "_")
      h3_id = ' id="' + h3_id_label + '"'
      h3_class = ' class="h3_tag"'
      h3_id_class = h3_id + h3_class

      # Update the src content to include the id.
      src = src[:h3_index+3] + h3_id_class + src[h3_index+3:]
      h3_start = src.find("</h3>", h3_index+4)

      # Add the header data to the nested_h3 list.
      cur_h3 = (h3_header, h3_id_label, h3_index)
      cur_nested_h3["h3"] = cur_h3

      # Find the next h3 tag so that we know when to stop searching for nested h4 tags.
      next_h3 = get_next_h_tag(src, h3_start, len(src), "<h3>")
      if next_h3 == -1:
        next_h3 = len(src)

      # Start searching for nested h4 tags here.
      h4_index = get_next_h_tag(src, h3_index, next_h3, "<h4>")
      # Loop until no more h4 tags are found.
      while h4_index != -1:
        # Find the start of the closing h4 tag.
        end_of_h4 = src.find("</h4>", h4_index)
        # Get the contents of the h tag.
        h4_header = src[h4_index:end_of_h4+5]

        # Parse the raw text from the html string h4_header.
        h4_parser = MyHTMLParser()
        h4_parser.feed(h4_header)
        h4_header = h4_parser.rawText

        # Create the id and class to represent the h tag.
        h4_id_label = h4_header
        if h4_header.find(" ") != -1:
          h4_id_label = h4_header.replace(" ", "_")
        h4_id = ' id="' + h4_id_label + '"'
        h4_class = ' class="h4_tag"'
        h4_id_class = h4_id + h4_class

        # Update the src content to include the id.
        src = src[:h4_index+3] + h4_id_class + src[h4_index+3:]
        h4_start = src.find("</h4>", h4_index+4)

        # Add the header data to the nested_h3 list.
        cur_h4 = (h4_header, h4_id_label, h4_index)

        # Add the current nested h4 tag to the cur_nested_h3 dictionary.
        cur_nested_h3["h4s"].append(cur_h4)

        # Get the next h3 tag again because the length of the src may have been adjusted
        # by the addition of adding ids to h4 tags.
        next_h3 = get_next_h_tag(src, h3_start, len(src), "<h3>")
        if next_h3 == -1:
          next_h3 = len(src)
        # Get the index of the next h4 tag.
        h4_index = get_next_h_tag(src, h4_start, next_h3, "<h4>")

      # Add the current nested h3 to the cur_nested_h2 dictionary.
      cur_nested_h2["h3s"].append(cur_nested_h3)

      # Get the next h2 tag again because the length of the src may have been adjusted
      # by the addition of adding ids to h3 tags.
      next_h2 = get_next_h_tag(src, h2_start, len(src), "<h2>")
      if next_h2 == -1:
        next_h2 = len(src)
      # Get the index of the next h3 tag.
      h3_index = get_next_h_tag(src, h3_start, next_h2, "<h3>")

    # Add the current nested h2 to the list of headers.
    headers.append(cur_nested_h2)
    # Get the index of the next h2 tag.
    h2_index = get_next_h_tag(src, h2_start, len(src), "<h2>")

  # Return the updated src and the list of headers.
  return (src, headers)

def add_class_to_imgs(src):
  img_start = 0
  img_index = src.find("<img", img_start)
  while img_index != -1:
    insert_here = img_index + 4
    img_class = ' class="post_img"'
    src = src[:insert_here] + img_class + src[insert_here:]

    img_start = insert_here
    img_index = src.find("<img", img_start)

  return src

def get_a_to_z_dicts(all_posts):
  # Initialize dicts for the browse a-z section.
  num_h_dict = {
    "#": [], "A": [], "B": [], "C": [], "D": [], "E": [], "F": [], "G": [], "H": []
  }

  i_q_dict = {
    "I": [], "J": [], "K": [], "L": [], "M": [], "N": [], "O": [], "P": [], "Q": []
  }

  r_z_dict = {
    "R": [], "S": [], "T": [], "U": [], "V": [], "W": [], "X": [], "Y": [], "Z": []
  }

  all_posts_dict = []
  for post in all_posts:
    cur_post = {
      "title": post[0],
      "category": post[1],
      "thumbnail": post[2]
    }
    all_posts_dict.append(cur_post)

  for post in all_posts_dict:
    first_letter = post["title"][0].upper()
    if first_letter < "A":
      num_h_dict["#"].append(post)
    elif first_letter >= "A" and first_letter <= "H":
      num_h_dict[first_letter].append(post)
    elif first_letter >= "I" and first_letter <= "Q":
      i_q_dict[first_letter].append(post)
    elif first_letter >= "R" and first_letter <= "Z":
      r_z_dict[first_letter].append(post)

  a_z_dicts = {
    "num_h": num_h_dict,
    "i_q": i_q_dict,
    "r_z": r_z_dict
  }
  return a_z_dicts

def get_unique_tags():
  character_tags = db.get_unique_tags_by_category("Characters")
  games_tags = db.get_unique_tags_by_category("Games")
  content_tags = db.get_unique_tags_by_category("Content")

  tags = {
    "characters": character_tags,
    "games": games_tags,
    "content": content_tags
  }

  return tags

class MyHTMLParser(HTMLParser):
  rawText = ""
  # Override how we want the parser to handle data.
  def handle_data(self, data):
    self.rawText += data

logo_url=env['LOGO_IMG']
favicon_url=env['FAV']
error_url=env['ERR']
loading_url=env['LOADING']