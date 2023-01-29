-- MySQL dump 10.13  Distrib 8.0.31, for macos12 (x86_64)
--
-- Host: localhost    Database: ezlife
-- ------------------------------------------------------
-- Server version	8.0.31

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
-- Table structure for table `account_book`
--

DROP TABLE IF EXISTS `account_book`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `account_book` (
  `id` int NOT NULL AUTO_INCREMENT,
  `book_name` varchar(50) NOT NULL,
  `host_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `host_id` (`host_id`),
  CONSTRAINT `account_book_ibfk_1` FOREIGN KEY (`host_id`) REFERENCES `member` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `account_book`
--

LOCK TABLES `account_book` WRITE;
/*!40000 ALTER TABLE `account_book` DISABLE KEYS */;
INSERT INTO `account_book` VALUES (2,'北海道七日遊',1),(4,'澳洲新大陸',1),(6,'101宿舍',1);
/*!40000 ALTER TABLE `account_book` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `category`
--

DROP TABLE IF EXISTS `category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `category` (
  `id` int NOT NULL AUTO_INCREMENT,
  `category` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `category`
--

LOCK TABLES `category` WRITE;
/*!40000 ALTER TABLE `category` DISABLE KEYS */;
/*!40000 ALTER TABLE `category` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `collaborator`
--

DROP TABLE IF EXISTS `collaborator`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `collaborator` (
  `book_id` int NOT NULL,
  `collaborator_id` int NOT NULL,
  PRIMARY KEY (`book_id`,`collaborator_id`),
  KEY `collaborator_id` (`collaborator_id`),
  CONSTRAINT `collaborator_ibfk_1` FOREIGN KEY (`book_id`) REFERENCES `account_book` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `collaborator_ibfk_2` FOREIGN KEY (`collaborator_id`) REFERENCES `member` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `collaborator`
--

LOCK TABLES `collaborator` WRITE;
/*!40000 ALTER TABLE `collaborator` DISABLE KEYS */;
INSERT INTO `collaborator` VALUES (2,1),(4,1),(6,1);
/*!40000 ALTER TABLE `collaborator` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `journal_list`
--

DROP TABLE IF EXISTS `journal_list`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `journal_list` (
  `id` int NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `category1` varchar(50) NOT NULL,
  `category2` varchar(50) DEFAULT NULL,
  `category3` varchar(50) DEFAULT NULL,
  `remark` varchar(50) DEFAULT NULL,
  `price` int NOT NULL,
  `book_id` int NOT NULL,
  `created_member_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `book_id` (`book_id`),
  KEY `created_member_id` (`created_member_id`),
  CONSTRAINT `journal_list_ibfk_1` FOREIGN KEY (`book_id`) REFERENCES `account_book` (`id`),
  CONSTRAINT `journal_list_ibfk_2` FOREIGN KEY (`created_member_id`) REFERENCES `member` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `journal_list`
--

LOCK TABLES `journal_list` WRITE;
/*!40000 ALTER TABLE `journal_list` DISABLE KEYS */;
INSERT INTO `journal_list` VALUES (1,'2023-01-23','食','餐費','家庭','麥當勞',200,2,1),(3,'2023-01-25','住','房租','個人','1月',8000,2,1),(4,'2023-01-26','食','餐費','宿舍','Crazy Pizza',500,2,1),(7,'2023-01-09','食','餐費','個人','77乳加巧克力',15,2,1),(8,'2023-01-11','樂','交際','個人','同事聚餐',288,2,1),(9,'2023-01-10','住','管理費','家庭','1月管理費',1500,2,2),(10,'2023-01-13','食','餐費','寵物','飼料',200,2,2),(11,'2023-01-11','住','電信','個人','1月',400,2,1);
/*!40000 ALTER TABLE `journal_list` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `member`
--

DROP TABLE IF EXISTS `member`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `member` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `member`
--

LOCK TABLES `member` WRITE;
/*!40000 ALTER TABLE `member` DISABLE KEYS */;
INSERT INTO `member` VALUES (1,'小黑','sha256$qTJwhQqy8ag3YGh3$b02f1cf90624d67d2b77beaa17de962fb110e118dd29dd0343c8ac7dc9cf199e','black@gmail.com'),(2,'小粉','sha256$zNHbzY2qVI9vbgmL$f402767459db2ebc9926d6dd7164e0a0f91c3292c7f2ad80d829fb54fa7714cf','pink@gmail.com'),(3,'小紅','sha256$Xl7MvmZFclptDdsD$8f4ae88b5270a9bb06b9c9fcead70afd1cb63cb0abb59a0b0413a9f06a45a6d8','red@gmail.com');
/*!40000 ALTER TABLE `member` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-01-29 16:53:14
