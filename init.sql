-- Create database if it does not exist
CREATE DATABASE IF NOT EXISTS devops;

-- Use the created database
USE devops;

-- Create user if it does not exist (considering compatibility)
CREATE USER IF NOT EXISTS 'tommy'@'%' IDENTIFIED WITH caching_sha2_password BY 'tommypassword';

-- Grant privileges to the user
GRANT ALL PRIVILEGES ON devops.* TO 'tommy'@'%';

-- Flush privileges to apply changes
FLUSH PRIVILEGES;

-- Create table in the 'devops' database
CREATE TABLE IF NOT EXISTS messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    message TEXT
);
