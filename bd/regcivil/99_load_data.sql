-- Must change file path so it points to the proper location of each file. Files'll be inside "data" folder where this script is, but the full path will differ from environment to environment.
-- E.g. C:/api/bd/regcivil/data/registrocivil_data.txt
-- For this specific file, since it's compressed in registrocivil_data.rar, it must be extracted first.
LOAD DATA INFILE '/path/to/bd/regcivil/data/registrocivil_data.txt' INTO TABLE registrocivil FIELDS TERMINATED BY ',' LINES TERMINATED BY '\r\n';
