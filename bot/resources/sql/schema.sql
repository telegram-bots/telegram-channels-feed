CREATE SEQUENCE IF NOT EXISTS channel_id_seq;
CREATE TABLE IF NOT EXISTS Channels (
  id              INT PRIMARY KEY NOT NULL DEFAULT nextval('channel_id_seq'),
  telegram_id     BIGINT          NOT NULL UNIQUE,
  url             VARCHAR(32)     NOT NULL,
  name            VARCHAR(255)    NOT NULL,
  last_message_id BIGINT
);
CREATE INDEX IF NOT EXISTS url_index
  ON Channels (url);

CREATE SEQUENCE IF NOT EXISTS user_id_seq;
CREATE TABLE IF NOT EXISTS Users (
  id           INT PRIMARY KEY NOT NULL DEFAULT nextval('user_id_seq'),
  telegram_id  BIGINT          NOT NULL UNIQUE,
  redirect_url VARCHAR(32)
);

CREATE TABLE IF NOT EXISTS Subscriptions (
  user_id         INT NOT NULL,
  channel_id      INT NOT NULL,
  last_message_id BIGINT,
  CONSTRAINT u_ch_constraint UNIQUE (user_id, channel_id)
);
