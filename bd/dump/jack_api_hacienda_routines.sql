-- MySQL dump 10.13  Distrib 5.7.17, for macos10.12 (x86_64)
--
-- Host: localhost    Database: jack_api_hacienda
-- ------------------------------------------------------
-- Server version	8.0.11

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Temporary view structure for view `vw_cabysxsac`
--

DROP TABLE IF EXISTS `vw_cabysxsac`;
/*!50001 DROP VIEW IF EXISTS `vw_cabysxsac`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE VIEW `vw_cabysxsac` AS SELECT 
 1 AS `code`,
 1 AS `Codigo SAC`,
 1 AS `Descripcion Cabys`,
 1 AS `cantidad_codigos_cabys_sac`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `vw_message`
--

DROP TABLE IF EXISTS `vw_message`;
/*!50001 DROP VIEW IF EXISTS `vw_message`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE VIEW `vw_message` AS SELECT 
 1 AS `id`,
 1 AS `company_id`,
 1 AS `company_user`,
 1 AS `key_mh`,
 1 AS `status`,
 1 AS `code`,
 1 AS `issue_date`,
 1 AS `issuer_idn_num`,
 1 AS `issuer_idn_type`,
 1 AS `issuer_email`,
 1 AS `recipient_idn`,
 1 AS `recipient_seq_number`,
 1 AS `signed_xml`,
 1 AS `answer_date`,
 1 AS `answer_xml`,
 1 AS `company_is_active`,
 1 AS `email_sent`*/;
SET character_set_client = @saved_cs_client;

--
-- Final view structure for view `vw_cabysxsac`
--

