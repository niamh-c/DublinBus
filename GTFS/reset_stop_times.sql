-- MySQL dump 10.13  Distrib 8.0.16, for Linux (x86_64)
--
-- Host: 127.0.0.1    Database: website
-- ------------------------------------------------------
-- Server version	8.0.16

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
 SET NAMES utf8 ;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `stop_times`
--

DROP TABLE IF EXISTS `stop_times`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `stop_times` (
  `trip_id` varchar(45) NOT NULL,
  `arrival_time` time DEFAULT NULL,
  `departure_time` time DEFAULT NULL,
  `stop_id` varchar(45) DEFAULT NULL,
  `stop_sequence` int(11) NOT NULL,
  `stop_headsign` varchar(45) DEFAULT NULL,
  `shape_dist_traveled` varchar(45) DEFAULT NULL,
  `service_id` varchar(45) DEFAULT NULL,
  `route_short_name` varchar(45) DEFAULT NULL,
  `predicted_arrival_times_0` time DEFAULT NULL,
  `predicted_arrival_times_1` time DEFAULT NULL,
  `predicted_arrival_times_2` time DEFAULT NULL,
  `predicted_arrival_times_3` time DEFAULT NULL,
  `predicted_arrival_times_4` time DEFAULT NULL,
  `predicted_arrival_times_5` time DEFAULT NULL,
  `predicted_arrival_times_6` time DEFAULT NULL,
  `predicted_arrival_times_7` time DEFAULT NULL,
  `predicted_arrival_times_8` time DEFAULT NULL,
  `predicted_arrival_times_9` time DEFAULT NULL,
  PRIMARY KEY (`trip_id`,`stop_sequence`),
  KEY `stops` (`stop_id`),
  KEY `trip+route` (`trip_id`,`stop_id`),
  KEY `route` (`route_short_name`),
  CONSTRAINT `fk_stop_times_1` FOREIGN KEY (`stop_id`) REFERENCES `stops` (`stop_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
