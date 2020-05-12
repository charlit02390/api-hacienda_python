-- MySQL dump 10.13  Distrib 8.0.18, for Win64 (x86_64)
--
-- Host: localhost    Database: jack_api_hacienda
-- ------------------------------------------------------
-- Server version	8.0.18

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `documents`
--

DROP TABLE IF EXISTS `documents`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `documents` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `company_id` int(11) DEFAULT NULL,
  `key_mh` varchar(50) DEFAULT NULL,
  `signxml` blob,
  `answerxml` blob,
  `status` varchar(80) DEFAULT NULL,
  `pdfdocument` blob,
  `isSent` tinyint(4) DEFAULT NULL,
  `dateanswer` datetime DEFAULT NULL,
  `datesign` datetime DEFAULT NULL,
  `document_type` varchar(45) DEFAULT NULL,
  `dni_type_receiver` varchar(10) DEFAULT NULL,
  `dni_receiver` varchar(50) DEFAULT NULL,
  `total_document` float DEFAULT NULL,
  `total_taxes` float DEFAULT NULL,
  `email` varchar(45) DEFAULT NULL,
  `email_costs` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FK_company_id_idx` (`company_id`),
  CONSTRAINT `FK_company_id` FOREIGN KEY (`company_id`) REFERENCES `companies` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=80 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `documents`
--
