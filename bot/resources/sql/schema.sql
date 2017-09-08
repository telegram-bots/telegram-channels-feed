CREATE SEQUENCE IF NOT EXISTS channel_id_seq;
CREATE TABLE IF NOT EXISTS Channels (
  id           INT PRIMARY KEY DEFAULT nextval('channel_id_seq'),
  telegram_id  INT UNIQUE,
  hash         BIGINT,
  url          VARCHAR(32) UNIQUE NOT NULL,
  name         VARCHAR(255)       NOT NULL,
  last_post_id INT,
  last_sent_id INT
);
CREATE INDEX IF NOT EXISTS url_index
  ON Channels (url);

CREATE SEQUENCE IF NOT EXISTS user_id_seq;
CREATE TABLE IF NOT EXISTS Users (
  id           INT PRIMARY KEY DEFAULT nextval('user_id_seq'),
  telegram_id  BIGINT NOT NULL UNIQUE,
  redirect_url VARCHAR(32)
);

CREATE TABLE IF NOT EXISTS Subscriptions (
  user_id      INT NOT NULL REFERENCES users (id) ON DELETE CASCADE,
  channel_id   INT NOT NULL REFERENCES channels (id) ON DELETE CASCADE,
  last_sent_id INT,
  CONSTRAINT u_ch_constraint UNIQUE (user_id, channel_id)
);
