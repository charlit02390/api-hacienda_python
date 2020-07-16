use jack_api_hacienda; -- or a different db? dunno

-- ---------------------------
-- Table cabys --
-- ---------------------------
DROP TABLE IF EXISTS `cabys`;
CREATE TABLE `cabys`
(
  `cat1`         	VARCHAR(1)				DEFAULT NULL,
  `cat1desc`     VARCHAR(1000)			DEFAULT NULL,
  `cat2`         	VARCHAR(2)				DEFAULT NULL,
  `cat2desc`     VARCHAR(1000)			DEFAULT NULL,
  `cat3`         	VARCHAR(3)				DEFAULT NULL,
  `cat3desc`     VARCHAR(1000)			DEFAULT NULL,
  `cat4`         	VARCHAR(4)				DEFAULT NULL,
  `cat4desc`     VARCHAR(1000)			DEFAULT NULL,
  `cat5`         	VARCHAR(5)				DEFAULT NULL,
  `cat5desc`     VARCHAR(1000)			DEFAULT NULL,
  `cat6`         	VARCHAR(7)				DEFAULT NULL,
  `cat6desc`     VARCHAR(1000)			DEFAULT NULL,
  `cat7`         	VARCHAR(9)				DEFAULT NULL,
  `cat7desc`     VARCHAR(1000)			DEFAULT NULL,
  `cat8`         	VARCHAR(11)				DEFAULT NULL,
  `cat8desc`     VARCHAR(1000)			DEFAULT NULL,
  `code`         	VARCHAR(13)				DEFAULT NULL,
  `description`	VARCHAR(4000),
  `tax`          	TINYINT UNSIGNED	DEFAULT 0,
	PRIMARY KEY (`code`)
);
-- ---------------------------


-- ---------------------------
-- Table cabysxsac --
-- ---------------------------
DROP TABLE IF EXISTS `cabysxsac`;
CREATE TABLE `cabysxsac`
(
  `sac_version_2017`					VARCHAR(20)					DEFAULT NULL,
  `codigo_cabys_sac`					VARCHAR(13)					DEFAULT NULL,
  `cantidad_codigos_cabys_sac`  SMALLINT UNSIGNED	DEFAULT 0,
  CONSTRAINT FK_CabysXSac_Cabys FOREIGN KEY (`codigo_cabys_sac`) REFERENCES `cabys` (`code`)
);
-- ---------------------------


-- ---------------------------
-- Table medicamento --
-- ---------------------------
DROP TABLE IF EXISTS `medicamento`;
CREATE TABLE `medicamento` (
	`cabyscodigo`	VARCHAR(15),
	`msprincipio`	VARCHAR(700)		DEFAULT NULL,
	`atccodigo`		VARCHAR(15),
	`atcprincipio`	VARCHAR(200),
	`descripcion`	VARCHAR(200)
);
-- ---------------------------
