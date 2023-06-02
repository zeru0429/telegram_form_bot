# telegram_form_bot
begize shopping online registration form on telegram bote
pip install python-telegram-bot==13.14
 pip mysql-connector-python
 
 #database comand
 CREATE DATABASE begize-bot;
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255),
    phone_number VARCHAR(20)
);

CREATE TABLE photos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    photo_url VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

 
 
 'user': 'Mihiretu',
    'password': 'Tsi@mt14',
    'host': 'Mihiretu.mysql.pythonanywhere-services.com',
    'database': 'Mihiretu$default'
 
 