/*!50001 DROP VIEW IF EXISTS `vw_cabysxsac`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8 */;
/*!50001 SET character_set_results     = utf8 */;
/*!50001 SET collation_connection      = utf8_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vw_cabysxsac` AS select `ca`.`code` AS `code`,`cs`.`sac_version_2017` AS `Codigo SAC`,`ca`.`description` AS `Descripcion Cabys`,`cs`.`cantidad_codigos_cabys_sac` AS `cantidad_codigos_cabys_sac` from (`cabysxsac` `cs` join `cabys` `ca` on((`cs`.`codigo_cabys_sac` = `ca`.`code`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `vw_message`
--

/*!50001 DROP VIEW IF EXISTS `vw_message`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8 */;
/*!50001 SET character_set_results     = utf8 */;
/*!50001 SET collation_connection      = utf8_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vw_message` AS select `msg`.`id` AS `id`,`msg`.`company_id` AS `company_id`,`cmp`.`company_user` AS `company_user`,`msg`.`key_mh` AS `key_mh`,`msg`.`status` AS `status`,`msg`.`code` AS `code`,`msg`.`issue_date` AS `issue_date`,`msg`.`issuer_idn_num` AS `issuer_idn_num`,`msg`.`issuer_idn_type` AS `issuer_idn_type`,`msg`.`issuer_email` AS `issuer_email`,`msg`.`recipient_idn` AS `recipient_idn`,`msg`.`recipient_seq_number` AS `recipient_seq_number`,`msg`.`signed_xml` AS `signed_xml`,`msg`.`answer_date` AS `answer_date`,`msg`.`answer_xml` AS `answer_xml`,`cmp`.`is_active` AS `company_is_active`,`msg`.`email_sent` AS `email_sent` from (`message` `msg` join `companies` `cmp` on((`msg`.`company_id` = `cmp`.`id`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Dumping events for database 'jack_api_hacienda'
--

--
-- Dumping routines for database 'jack_api_hacienda'
--
/*!50003 DROP PROCEDURE IF EXISTS `sp_CheckUser` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_CheckUser`(
v_email varchar(128),
v_password varchar(50)
)
BEGIN
	Select * from users where email=v_email and password = v_password;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_createCompany` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_createCompany`(
IN v_company_user varchar(45) ,
IN v_name varchar(100),
IN v_tradename varchar(100),
IN v_type_identification varchar(2),
IN v_identification_dni varchar(45),
IN v_state varchar(45),
IN v_county varchar(45),
IN v_district varchar(45),
IN v_neighborhood varchar(45),
IN v_address varchar(255),
IN v_code_phone int,
IN v_phone int,
IN v_email varchar(128),
IN v_activity_code varchar(45),
IN v_is_active tinyint(4)
)
BEGIN

INSERT INTO `jack_api_hacienda`.`companies`
(
`company_user`,
`name`,
`tradename`,
`type_identification`,
`identification_dni`,
`state`,
`county`,
`district`,
`neighborhood`,
`address`,
`code_phone`,
`phone`,
`email`,
`activity_code`,
`is_active`
)
VALUES
(v_company_user ,
v_name,
 v_tradename,
v_type_identification,
v_identification_dni,
v_state,
v_county,
v_district ,
v_neighborhood ,
v_address ,
v_code_phone,
v_phone ,
v_email,
v_activity_code,
v_is_active);

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_createDocumentLineInfo` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_createDocumentLineInfo`(
v_id_company varchar(45),
v_line_number varchar(45),
v_quantity varchar(45),
v_unity varchar(45),
v_detail varchar(150),
v_unit_price varchar(45),
v_net_tax varchar(45),
v_total_line varchar(45),
v_key_mh varchar(50))
BEGIN
DECLARE v_document_id int;
SET v_document_id = (Select id from documents where key_mh = v_key_mh);
IF not exists ( select id from document_line where id_company = v_id_company and
				id_document = v_document_id and
                line_number = v_line_number) then
	INSERT INTO `jack_api_hacienda`.`document_line`
	(
	`id_company`,
	`id_document`,
	`line_number`,
	`quantity`,
	`unity`,
	`detail`,
	`unit_price`,
	`net_tax`,
	`total_line`
	)
	VALUES
	(
	v_id_company,
	v_document_id,
	v_line_number,
	v_quantity,
	v_unity,
	v_detail,
	v_unit_price,
	v_net_tax,
	v_total_line
	);
END IF;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_createDocumentTaxInfo` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_createDocumentTaxInfo`(
v_id_company varchar(45),
v_line_number varchar(45),
v_rate_code varchar(45),
v_code varchar(45),
v_rate varchar(45),
v_ammount varchar(45),
v_key_mh varchar(50))
BEGIN
DECLARE v_document_id int; DECLARE v_document_line_id int;
SET v_document_id = (Select id from documents where key_mh = v_key_mh);
SET v_document_line_id = (Select id from document_line where line_number = v_line_number and id_document = v_document_id);
IF not exists (select id from document_taxes where id_document = v_document_id and
				id_line = v_document_line_id and code = v_code) THEN
	INSERT INTO `jack_api_hacienda`.`document_taxes`
	(
	`id_document`,
	`id_line`,
	`rate_code`,
	`code`,
	`rate`,
	`ammount`
	)
	VALUES
	(
	v_document_id,
	v_document_line_id,
	v_rate_code,
	v_code,
	v_rate,
	v_ammount
	);
END IF;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_createSmtpData` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_createSmtpData`(
v_host varchar(128),
v_user varchar(128),
v_password varchar(128),
v_port varchar(45),
v_encrypt_type varchar(45),
v_id_company varchar(45),
p_sender varchar(128))
BEGIN
INSERT INTO `jack_api_hacienda`.`companies_smtp`
(
`host`,
`user`,
`password`,
`port`,
`encrypt_type`,
`id_company`,
`sender`
)
VALUES
(
v_host,
v_user,
v_password,
v_port,
v_encrypt_type,
(Select id from companies where company_user = v_id_company),
p_sender
);
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_createUser` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_createUser`(
v_email varchar(128),
v_password varchar(45),
v_name varchar(100),
v_idrol int
)
BEGIN
INSERT INTO `jack_api_hacienda`.`users`
(
`email`,
`password`,
`name`,
`idrol`)
VALUES
(
v_email,
v_password,
v_name,
v_idrol
);
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_createUser_Company` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_createUser_Company`(
v_email varchar(128),
v_idcompany int
)
BEGIN
INSERT INTO `jack_api_hacienda`.`users_companies`
(
`iduser`,
`idcompany`
)
VALUES
(
(select u.idusers from users u where u.email = v_email),
v_idcompany
);
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_deleteCompany` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_deleteCompany`(
v_company_id varchar(45))
BEGIN
	DECLARE EXIT HANDLER FOR SQLEXCEPTION
    	BEGIN
        	ROLLBACK;
            RESIGNAL;
        END;

	START TRANSACTION;
		Delete from companies_mh where company_api = (select id from companies where company_user = v_company_id);
		Delete from companies where company_user = v_company_id;
	COMMIT;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_deleteCompanySmtp` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_deleteCompanySmtp`(
v_company_id varchar(45))
BEGIN
	Delete from companies_smtp where id_company = (SELECT c.id from companies c where c.company_user = v_company_id);
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_deleteUser` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_deleteUser`(
v_email varchar(128))
BEGIN
	DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
    	ROLLBACK;
        RESIGNAL;
    END;

	START TRANSACTION;
		Delete from users_companies where iduser = (select idusers from users where email = v_email);
		Delete from users where email = v_email;
    COMMIT;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_deleteUserCompany` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_deleteUserCompany`(
v_email varchar(128),
v_idcompany int
)
BEGIN
	Delete from users_companies where iduser = (select idusers from users where email = v_email)
    and `idcompany` = v_idcompany;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_getCompanies` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_getCompanies`()
BEGIN
Select c.*, mh.user_mh, mh.pass_mh, mh.pin_sig, mh.env, mh.expiration_date
	from companies  c 
    left join companies_mh mh 
		on mh.company_api = c.id ;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_getCompanyInfo` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_getCompanyInfo`(
v_company_id varchar(45))
BEGIN

Select c.*, mh.user_mh, mh.pass_mh, mh.pin_sig, mh.env, mh.expiration_date, CONVERT(mh.logo USING utf8) as logo,  CONVERT(mh.signature USING utf8) as signature
	from companies  c 
    left join companies_mh mh 
		on mh.company_api = c.id 
	where   c.company_user  = v_company_id;

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_getCompanySmtpInfo` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_getCompanySmtpInfo`(
v_company_id varchar(45))
BEGIN

Select c.company_user, csmtp.host, csmtp.user, csmtp.password, csmtp.port, csmtp.encrypt_type, csmtp.sender
	from companies_smtp csmtp 
    inner join companies c
		on c.id = csmtp.id_company
	where   c.company_user  = v_company_id;
    
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_getDocumentByKey` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_getDocumentByKey`(
v_key_mh varchar(50))
BEGIN
	Select cp.company_user, cp.name, d.key_mh, d.status, d.isSent, d.dateanswer, d.datesign, d.document_type, 
d.dni_receiver, d.dni_type_receiver, d.total_document, d.email, d.email_costs, CONVERT(d.signxml USING utf8) signxml,
CONVERT(d.answerxml USING utf8) answerxml , CONVERT(d.pdfdocument USING utf8) as pdfdocument 
from documents d 
inner join companies cp on d.company_id = cp.id  where d.key_mh = v_key_mh;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_getDocumentsConsult` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_getDocumentsConsult`()
BEGIN
Select cp.company_user,  d.key_mh
from documents d 
inner join companies cp on d.company_id = cp.id where d.status = "procesando" limit 20;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_getDocumentsReport` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_getDocumentsReport`(
v_id_company varchar(50),
v_type_document varchar(50)
)
BEGIN
Select cp.company_user, d.key_mh, d.status, d.isSent, d.dateanswer, d.datesign, d.document_type, 
d.dni_receiver, d.dni_type_receiver, d.total_document, d.email, d.email_costs, CONVERT(d.signxml USING utf8) signxml,
CONVERT(d.answerxml USING utf8) answerxml , CONVERT(d.pdfdocument USING utf8) as pdfdocument
from documents d 
inner join companies cp on d.company_id = cp.id  
where cp.company_user= v_id_company 
and d.document_type = v_type_document;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_getDocumentsValidate` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_getDocumentsValidate`()
BEGIN
	Select cp.company_user,  d.key_mh
from documents d 
inner join companies cp on d.company_id = cp.id where d.status = "creado" limit 20;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_getLogoCompany` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_getLogoCompany`(
v_company_id varchar(45))
BEGIN
	Select mh.logo
	from companies_mh mh 
    inner join companies c on c.id = mh.company_api
	where   c.company_user  = v_company_id;

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_getMHInfo` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_getMHInfo`(
v_company_id varchar(45))
BEGIN

Select c.identification_dni, mh.user_mh, mh.pass_mh, mh.signature, mh.pin_sig, mh.env 
	from companies  c 
    inner join companies_mh mh 
		on mh.company_api = c.id 
	where   c.company_user  = v_company_id;

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_getSignCompany` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_getSignCompany`(
v_company_id varchar(45))
BEGIN
	Select mh.signature
	from companies_mh mh 
    inner join companies c on c.id = mh.company_api
	where   c.company_user  = v_company_id;

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_getUserCompany_info` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_getUserCompany_info`(
IN v_email varchar(128),
IN v_idcompany int
)
BEGIN
SELECT uc.*
FROM users_companies uc inner join users u on idusers = iduser
WHERE v_idcompany = uc.idcompany and v_email = u.email; 
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_getUserInfo` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_getUserInfo`(
v_email varchar(128))
BEGIN

select u.*,r.value rol
from users u 
inner join roles r on u.idrol = r.id
where u.email = v_email;

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_getUserInfoCompanies` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_getUserInfoCompanies`(
v_email varchar(128))
BEGIN
select c.id internalid, c.company_user idcompany, c.tradename tradename
from users u 
inner join users_companies uc on u.idusers = uc.iduser
inner join companies c on uc.idcompany = c.id
where u.email = v_email;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_getUsers` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_getUsers`()
BEGIN
	SELECT *
    FROM users u;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_ModifyCompany` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_ModifyCompany`(
IN v_company_user varchar(45) ,
IN v_name varchar(100),
IN v_tradename varchar(100),
IN v_type_identification varchar(2),
IN v_identification_dni varchar(45),
IN v_state varchar(45),
IN v_county varchar(45),
IN v_district varchar(45),
IN v_neighborhood varchar(45),
IN v_address varchar(255),
IN v_code_phone int,
IN v_phone int,
IN v_email varchar(128),
IN v_activity_code varchar(45),
IN v_is_active tinyint(4)
)
BEGIN

UPDATE `jack_api_hacienda`.`companies`
SET
`name` = v_name,
`tradename` = v_tradename,
`type_identification` = v_type_identification,
`identification_dni` = v_identification_dni,
`state`= v_state,
`county` = v_county,
`district` = v_district,
`neighborhood` = v_neighborhood,
`address` = v_address,
`code_phone` = v_code_phone,
`phone`= v_phone,
`email` = v_email,
`activity_code` = v_activity_code,
`is_active` = v_is_active
where `company_user` = v_company_user;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_ModifyCompanySmtp` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_ModifyCompanySmtp`(
v_host varchar(128),
v_user varchar(128),
v_password varchar(128),
v_port varchar(45),
v_encrypt_type varchar(45),
v_id_company varchar(45),
p_sender VARCHAR(128) )
BEGIN
UPDATE `jack_api_hacienda`.`companies_smtp`
SET
`host` = v_host,
`user` = v_user,
`password` = v_password,
`port` = v_port,
`encrypt_type` = v_encrypt_type,
`sender` = p_sender
where `id_company` = (Select id from companies c where c.company_user = v_id_company);
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_modifyMHInfo` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_modifyMHInfo`(
v_user_mh varchar(100),
v_pass_mh varchar(100),
v_signature blob,
v_logo longblob,
v_pin_sig varchar(4),
v_company_api varchar(45),
v_env varchar(45),
v_expiration_date varchar(45) )
BEGIN
UPDATE `jack_api_hacienda`.`companies_mh`
SET
`user_mh` = v_user_mh,
`pass_mh` = v_pass_mh,
`signature` = v_signature,
`logo` = v_logo,
`pin_sig` = v_pin_sig,
`env` = v_env,
`expiration_date` = v_expiration_date
where `company_api` = (Select id from companies c where c.company_user = v_company_api);
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_ModifyUser` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_ModifyUser`(
IN v_email varchar(128),
IN v_password varchar(45),
IN v_name varchar(100),
IN v_idrol int
)
BEGIN
UPDATE `jack_api_hacienda`.`users`
SET
`email` = v_email,
`password` = v_password,
`name` = v_name,
`idrol` = v_idrol
WHERE `email` = v_email;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_saveDocument` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_saveDocument`(
v_company_id varchar(45),
v_key_mh varchar(50),
v_signxml blob,
v_status varchar(80),
v_date datetime,
v_document_type varchar(45),
v_dni_type varchar(10),
v_dni varchar(50),
v_total_document float,
v_total_taxes float,
v_pdf longblob,
v_email varchar(128),
v_email_costs varchar(128)
)
BEGIN
IF not exists (select id from documents where key_mh = v_key_mh) then
	INSERT INTO `jack_api_hacienda`.`documents`
	(
	`company_id`,
	`key_mh`,
	`signxml`,
	`status`,
	`datesign`,
	`document_type`,
	`dni_type_receiver`,
	`dni_receiver`,
	`total_document`,
	`total_taxes`,
	`pdfdocument`,
	`email`,
	`email_costs`)
	VALUES
	(
	(Select id from companies where company_user = v_company_id),
	v_key_mh,
	v_signxml,
	v_status,
	v_date,
	v_document_type,
	v_dni_type,
	v_dni,
	v_total_document,
	v_total_taxes,
	v_pdf,
	v_email,
	v_email_costs);
END IF;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_saveMHInfo` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_saveMHInfo`(
v_user_mh varchar(100),
v_pass_mh varchar(100),
v_signature blob,
v_logo longblob,
v_pin_sig varchar(4),
v_company_api varchar(45),
v_env varchar(45),
v_expiration_date varchar(45)
)
BEGIN
INSERT INTO `jack_api_hacienda`.`companies_mh`
(
`user_mh`,
`pass_mh`,
`signature`,
`logo`,
`pin_sig`,
`company_api`,
`env`,
`expiration_date`)
VALUES
(
v_user_mh,
v_pass_mh,
v_signature,
v_logo,
v_pin_sig,
(Select id from companies where company_user = v_company_api),
v_env,
v_expiration_date
);
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_updateDocument` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_updateDocument`(
v_company_id varchar(45),
v_key_mh varchar(50),
v_answerxml blob,
v_status varchar(80),
v_date datetime
)
BEGIN
UPDATE `jack_api_hacienda`.`documents`
SET
`answerxml` = v_answerxml,
`status` = v_status,
`dateanswer` = v_date
WHERE `key_mh` = v_key_mh and `company_id` = (Select id from companies where company_user = v_company_id) ;
END ;;
DELIMITER ;

DROP PROCEDURE IF EXISTS `usp_updateIsSent_documents`;
DELIMITER $$
CREATE PROCEDURE `usp_updateIsSent_documents` (
	v_key_mh VARCHAR(50),
	v_isSent TINYINT
)
BEGIN
	UPDATE documents
	SET	`isSent` = v_isSent
	WHERE `key_mh` = v_key_mh;
END $$
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `usp_buscar_cabys` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `usp_buscar_cabys`(
    IN p_patron VARCHAR(100)
)
BEGIN
	SELECT `code` AS codigo
    	,description AS descripcion
        ,tax AS impuesto
	FROM cabys
	WHERE CONCAT_WS(' ', `code`, cat8desc, description) REGEXP p_patron;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `usp_buscar_medicamento` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `usp_buscar_medicamento`(
    IN p_patron VARCHAR(100)
)
BEGIN
	SELECT cabyscodigo AS `Codigo Cabys`
    	,msprincipio AS `Principio Activo MS`
        ,atccodigo AS `Codigo ATC`
        ,atcprincipio AS `Principio ATC`
        ,descripcion AS `Descripcion`
   	FROM medicamento
    WHERE CONCAT_WS(' ', msprincipio, atcprincipio, descripcion) REGEXP p_patron;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `usp_deleteUser_CompanyByUser` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `usp_deleteUser_CompanyByUser`(
	IN `p_user_email` VARCHAR(128)
)
BEGIN
	DELETE FROM users_companies WHERE iduser = (SELECT idusers FROM users WHERE email = p_user_email);
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `usp_insert_documentxemail` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `usp_insert_documentxemail`(
	IN `p_key` VARCHAR(50),
	IN `p_email` VARCHAR(128)
)
BEGIN
	DECLARE v_iddoc int;
	SET v_iddoc = (SELECT id FROM documents WHERE key_mh = p_key);
	IF v_iddoc IS NOT NULL THEN
		INSERT INTO documentxemail(
        	iddocument,
        	email
    	)
   		VALUES (
            v_iddoc,
        	p_email
    	);
    END IF;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `usp_obtenerpersona_registrocivil` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `usp_obtenerpersona_registrocivil`(
    p_cedula VARCHAR(9)
)
BEGIN
	SELECT `cedula`,
		`codelec` AS `ubicacion`,
		`expiracion`,
		`nombre`,
		`apellido1`,
		`apellido2`
	FROM `registrocivil`
	WHERE `cedula` = p_cedula;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `usp_obtenersacs_cabysxsac` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `usp_obtenersacs_cabysxsac`(
    p_cod_cabys VARCHAR(13)
)
BEGIN
	SELECT `code` AS `Codigo Cabys`,
		`Codigo SAC`,
    	`Descripcion Cabys`
    FROM vw_cabysxsac
    WHERE `code` = p_cod_cabys;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `usp_selectByDocKey_documentxemail` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `usp_selectByDocKey_documentxemail`(
	IN `p_key` VARCHAR(50)
)
BEGIN
    DECLARE v_iddoc int;
    SET v_iddoc = (SELECT id FROM documents WHERE key_mh = p_key);
    IF v_iddoc IS NOT NULL THEN
    	SELECT email FROM documentxemail WHERE iddocument = v_iddoc;
    END IF;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-11-06 11:57:11

-- ---------------------------------------
-- Messages USPs --------------------
-- ---------------------------------------
DROP PROCEDURE IF EXISTS usp_insert_message;
DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `usp_insert_message` (
	IN `p_company_id` VARCHAR(45),
	IN `p_key_mh` VARCHAR(50),
	IN `p_issuer_idn_num` VARCHAR(15),
	IN `p_issuer_idn_type` VARCHAR(10),
	IN `p_issue_date` DATETIME,
	IN `p_code` VARCHAR(1),
	IN `p_recipient_idn` VARCHAR(15),
	IN `p_recipient_seq_number` VARCHAR(20),
	IN `p_encd_xml` BLOB,
	IN `p_status` VARCHAR(30),
	IN `p_issuer_email` VARCHAR(128)
)
BEGIN
	DECLARE v_idcomp INT;
	SET v_idcomp = (SELECT id from companies WHERE company_user = p_company_id);
	IF v_idcomp IS NOT NULL THEN
		INSERT INTO `message` (
			company_id,
			key_mh,
			status,
			code,
			issue_date,
			issuer_idn_num,
			issuer_idn_type,
			issuer_email,
			recipient_idn,
			recipient_seq_number,
			signed_xml)
		VALUES (
			v_idcomp,
			`p_key_mh`,
			`p_status`,
			`p_code`,
			`p_issue_date`,
			`p_issuer_idn_num`,
			`p_issuer_idn_type`,
			`p_issuer_email`,
			`p_recipient_idn`,
			`p_recipient_seq_number`,
			`p_encd_xml`
		);
	END IF;
END$$
DELIMITER ;


DROP PROCEDURE IF EXISTS usp_updateFromAnswer_message;
DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `usp_updateFromAnswer_message` (
	IN `p_company_user` VARCHAR(45),
	IN `p_key_mh` VARCHAR(50),
	IN `p_recipient_seq_number` VARCHAR(20),
	IN `p_encd_answer_xml` BLOB,
	IN `p_status` VARCHAR(30),
	IN `p_answer_date` DATETIME
)
BEGIN
	DECLARE v_idcomp INT;
	SET v_idcomp = (SELECT id from companies WHERE company_user = `p_company_user`);
	IF v_idcomp IS NOT NULL THEN
		UPDATE `message`
		SET	answer_xml	=	`p_encd_answer_xml`,
			status	=	`p_status`,
			answer_date =	`p_answer_date`
		WHERE	company_id = v_idcomp
			AND	key_mh	=	`p_key_mh`
			AND	recipient_seq_number = `p_recipient_seq_number`;
	END IF;
END$$
DELIMITER ;


DROP PROCEDURE IF EXISTS `usp_updateEmailSent_message`;
DELIMITER $$
CREATE PROCEDURE `usp_updateEmailSent_message` (
	p_key_mh VARCHAR(50),
	p_recipient_seq_number VARCHAR(20),
	p_email_sent TINYINT
)
BEGIN
	UPDATE message
	SET	`email_sent` = p_email_sent
	WHERE `key_mh` = p_key_mh
		AND `recipient_seq_number` = p_recipient_seq_number;
END$$
DELIMITER ;


DROP VIEW IF EXISTS vw_message;
CREATE VIEW `vw_message`
AS
SELECT	msg.id,
	msg.company_id,
	cmp.company_user,
	msg.key_mh,
	msg.status,
	msg.code,
	msg.issue_date,
	msg.issuer_idn_num,
	msg.issuer_idn_type,
	msg.issuer_email,
	msg.recipient_idn,
	msg.recipient_seq_number,
	msg.signed_xml,
	msg.answer_date,
	msg.answer_xml,
	cmp.is_active as company_is_active,
	msg.email_sent
FROM	`message` AS msg INNER JOIN
	companies as cmp ON msg.company_id = cmp.id;


DROP PROCEDURE IF EXISTS usp_select_message;
DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `usp_select_message` (
	IN `p_key_mh` VARCHAR(50),
	IN `p_recipient_seq_number` VARCHAR(20)
)
BEGIN
	SELECT vw_msg.*
	FROM	`vw_message` AS vw_msg
	WHERE	vw_msg.key_mh = p_key_mh
		AND	vw_msg.recipient_seq_number = `p_recipient_seq_number`;
END$$
DELIMITER ;


DROP PROCEDURE IF EXISTS usp_selectByCompany_message;
DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `usp_selectByCompany_message` (
	IN `p_company_user` VARCHAR(50),
	IN `p_limit` INT UNSIGNED
)
BEGIN
	SET @q = 'SELECT v_msg.*	FROM	`vw_message` AS v_msg WHERE v_msg.company_user = ?';
	IF `p_limit` IS NOT NULL THEN
		SET @q = CONCAT(@q, ' LIMIT ', `p_limit`);
	END IF;
	PREPARE stmt FROM @q;
	SET @cmp_user = `p_company_user`;
	EXECUTE stmt USING @cmp_user;
	DEALLOCATE PREPARE stmt;
END$$
DELIMITER ;


DROP PROCEDURE IF EXISTS usp_selectByStatus_message;
DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `usp_selectByStatus_message` (
	IN `p_status` VARCHAR(30),
	IN `p_company_user` VARCHAR(50),
	IN `p_company_is_active` TINYINT UNSIGNED,
	IN `p_limit` INT UNSIGNED
)
BEGIN
	SET @q = 'SELECT v_msg.*	FROM	`vw_message` AS v_msg WHERE v_msg.status = ?';
	IF `p_company_user` IS NOT NULL THEN
		SET @q = CONCAT(@q, ' AND v_msg.company_user = ', `p_company_user`);
	END IF;
	IF `p_company_is_active` IS NOT NULL THEN
		SET @q = CONCAT(@q, ' AND v_msg.company_is_active = ', `p_company_is_active`);
	END IF;
	IF `p_limit` IS NOT NULL THEN
		SET @q = CONCAT(@q, ' LIMIT ', `p_limit`);
	END IF;
	PREPARE stmt FROM @q;
	SET @status = `p_status`;
	EXECUTE stmt USING @status;
	DEALLOCATE PREPARE stmt;
END$$
DELIMITER ;


DROP PROCEDURE IF EXISTS usp_selectByCode_message;
DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `usp_selectByCode_message` (
	IN `p_code` VARCHAR(1),
	IN `p_company_user` VARCHAR(50),
	IN `p_limit` INT UNSIGNED
)
BEGIN
	SET @q = 'SELECT v_msg.*	FROM	`vw_message` AS v_msg WHERE v_msg.code = ?';
	IF `p_company_user` IS NOT NULL THEN
		SET @q = CONCAT(@q, ' AND v_msg.company_user = ', `p_company_user`);
	END IF;
	IF `p_limit` IS NOT NULL THEN
		SET @q = CONCAT(@q, ' LIMIT ', `p_limit`);
	END IF;
	PREPARE stmt FROM @q;
	SET @code = `p_code`;
	EXECUTE stmt USING @code;
	DEALLOCATE PREPARE stmt;
END$$
DELIMITER ;


DROP PROCEDURE IF EXISTS usp_selectByIssuerIDN_message;
DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `usp_selectByIssuerIDN_message` (
	IN `p_issuer_idn_num` VARCHAR(1),
	IN `p_company_user` VARCHAR(50),
	IN `p_limit` INT UNSIGNED
)
BEGIN
	SET @q = 'SELECT v_msg.*	FROM	`vw_message` AS v_msg WHERE v_msg.issuer_idn_num = ?';
	IF `p_company_user` IS NOT NULL THEN
		SET @q = CONCAT(@q, ' AND v_msg.company_user = ', `p_company_user`);
	END IF;
	IF `p_limit` IS NOT NULL THEN
		SET @q = CONCAT(@q, ' LIMIT ', `p_limit`);
	END IF;
	PREPARE stmt FROM @q;
	SET @idn = `p_issuer_idn_num`;
	EXECUTE stmt USING @idn;
	DEALLOCATE PREPARE stmt;
END$$
DELIMITER ;
-- ---------------------------------------

-- ---------------------------------------
DROP PROCEDURE IF EXISTS USP_UpdateCompanyState;
DELIMITER $$
CREATE PROCEDURE USP_UpdateCompanyState(
	p_companyId INT UNSIGNED,
	p_newState BOOLEAN
)
BEGIN
	UPDATE companies
	SET is_active = p_newState
	WHERE id = p_companyId;
END $$
DELIMITER ;
-- ---------------------------------------

-- ---------------------------------------
DROP PROCEDURE IF EXISTS usp_verifyExists_documents;
DELIMITER $$
CREATE PROCEDURE usp_verifyExists_documents(
	p_key_mh VARCHAR(50)
)
BEGIN
	SELECT d.id
	FROM documents as d
	WHERE d.key_mh = p_key_mh;
END $$
DELIMITER ;
-- --------------------------------------
