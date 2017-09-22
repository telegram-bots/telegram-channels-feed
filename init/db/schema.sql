-- Global functions
CREATE OR REPLACE FUNCTION update_updated_at()
  RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ language 'plpgsql';

-- Autoincrement ID
CREATE SEQUENCE IF NOT EXISTS channel_id_seq;
-- Table
CREATE TABLE IF NOT EXISTS channels (
  id           INT PRIMARY KEY DEFAULT nextval('channel_id_seq'),
  telegram_id  INT UNIQUE,
  hash         BIGINT,
  url          VARCHAR(32) UNIQUE      NOT NULL,
  name         VARCHAR(255)            NOT NULL,
  last_post_id INT,
  last_sent_id INT,
  created_at   TIMESTAMP DEFAULT now() NOT NULL,
  updated_at   TIMESTAMP DEFAULT now() NOT NULL
);
-- Indexes
CREATE INDEX IF NOT EXISTS url_index
  ON channels (url);
-- Triggers
DROP TRIGGER IF EXISTS channels_updated_at
ON channels;
CREATE TRIGGER channels_updated_at
BEFORE UPDATE ON channels
FOR EACH ROW
EXECUTE PROCEDURE update_updated_at();

-- Autoincrement ID
CREATE SEQUENCE IF NOT EXISTS user_id_seq;
-- Table
CREATE TABLE IF NOT EXISTS users (
  id           INT PRIMARY KEY DEFAULT nextval('user_id_seq'),
  telegram_id  BIGINT                  NOT NULL UNIQUE,
  redirect_url VARCHAR(32),
  created_at   TIMESTAMP DEFAULT now() NOT NULL,
  updated_at   TIMESTAMP DEFAULT now() NOT NULL
);
-- Triggers
DROP TRIGGER IF EXISTS users_updated_at
ON users;
CREATE TRIGGER users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE PROCEDURE update_updated_at();

-- Table
CREATE TABLE IF NOT EXISTS subscriptions (
  user_id      INT                     NOT NULL REFERENCES users (id) ON DELETE CASCADE,
  channel_id   INT                     NOT NULL REFERENCES channels (id) ON DELETE CASCADE,
  last_sent_id INT,
  created_at   TIMESTAMP DEFAULT now() NOT NULL,
  updated_at   TIMESTAMP DEFAULT now() NOT NULL,
  CONSTRAINT u_ch_constraint UNIQUE (user_id, channel_id)
);
-- Triggers
DROP TRIGGER IF EXISTS subscriptions_updated_at
ON subscriptions;
CREATE TRIGGER subscriptions_updated_at
BEFORE UPDATE ON subscriptions
FOR EACH ROW
EXECUTE PROCEDURE update_updated_at();
