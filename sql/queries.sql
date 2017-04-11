-- 1. сохранить telegram_id пользователя и name канала
-- приходит три параметра: user telegram_id, channel telegram_id и channel name

INSERT INTO Channels (name, telegram_id, last_update)
VALUES ('%some_channel_name%', '%given_telegram_id%', now())
WHERE NOT EXISTS (
        SELECT 1
        FROM Channels
        WHERE telegram_id = '%given_telegram_id%'
        AND name = '%some_channel_name%');

INSERT INTO Subscriptions (user_id, channel_id, last_update)
SELECT Users.id, Channels.id, now()
FROM Users, Channels
WHERE Users.telegram_id = '%given_telegram_id%'
    AND Channels.telegram_id = '%given_telegram_id%';

-- 2. удалить пользователя и все его подписки по его telegram_id
DELETE FROM Subscriptions USING Users
WHERE Subscriptions.user_id = Users.id
    AND Users.telegram_id = '%given_user_tg_id%';

DELETE FROM Users
WHERE telegram_id = '%given_user_tg_id%';

-- 3. удалить одну подписку по name канала у конкретного пользователя по его telegram_id
DELETE FROM Subscriptions USING Channels, Users
WHERE Subscriptions.channel_id = Channels.id
AND Channels.name = '%some_channel_name%'
AND Subscriptions.user_id = Users.id
AND Users.telegram_id = '%given_user_tg_id';

-- 4. найти и вернуть все подписки пользователя по его telegram_id или пустой список
SELECT Channels.id, Channels.name, Channels.telegram_id
FROM Channels
    JOIN Subscriptions ON Channels.id=Subscriptions.channel_id
    JOIN Users ON Subscriptions.user_id=Users.id
WHERE Users.telegram_id = '%given_user_tg_id%';

-- 5. найти всех пользователей подписанных на канал по его name
SELECT Users.id, Users.telegram_id
FROM Users
    JOIN Subscriptions ON Users.id=Subscriptions.user_id
    JOIN Channels ON Subscriptions.channel_id=Channels.id
WHERE Channels.name = '%some_channel_name%';

