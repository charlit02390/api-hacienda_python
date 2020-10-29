use jack_api_hacienda;

-- ------------------------------------------------------
-- Table message --
-- ------------------------------------------------------
DROP TABLE IF EXISTS `message`;
CREATE TABLE `message` (
	`id` INT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
	`company_id` INT NOT NULL,
	`key_mh` VARCHAR(50) NOT NULL,
	`status` VARCHAR(30) NOT NULL,
	`code` VARCHAR(1) NOT NULL,
	`issue_date` DATETIME NOT NULL,
	`issuer_idn_num` VARCHAR(15) NOT NULL,
	`issuer_idn_type` VARCHAR(10) NOT NULL,
	`issuer_email` VARCHAR(128),
	`recipient_idn` VARCHAR(15) NOT NULL,
	`recipient_seq_number` VARCHAR(20) NOT NULL,
	`signed_xml` BLOB NOT NULL,
	`answer_date` DATETIME,
	`answer_xml` BLOB
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
ALTER TABLE `message` ADD CONSTRAINT `UQ_message` UNIQUE(key_mh);
ALTER TABLE `message` ADD CONSTRAINT `FK_message_companies` FOREIGN KEY (`company_id`) REFERENCES `companies` (`id`);
-- ------------------------------------------------------
