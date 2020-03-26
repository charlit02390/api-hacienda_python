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
-- Table structure for table `document_line`
--

DROP TABLE IF EXISTS `document_line`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `document_line` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_company` int NOT NULL,
  `id_document` int NOT NULL,
  `line_number` varchar(45) DEFAULT NULL,
  `quantity` varchar(45) DEFAULT NULL,
  `unity` varchar(45) DEFAULT NULL,
  `detail` varchar(45) DEFAULT NULL,
  `unit_price` varchar(45) DEFAULT NULL,
  `net_tax` varchar(45) DEFAULT NULL,
  `total_line` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `id_company_fk_idx` (`id_company`),
  KEY `id_document_fk_idx` (`id_document`),
  CONSTRAINT `id_company_fk2` FOREIGN KEY (`id_company`) REFERENCES `companies` (`id`),
  CONSTRAINT `id_document_fk2` FOREIGN KEY (`id_document`) REFERENCES `documents` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `document_line`
--

LOCK TABLES `document_line` WRITE;
/*!40000 ALTER TABLE `document_line` DISABLE KEYS */;
INSERT INTO `document_line` VALUES (30,32,76,'1','2.000','Unid','SALSA NATURAS HONGOS 106 GR','460.18000','119.64680','1040.00680'),(31,32,77,'1','2.000','Unid','SALSA NATURAS HONGOS 106 GR','460.18000','119.64680','1040.00680'),(32,32,77,'2','2.000','Unid','SALSA NATURAS HONGOS 106 GR','460.18000','119.64680','1040.00680'),(33,32,78,'1','2.000','Unid','SALSA NATURAS HONGOS 106 GR','460.18000','119.64680','1040.00680'),(34,32,78,'2','2.000','Unid','SALSA NATURAS HONGOS 106 GR','460.18000','119.64680','1040.00680'),(35,32,79,'1','2.000','Unid','SALSA NATURAS HONGOS 106 GR','460.18000','119.64680','1040.00680'),(36,32,79,'2','2.000','Unid','SALSA NATURAS HONGOS 106 GR','460.18000','119.64680','1040.00680');
/*!40000 ALTER TABLE `document_line` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-03-26  0:21:07
