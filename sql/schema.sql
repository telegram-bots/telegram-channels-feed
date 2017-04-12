CREATE TABLE Channels (
		id int primary key, 
		name char(50), 
		telegram_id int, 
		last_update timestamp
	);


CREATE TABLE Users (
		id int primary key, 
		telegram_id int
	);


CREATE TABLE Subscriptions (
		user_id int, 
		channel_id int, 
		last_update timestamp
	);
