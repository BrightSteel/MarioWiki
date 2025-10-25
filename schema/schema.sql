-- Create an index to speed up our full text search --
CREATE INDEX raw_text_search_idx on posts USING GIN (to_tsvector('english', raw_text));

-- refers to either a main post or a discussion post --
CREATE TABLE posts(
    id SERIAL,
    user_id VARCHAR(128) NOT NULL,
    title VARCHAR(64) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(64) NOT NULL, 
    post_date TIMESTAMP NOT NULL default CURRENT_TIMESTAMP,
    post_type VARCHAR(16) NOT NULL, -- either POST or DISCUSSION --
    likes INT NOT NULL DEFAULT 0,
    raw_text TEXT NOT NULL,
    thumbnail VARCHAR(128) NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE post_comments(
    id SERIAL NOT NULL,
    user_id VARCHAR(128) NOT NULL,
    post_id INT NOT NULL,
    content TEXT NOT NULL,
    post_date TIMESTAMP NOT NULL default CURRENT_TIMESTAMP,
    revision_date TIMESTAMP,
    likes INT NOT NULL DEFAULT 0,
    PRIMARY KEY (id)
);

CREATE TABLE category(
    title VARCHAR(64) NOT NULL,
    description TEXT,
    photo VARCHAR(256),
    PRIMARY KEY (title)
);

CREATE TABLE users(
    user_id VARCHAR(128) NOT NULL,
    username VARCHAR(32) NOT NULL, --will need to enforce uniqueness--
    photo_url VARCHAR(256),
    bio TEXT,
    PRIMARY KEY (user_id)
);

CREATE TABLE user_followers(
    user_id VARCHAR(128) NOT NULL,
    follower_id VARCHAR(128) NOT NULL,
    PRIMARY KEY (user_id, follower_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE post_likes(
    post_id INT NOT NULL,
    user_id VARCHAR(128) NOT NULL,
    PRIMARY KEY (post_id, user_id),
    FOREIGN KEY (post_id) REFERENCES posts(id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE tags(
    tag VARCHAR(64),
    post_id INT,
    PRIMARY KEY (tag, post_id),
    FOREIGN KEY (post_id) REFERENCES posts(id)
);
