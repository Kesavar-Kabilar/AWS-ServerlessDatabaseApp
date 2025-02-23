CREATE DATABASE IF NOT EXISTS superhero_db;  -- Creates the database if it doesn't exist
USE superhero_db; -- Selects the database to use

CREATE TABLE superheroes (
    id INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,  -- Auto-incrementing primary key
    name VARCHAR(20),  -- VARCHAR with a length of 20
    hero VARCHAR(20),  -- VARCHAR with a length of 20
    power VARCHAR(20),  -- VARCHAR with a length of 20
    xp INT UNSIGNED,
    color VARCHAR(20)   -- VARCHAR with a length of 20
);

-- Populate RDS Auoral MySQL Database with the Data from S3 Bucket
LOAD DATA FROM S3 's3://mybucketkes/mp6data.csv'
INTO TABLE superheroes
FIELDS TERMINATED BY ','
IGNORE 1 LINES  -- Skip the header row
(id, name, hero, power, xp, color);

-- Check if populated correctly
USE superhero_db; 
SELECT * FROM superheroes LIMIT 5;


-- Run The Following Section To Delete All Data
USE superhero_db;
TRUNCATE TABLE superheroes;
DROP TABLE superheroes; 
DROP DATABASE superhero_db; 