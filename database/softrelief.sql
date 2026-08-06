-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: softrelief
-- ------------------------------------------------------
-- Server version	8.0.46

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `softrelief`
--

/*!40000 DROP DATABASE IF EXISTS `softrelief`*/;

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `softrelief` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `softrelief`;

--
-- Table structure for table `bitacora_cuenta`
--

DROP TABLE IF EXISTS `bitacora_cuenta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bitacora_cuenta` (
  `id_bitacora` int NOT NULL AUTO_INCREMENT,
  `id_admin` int DEFAULT NULL,
  `id_usuario` int DEFAULT NULL,
  `accion` enum('asignar_recomendacion','cargar_recurso','sugerir_musica','activa','restringida','eliminar') COLLATE utf8mb4_unicode_ci NOT NULL,
  `descripcion` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `fecha_evento` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_bitacora`),
  KEY `fk_bitacora_admin` (`id_admin`),
  KEY `fk_bitacora_usuario` (`id_usuario`),
  CONSTRAINT `fk_bitacora_admin` FOREIGN KEY (`id_admin`) REFERENCES `usuario` (`id_usuario`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_bitacora_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bitacora_cuenta`
--

LOCK TABLES `bitacora_cuenta` WRITE;
/*!40000 ALTER TABLE `bitacora_cuenta` DISABLE KEYS */;
INSERT INTO `bitacora_cuenta` VALUES (1,2,3,'asignar_recomendacion','RECOMENDACION\nTítulo: prueba\nDetalle: cd\nMongo ID: mongo_usuario_3','2026-07-20 14:23:38'),(2,2,3,'asignar_recomendacion','RECOMENDACION\nTítulo: dia 2\nDetalle: debes de ser mas constante en tu actividad\nMongo ID: mongo_usuario_3','2026-07-23 09:35:49'),(3,2,3,'asignar_recomendacion','RECOMENDACION\nTítulo: day 3\nDetalle: mantener enfoque\nMongo ID: mongo_usuario_3','2026-07-23 12:58:37'),(4,2,3,'asignar_recomendacion','RECOMENDACION\nTítulo: prueba\nDetalle: debes cuidarte','2026-07-30 22:56:07'),(5,2,3,'asignar_recomendacion','RECOMENDACION\nTítulo: te sientes triste\nDetalle: debes de hacer mas microdescanso','2026-07-31 00:41:46');
/*!40000 ALTER TABLE `bitacora_cuenta` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `estado_cuenta`
--

DROP TABLE IF EXISTS `estado_cuenta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `estado_cuenta` (
  `id_estado` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `descripcion` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id_estado`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=115 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `estado_cuenta`
--

LOCK TABLES `estado_cuenta` WRITE;
/*!40000 ALTER TABLE `estado_cuenta` DISABLE KEYS */;
INSERT INTO `estado_cuenta` VALUES (1,'activa','Cuenta activa con acceso permitido al sistema.'),(2,'restringida','Cuenta limitada por decisión administrativa.');
/*!40000 ALTER TABLE `estado_cuenta` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `permiso`
--

DROP TABLE IF EXISTS `permiso`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `permiso` (
  `id_permiso` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `descripcion` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id_permiso`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=857 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `permiso`
--

LOCK TABLES `permiso` WRITE;
/*!40000 ALTER TABLE `permiso` DISABLE KEYS */;
INSERT INTO `permiso` VALUES (1,'checkin','Permite registrar check-in emocional.'),(2,'modo_calma','Permite acceder al modo calma.'),(3,'sonidos','Permite acceder a sonidos ambientales.'),(4,'microdescansos','Permite realizar microdescansos.'),(5,'historial','Permite consultar historial personal.'),(6,'configuracion','Permite modificar preferencias visuales.'),(7,'panel_especialista','Permite acceder al panel especialista.'),(8,'trayectoria_usuario','Permite consultar trayectoria de usuarios.'),(9,'asignar_recomendacion','Permite asignar recomendaciones.'),(10,'marcar_seguimiento','Permite marcar seguimiento.'),(11,'cargar_recurso','Permite cargar recursos de apoyo.'),(12,'gestionar_usuarios','Permite administrar cuentas.'),(13,'moderar_usuarios','Permite activar, restringir o eliminar usuarios.'),(14,'gestionar_roles','Permite gestionar roles y permisos.'),(407,'consultar_historial_bienestar','Permite consultar el historial de bienestar en MongoDB.'),(408,'sugerir_musica','Permite sugerir música a usuarios.');
/*!40000 ALTER TABLE `permiso` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `preferencia_visual`
--

DROP TABLE IF EXISTS `preferencia_visual`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `preferencia_visual` (
  `id_preferencia` int NOT NULL AUTO_INCREMENT,
  `id_tema` int NOT NULL,
  `tamano_fuente` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'normal',
  `modo_visualizacion` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'estandar',
  `idioma` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'es',
  PRIMARY KEY (`id_preferencia`),
  KEY `fk_preferencia_tema` (`id_tema`),
  CONSTRAINT `fk_preferencia_tema` FOREIGN KEY (`id_tema`) REFERENCES `tema` (`id_tema`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `preferencia_visual`
--

LOCK TABLES `preferencia_visual` WRITE;
/*!40000 ALTER TABLE `preferencia_visual` DISABLE KEYS */;
INSERT INTO `preferencia_visual` VALUES (2,1,'normal','estandar','es'),(3,2,'normal','estandar','en'),(4,1,'normal','estandar','es'),(7,2,'normal','estandar','es');
/*!40000 ALTER TABLE `preferencia_visual` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rol`
--

DROP TABLE IF EXISTS `rol`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rol` (
  `id_rol` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `descripcion` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id_rol`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=172 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rol`
--

LOCK TABLES `rol` WRITE;
/*!40000 ALTER TABLE `rol` DISABLE KEYS */;
INSERT INTO `rol` VALUES (1,'usuario','Usuario regular con acceso a funciones de bienestar personal.'),(2,'especialista','Usuario encargado de asesoría, seguimiento y recursos.'),(3,'superuser','Administrador principal del sistema.');
/*!40000 ALTER TABLE `rol` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rol_permiso`
--

DROP TABLE IF EXISTS `rol_permiso`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rol_permiso` (
  `id_rol` int NOT NULL,
  `id_permiso` int NOT NULL,
  PRIMARY KEY (`id_rol`,`id_permiso`),
  KEY `fk_rol_permiso_permiso` (`id_permiso`),
  CONSTRAINT `fk_rol_permiso_permiso` FOREIGN KEY (`id_permiso`) REFERENCES `permiso` (`id_permiso`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_rol_permiso_rol` FOREIGN KEY (`id_rol`) REFERENCES `rol` (`id_rol`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rol_permiso`
--

LOCK TABLES `rol_permiso` WRITE;
/*!40000 ALTER TABLE `rol_permiso` DISABLE KEYS */;
INSERT INTO `rol_permiso` VALUES (1,1),(1,2),(1,3),(1,4),(1,5),(1,6),(2,6),(3,6),(2,7),(2,8),(2,9),(2,10),(2,11),(3,12),(3,13),(3,14),(2,407),(3,407),(2,408);
/*!40000 ALTER TABLE `rol_permiso` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tema`
--

DROP TABLE IF EXISTS `tema`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tema` (
  `id_tema` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `descripcion` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id_tema`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=120 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tema`
--

LOCK TABLES `tema` WRITE;
/*!40000 ALTER TABLE `tema` DISABLE KEYS */;
INSERT INTO `tema` VALUES (1,'light','Tema visual claro.'),(2,'dark','Tema visual oscuro.');
/*!40000 ALTER TABLE `tema` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuario`
--

DROP TABLE IF EXISTS `usuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuario` (
  `id_usuario` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `correo` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `contrasena` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `fecha_registro` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `id_rol` int NOT NULL,
  `id_estado` int NOT NULL,
  `id_preferencia` int NOT NULL,
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `correo` (`correo`),
  UNIQUE KEY `id_preferencia` (`id_preferencia`),
  KEY `fk_usuario_rol` (`id_rol`),
  KEY `fk_usuario_estado` (`id_estado`),
  CONSTRAINT `fk_usuario_estado` FOREIGN KEY (`id_estado`) REFERENCES `estado_cuenta` (`id_estado`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_usuario_preferencia` FOREIGN KEY (`id_preferencia`) REFERENCES `preferencia_visual` (`id_preferencia`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_usuario_rol` FOREIGN KEY (`id_rol`) REFERENCES `rol` (`id_rol`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `chk_usuario_contrasena` CHECK ((char_length(`contrasena`) >= 4))
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuario`
--

LOCK TABLES `usuario` WRITE;
/*!40000 ALTER TABLE `usuario` DISABLE KEYS */;
INSERT INTO `usuario` VALUES (2,'Especialista','especialista@softrelief.local','e3e996e6262842926a94df6df56fa710017328aaba5c59e1e481394e2e8ae981','2026-07-20 00:00:00',2,1,2),(3,'mau','mau@gmail.com','8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92','2026-07-20 00:00:00',1,1,3),(4,'la ballena','ballena@hot.com','8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92','2026-07-23 00:00:00',1,1,4),(7,'Superuser','superuser@softrelief.local','240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9','2026-08-03 00:00:00',3,1,7);
/*!40000 ALTER TABLE `usuario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'softrelief'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-08-05 23:11:37
