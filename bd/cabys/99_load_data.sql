-- Must change file path so it points to the proper location of each file. Files'll be inside "data" folder where this script is, but the full path will differ from environment to environment.
-- E.g. C:/api/bd/cabys/data/cabys_data.txt
LOAD DATA INFILE '/path/to/bd/cabys/data/cabys_data.txt' INTO TABLE cabys FIELDS TERMINATED BY '$' LINES TERMINATED BY '\r\n';
LOAD DATA INFILE '/path/to/bd/cabys/data/cabysxsac_data.txt' INTO TABLE cabysxsac FIELDS TERMINATED BY ',' LINES TERMINATED BY '\r\n';
LOAD DATA INFILE '/path/to/bd/cabys/data/medicamento_data.txt' INTO TABLE medicamento FIELDS TERMINATED BY '$' LINES TERMINATED BY '\r\n';
