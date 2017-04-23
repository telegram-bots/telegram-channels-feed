CREATE TABLE IF NOT EXISTS Channels (
    id int primary key not null,
    name char(50) not null,
    telegram_id bigint not null
);

CREATE TABLE IF NOT EXISTS Users (
    id int primary key not null,
    telegram_id bigint not null
);

CREATE TABLE IF NOT EXISTS Subscriptions (
    user_id int not null,
    channel_id int not null,
    last_update timestamp
);

CREATE TABLE IF NOT EXISTS NewsQueue (
    channel_telegram_id bigint not null,
    payload json not null
);
