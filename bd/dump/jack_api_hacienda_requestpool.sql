CREATE TABLE requestpool (
	id TINYINT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
	pool INT UNSIGNED NOT NULL,
	maxpool INT UNSIGNED NOT NULL,
	defaultinterval INT UNSIGNED NOT NULL,
	burstduration INT UNSIGNED NOT NULL,
	burstlimit INT UNSIGNED NOT NULL,
	burstsleep INT UNSIGNED NOT NULL,
	burstbegin TIMESTAMP(6),
	burstend TIMESTAMP(6),
	burstcurrent INT UNSIGNED
);
INSERT INTO requestpool(pool, maxpool, defaultinterval, burstduration, burstlimit, burstsleep)
	VALUES (10, 10, 30, 20, 5, 60);
