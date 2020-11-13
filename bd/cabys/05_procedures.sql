use jack_api_hacienda; -- or a different db? dunno

DELIMITER //
-- ---------------------------
-- User Stored Procedure usp_buscar_cabys --
-- ---------------------------
CREATE PROCEDURE usp_buscar_cabys(
    IN p_patron VARCHAR(100)
)
BEGIN
	SELECT `code` AS codigo
    	,description AS descripcion
        ,tax AS impuesto
	FROM cabys
	WHERE CONCAT_WS(' ', cat8desc, description) REGEXP p_patron;
END //
-- ---------------------------


-- ---------------------------
-- User Stored Procedure usp_buscar_medicamento --
-- ---------------------------
CREATE PROCEDURE usp_buscar_medicamento(
    IN p_patron VARCHAR(100)
)
BEGIN
	SELECT cabyscodigo AS `Codigo Cabys`
    	,msprincipio AS `Principio Activo MS`
        ,atccodigo AS `Codigo ATC`
        ,atcprincipio AS `Principio ATC`
        ,descripcion AS `Descripcion`
   	FROM medicamento
    WHERE CONCAT_WS(' ', msprincipio, atcprincipio, descripcion) REGEXP p_patron;
END //
-- ---------------------------


-- ---------------------------
-- User Stored Procedure usp_obtenersacs_cabysxsac --
-- ---------------------------
CREATE PROCEDURE usp_obtenersacs_cabysxsac(
    p_cod_cabys VARCHAR(13)
)
BEGIN
	SELECT `code` AS `Codigo Cabys`,
		`Codigo SAC`,
    	`Descripcion Cabys`
    FROM vw_cabysxsac
    WHERE `code` = p_cod_cabys;
END //
-- ---------------------------

-- ---------------------------
-- User Stored Procedure usp_obtenersacs_cabysxsac --
-- ---------------------------
CREATE PROCEDURE usp_selectByCode_cabys (
    p_code VARCHAR(13)
)
BEGIN
    SELECT `code` AS codigo
    	,description AS descripcion
        ,tax AS impuesto
	FROM cabys
	WHERE `code` = p_code; 
END //
-- ---------------------------
DELIMITER ;
