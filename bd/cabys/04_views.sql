use jack_api_hacienda; -- or a different db? dunno

-- ---------------------------
-- View vw_cabysxsac --
-- ---------------------------
CREATE VIEW vw_cabysxsac
AS
SELECT	ca.`code`,
	cs.sac_version_2017 AS `Codigo SAC`,
	ca.description AS `Descripcion Cabys`,
	cs.cantidad_codigos_cabys_sac
        
FROM	cabysxsac AS cs INNER JOIN
			cabys AS ca ON cs.codigo_cabys_sac = ca.`code`;
-- ---------------------------
