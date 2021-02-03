use jack_api_hacienda; -- or a different db? dunno

DELIMITER //
-- ---------------------------
-- User Stored Procedure usp_obtenerpersona_registrocivil --
-- ---------------------------
CREATE PROCEDURE usp_obtenerpersona_registrocivil (
    p_cedula VARCHAR(15)
)
BEGIN
	SELECT `cedula`,
		`codelec` AS `ubicacion`,
		`expiracion`,
		`nombre`,
		`apellido1`,
		`apellido2`
	FROM `registrocivil`
	WHERE `cedula` = p_cedula;
END //
-- ---------------------------
DELIMITER ;
