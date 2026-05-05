CREATE DATABASE IF NOT EXISTS restaurant_management;
USE restaurant_management;

DROP TABLE IF EXISTS attendance_logs;
DROP TABLE IF EXISTS bills;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS restaurant_tables;
DROP TABLE IF EXISTS menu_items;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
  user_id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL,
  role ENUM('Admin','Staff') NOT NULL DEFAULT 'Staff'
);

CREATE TABLE customers (
  customer_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  phone VARCHAR(20),
  email VARCHAR(100)
);

CREATE TABLE menu_items (
  item_id INT AUTO_INCREMENT PRIMARY KEY,
  item_name VARCHAR(100) NOT NULL,
  category VARCHAR(50) NOT NULL,
  price DECIMAL(10,2) NOT NULL CHECK (price >= 0),
  availability ENUM('Available','Unavailable') NOT NULL DEFAULT 'Available'
);

CREATE TABLE restaurant_tables (
  table_id INT AUTO_INCREMENT PRIMARY KEY,
  table_number VARCHAR(20) NOT NULL UNIQUE,
  capacity INT NOT NULL CHECK (capacity > 0),
  status ENUM('Available','Occupied','Reserved') NOT NULL DEFAULT 'Available'
);

CREATE TABLE orders (
  order_id INT AUTO_INCREMENT PRIMARY KEY,
  customer_id INT,
  table_id INT,
  created_by INT,
  order_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  status ENUM('Open','Served','Billed','Cancelled') NOT NULL DEFAULT 'Open',
  FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE SET NULL,
  FOREIGN KEY (table_id) REFERENCES restaurant_tables(table_id) ON DELETE SET NULL,
  FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL
);

CREATE TABLE order_items (
  order_item_id INT AUTO_INCREMENT PRIMARY KEY,
  order_id INT NOT NULL,
  item_id INT NOT NULL,
  quantity INT NOT NULL CHECK (quantity > 0),
  unit_price DECIMAL(10,2) NOT NULL,
  FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
  FOREIGN KEY (item_id) REFERENCES menu_items(item_id)
);

CREATE TABLE bills (
  bill_id INT AUTO_INCREMENT PRIMARY KEY,
  order_id INT NOT NULL UNIQUE,
  item_total DECIMAL(10,2) NOT NULL,
  tax DECIMAL(10,2) NOT NULL,
  discount DECIMAL(10,2) NOT NULL DEFAULT 0,
  final_amount DECIMAL(10,2) NOT NULL,
  payment_method ENUM('Cash','Card','UPI') NOT NULL,
  paid_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE
);

CREATE TABLE attendance_logs (
  log_id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  clock_in_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  clock_out_time DATETIME NULL,
  status ENUM('Clocked In','Clocked Out') NOT NULL DEFAULT 'Clocked In',
  FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

INSERT INTO users(username, password, role) VALUES
('admin', 'admin123', 'Admin'),
('staff', 'staff123', 'Staff');

INSERT INTO customers(name, phone, email) VALUES
('John Doe', '555-1234', 'john@example.com'),
('Sarah Smith', '555-5678', 'sarah@example.com');

INSERT INTO menu_items(item_name, category, price, availability) VALUES
('Burger', 'Main Course', 8.99, 'Available'),
('French Fries', 'Starters', 3.49, 'Available'),
('Chicken Pizza', 'Main Course', 11.99, 'Available'),
('Coke', 'Drinks', 2.50, 'Available'),
('Brownie', 'Desserts', 4.99, 'Available');

INSERT INTO restaurant_tables(table_number, capacity, status) VALUES
('T1', 2, 'Available'),
('T2', 4, 'Available'),
('T3', 4, 'Reserved'),
('T4', 6, 'Available');
