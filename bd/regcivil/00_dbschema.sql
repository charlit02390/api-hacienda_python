use jack_api_hacienda; -- or a different db? dunno

-- ---------------------------
-- Table registrocivil --
-- ---------------------------
CREATE TABLE `registrocivil` (
    `cedula`			VARCHAR(9)	NOT NULL	PRIMARY KEY,
    `codelec`			VARCHAR(6)	NOT NULL,
    `expiracion`	VARCHAR(8)	NOT NULL,
    `nombre`			VARCHAR(30)	NOT NULL,
    `apellido1`		VARCHAR(26)	NOT NULL,
    `apellido2`		VARCHAR(26)
);
-- ---------------------------