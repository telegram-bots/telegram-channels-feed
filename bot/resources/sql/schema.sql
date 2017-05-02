CREATE TABLE IF NOT EXISTS Channels (
  id          INT PRIMARY KEY NOT NULL,
  telegram_id BIGINT          NOT NULL,
  url         VARCHAR         NOT NULL,
  name        VARCHAR         NOT NULL,
  last_update TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Users (
  id          INT PRIMARY KEY NOT NULL,
  telegram_id BIGINT          NOT NULL
);

CREATE TABLE IF NOT EXISTS Subscriptions (
  user_id     INT NOT NULL,
  channel_id  INT NOT NULL,
  last_update TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Notifications (
  channel_telegram_id BIGINT NOT NULL,
  message_id          BIGINT NOT NULL,
  raw                 JSON   NOT NULL
);

CREATE OR REPLACE FUNCTION NotifyEvent()
  RETURNS TRIGGER AS $$

DECLARE
  data         JSON;
  notification JSON;

BEGIN
  -- Convert the old or new row to JSON, based on the kind of action.
  -- Action = DELETE?             -> OLD row
  -- Action = INSERT or UPDATE?   -> NEW row
  IF (TG_OP = 'DELETE')
  THEN
    data = row_to_json(OLD);
  ELSE
    data = row_to_json(NEW);
  END IF;

  -- Construct the notification as a JSON string.
  notification = json_build_object(
      'table', TG_TABLE_NAME,
      'action', TG_OP,
      'data', data
  );

  -- Execute pg_notify(channel, notification)
  PERFORM pg_notify('events', notification :: TEXT);

  -- Result is ignored since this is an AFTER trigger
  RETURN NULL;
END;

$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS Notifications
ON Notifications;
CREATE TRIGGER Notifications
AFTER INSERT ON Notifications
FOR EACH ROW EXECUTE PROCEDURE NotifyEvent();
