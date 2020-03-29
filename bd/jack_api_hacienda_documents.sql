-- MySQL dump 10.13  Distrib 8.0.19, for Win64 (x86_64)
--
-- Host: localhost    Database: jack_api_hacienda
-- ------------------------------------------------------
-- Server version	8.0.19

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
  `id` int NOT NULL AUTO_INCREMENT,
  `company_id` int DEFAULT NULL,
  `key_mh` varchar(50) DEFAULT NULL,
  `signxml` blob,
  `answerxml` blob,
  `status` varchar(80) DEFAULT NULL,
  `pdfdocument` blob,
  `isSent` tinyint DEFAULT NULL,
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

LOCK TABLES `documents` WRITE;
/*!40000 ALTER TABLE `documents` DISABLE KEYS */;
INSERT INTO `documents` VALUES (76,32,'5069010a0000001011s84573172',NULL,NULL,'creado',NULL,NULL,NULL,'2020-03-25 23:46:18','FE','01','114470760',1040.01,119.647,'cmonge@jackdevelopers.com','hfcrod@gmail.com'),(77,32,'5069010a0a000001011s84573172',NULL,NULL,'creado',NULL,NULL,NULL,'2020-03-25 23:47:06','FE','01','114470760',1040.01,119.647,'cmonge@jackdevelopers.com','hfcrod@gmail.com'),(78,32,'50690s10a0a000001011s84573172',NULL,NULL,'creado',NULL,NULL,NULL,'2020-03-25 23:54:14','FE','01','114470760',1040.01,119.647,'cmonge@jackdevelopers.com','hfcrod@gmail.com'),(79,32,'50690s10a0a000s001011s84573172',NULL,NULL,'creado',NULL,NULL,NULL,'2020-03-26 00:00:17','FE','01','114470760',1040.01,119.647,'cmonge@jackdevelopers.com','hfcrod@gmail.com');
/*!40000 ALTER TABLE `documents` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-03-28 22:14:33
