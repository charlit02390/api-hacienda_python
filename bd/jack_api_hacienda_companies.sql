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
-- Table structure for table `companies`
--

DROP TABLE IF EXISTS `companies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `companies` (
  `id` int NOT NULL AUTO_INCREMENT,
  `company_user` varchar(45) DEFAULT NULL,
  `name` varchar(100) DEFAULT NULL,
  `tradename` varchar(100) DEFAULT NULL,
  `type_identification` varchar(2) DEFAULT NULL,
  `identification_dni` varchar(45) DEFAULT NULL,
  `state` varchar(45) DEFAULT NULL,
  `county` varchar(45) DEFAULT NULL,
  `district` varchar(45) DEFAULT NULL,
  `neighborhood` varchar(45) DEFAULT NULL,
  `address` varchar(100) DEFAULT NULL,
  `code_phone` int DEFAULT NULL,
  `phone` int DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `activity_code` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=40 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `companies`
--

LOCK TABLES `companies` WRITE;
/*!40000 ALTER TABLE `companies` DISABLE KEYS */;
INSERT INTO `companies` VALUES (29,'08089','Jossy Mejia','Jacks','01','207790754','03','07','01','03','San Rafael',506,70113110,'yoz08@gmail.com','289304'),(31,'0808878','Corin Mejia ','UNED','01','206660666','03','07','01','03','San Rafael',506,70113110,'yoz08@gmail.com','289304'),(32,'999','Corin Mejia ','UNED','01','206660666','03','07','01','03','San Rafael',506,70113110,'yoz08@gmail.com','289304'),(33,'998','Corin Mejia ','UNED','01','206660666','03','07','01','03','San Rafael',506,70113110,'yoz08@gmail.com','289304'),(34,'99888','Corin Mejia ','UNED','01','206660666','03','07','01','03','San Rafael',506,70113110,'yoz08@gmail.com','289304'),(35,'8','Corin Mejia ','UNED','01','206660666','03','07','01','03','San Rafael',506,70113110,'yoz08@gmail.com','289304'),(36,'87','Corin Mejia ','UNED','01','206660666','03','07','01','03','San Rafael',506,70113110,'yoz08@gmail.com','289304'),(37,'876','Corin Mejia ','UNED','01','206660666','03','07','01','03','San Rafael',506,70113110,'yoz08@gmail.com','289304'),(38,'87666','Angel','UNED','01','206660666','03','07','01','03','San Rafael',506,70113110,'yoz08@gmail.com','289304'),(39,'12','angelica araya','UNED','01','206660666','03','07','01','03','San Rafael',506,70113110,'yoz08@gmail.com','289304');
/*!40000 ALTER TABLE `companies` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-03-09 18:49:33
