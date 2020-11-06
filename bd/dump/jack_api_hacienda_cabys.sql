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
-- Table structure for table `cabys`
--

DROP TABLE IF EXISTS `cabys`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cabys` (
  `cat1` varchar(1) DEFAULT NULL,
  `cat1desc` varchar(1000) DEFAULT NULL,
  `cat2` varchar(2) DEFAULT NULL,
  `cat2desc` varchar(1000) DEFAULT NULL,
  `cat3` varchar(3) DEFAULT NULL,
  `cat3desc` varchar(1000) DEFAULT NULL,
  `cat4` varchar(4) DEFAULT NULL,
  `cat4desc` varchar(1000) DEFAULT NULL,
  `cat5` varchar(5) DEFAULT NULL,
  `cat5desc` varchar(1000) DEFAULT NULL,
  `cat6` varchar(7) DEFAULT NULL,
  `cat6desc` varchar(1000) DEFAULT NULL,
  `cat7` varchar(9) DEFAULT NULL,
  `cat7desc` varchar(1000) DEFAULT NULL,
  `cat8` varchar(11) DEFAULT NULL,
  `cat8desc` varchar(1000) DEFAULT NULL,
  `code` varchar(13) NOT NULL,
  `description` varchar(4000) DEFAULT NULL,
  `tax` tinyint(3) DEFAULT '0',
  PRIMARY KEY (`code`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-11-06 11:57:11
