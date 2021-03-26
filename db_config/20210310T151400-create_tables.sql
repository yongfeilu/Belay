

-- mysql -u root -p < 20210310T151400-create_tables.sql

use yongfeilu;

DROP TABLE IF EXISTS user;
CREATE TABLE user (
	user_id INT AUTO_INCREMENT PRIMARY KEY,
	username VARCHAR(50) NOT NULL,
	useremail VARCHAR(50) NOT NULL,
	password VARCHAR(100) NOT NULL
);

DROP TABLE IF EXISTS channel;
CREATE TABLE channel (
	channel_id INT AUTO_INCREMENT PRIMARY KEY,
	channel_name VARCHAR(100) NOT NULL,
	creater_id INT NOT NULL,
	create_time DATETIME,
	number_of_messages INT NOT NULL,

	FOREIGN KEY(creater_id) REFERENCES user(user_id) ON DELETE CASCADE
);

DROP TABLE IF EXISTS message;
CREATE TABLE message(
	mg_id INT AUTO_INCREMENT PRIMARY KEY,
	body TEXT,
	sender_id INT NOT NULL,
	room_id INT NOT NULL,
	post_time DATETIME,

	FOREIGN KEY(sender_id) REFERENCES user(user_id),
	FOREIGN KEY(room_id) REFERENCES channel(channel_id) ON DELETE CASCADE
);

DROP TABLE IF EXISTS reply;
CREATE TABLE reply(
	original_mg_id INT NOT NULL,
	reply_id INT NOT NULL,

	PRIMARY KEY(original_mg_id, reply_id),
	FOREIGN KEY(original_mg_id) REFERENCES message(mg_id) ON DELETE CASCADE,
	FOREIGN KEY(reply_id) REFERENCES message(mg_id) ON DELETE CASCADE
);

DROP TABLE IF EXISTS last_message;
CREATE TABLE last_message(
	channel_id INT,
	user_id INT,
	last_mg_id INT,
	current_total INT NOT NULL,

	PRIMARY KEY(channel_id, user_id),
	FOREIGN KEY(channel_id) REFERENCES channel(channel_id) ON DELETE CASCADE,
	FOREIGN KEY(user_id) REFERENCES user(user_id) ON DELETE CASCADE,
	FOREIGN KEY(last_mg_id) REFERENCES message(mg_id) ON DELETE CASCADE
);















