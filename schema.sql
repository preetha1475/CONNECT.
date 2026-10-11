
CREATE DATABASE IF NOT EXISTS connect_ngo;
USE connect_ngo;

CREATE TABLE IF NOT EXISTS ngo_needs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ngo_name VARCHAR(150) NOT NULL,
    need_type VARCHAR(80) NOT NULL,
    description TEXT NOT NULL,
    area VARCHAR(150) NOT NULL,
    status VARCHAR(30) DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS food_donations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    donor_name VARCHAR(150) NOT NULL,
    food_name VARCHAR(150) NOT NULL,
    quantity VARCHAR(100) NOT NULL,
    area VARCHAR(150) NOT NULL,
    status VARCHAR(30) DEFAULT 'Available',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS contact_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS healthcare_facilities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    facility_name VARCHAR(200) NOT NULL,
    facility_type VARCHAR(100),
    area VARCHAR(150),
    latitude DECIMAL(10,7) NOT NULL,
    longitude DECIMAL(10,7) NOT NULL,
    source VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
