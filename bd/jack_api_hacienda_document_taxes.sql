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
-- Table structure for table `document_taxes`
--

DROP TABLE IF EXISTS `document_taxes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `document_taxes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_document` int(11) NOT NULL,
  `id_line` int(11) NOT NULL,
  `rate_code` varchar(45) DEFAULT NULL,
  `code` varchar(45) DEFAULT NULL,
  `rate` varchar(45) DEFAULT NULL,
  `ammount` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `id_document_taxes_fk_idx` (`id_document`),
  KEY `id_line_taxe_fk_idx` (`id_line`),
  CONSTRAINT `id_document_taxes_fk` FOREIGN KEY (`id_document`) REFERENCES `documents` (`id`),
  CONSTRAINT `id_line_taxe_fk` FOREIGN KEY (`id_line`) REFERENCES `document_line` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=51 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `document_taxes`
--
