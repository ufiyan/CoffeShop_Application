
DROP TABLE IF EXISTS LineItems CASCADE;
DROP TABLE IF EXISTS Orders CASCADE;
DROP TABLE IF EXISTS DrinkIngredients CASCADE;
DROP TABLE IF EXISTS Preparation CASCADE;
DROP TABLE IF EXISTS Drinks CASCADE;
DROP TABLE IF EXISTS AccountingEntries CASCADE;
DROP TABLE IF EXISTS WorkSchedule CASCADE;
DROP TABLE IF EXISTS Baristas CASCADE;
DROP TABLE IF EXISTS Managers CASCADE;
DROP TABLE IF EXISTS Employees CASCADE;
DROP TABLE IF EXISTS Inventory CASCADE;
DROP TABLE IF EXISTS Promotions CASCADE;
DROP TABLE IF EXISTS passwords CASCADE;

-----------------------------------------------------
-- 1. Employees
-----------------------------------------------------
CREATE TABLE employees (
    ssn VARCHAR(11) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    salary NUMERIC(10,2)
);

-----------------------------------------------------
-- 2. Managers
-----------------------------------------------------
CREATE TABLE managers (
    ssn VARCHAR(11) PRIMARY KEY,
    ownership_percentage NUMERIC(5,2) NOT NULL,
    CONSTRAINT fk_manager_employee FOREIGN KEY (ssn)
        REFERENCES employees(ssn)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

-----------------------------------------------------
-- 3. Baristas
-----------------------------------------------------
CREATE TABLE baristas (
    ssn VARCHAR(11) PRIMARY KEY,
    CONSTRAINT fk_barista_employee FOREIGN KEY (ssn)
        REFERENCES employees(ssn)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

-----------------------------------------------------
-- 4. WorkSchedule
-----------------------------------------------------
CREATE TABLE workschedule (
    ssn VARCHAR(11) NOT NULL,
    day_of_week VARCHAR(20) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    PRIMARY KEY (ssn, day_of_week, start_time),
    CONSTRAINT fk_work_schedule_barista FOREIGN KEY (ssn)
        REFERENCES Baristas(ssn)
        ON DELETE CASCADE
);

-----------------------------------------------------
-- 5. AccountingEntries
-----------------------------------------------------
CREATE TABLE accountingentries (
    entry_timestamp TIMESTAMP PRIMARY KEY,
    balance NUMERIC(10,2) NOT NULL
);

-----------------------------------------------------
-- 6. Inventory
-----------------------------------------------------
CREATE TABLE inventory (
    ingredient_name VARCHAR(50) NOT NULL,
    quantity_in_stock NUMERIC(10,2) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    purchase_price NUMERIC(10,2) NOT NULL,
    PRIMARY KEY (ingredient_name)
);

-----------------------------------------------------
-- 7. Drinks
-----------------------------------------------------
CREATE TABLE drinks (
    drink_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    size NUMERIC(10,2) NOT NULL,
    type VARCHAR(50) NOT NULL,
    price NUMERIC(10,2) NOT NULL,
    temperature VARCHAR(10) NOT NULL
);

-----------------------------------------------------
-- 8. Preparation
-----------------------------------------------------
CREATE TABLE preparation (
    drink_id INT NOT NULL,
    step_number INT NOT NULL,
    step_description TEXT NOT NULL,
    PRIMARY KEY (drink_id, step_number),
    CONSTRAINT fk_prep_drink
        FOREIGN KEY (drink_id) REFERENCES Drinks(drink_id)
);

-----------------------------------------------------
-- 9. DrinkIngredients
-----------------------------------------------------
CREATE TABLE drinkingredients (
    drink_id INT NOT NULL,
    ingredient_name VARCHAR(50) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    quantity NUMERIC(10,2) NOT NULL,
    PRIMARY KEY (drink_id, ingredient_name),
    CONSTRAINT fk_ingredients_drink
        FOREIGN KEY (drink_id) REFERENCES Drinks(drink_id),
    CONSTRAINT fk_ingredients_inventory
        FOREIGN KEY (ingredient_name) REFERENCES Inventory(ingredient_name)
);

-----------------------------------------------------
-- 10. Orders
-----------------------------------------------------
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    payment_method VARCHAR(50) NOT NULL,
    order_timestamp TIMESTAMP NOT NULL
);

-----------------------------------------------------
-- 11. LineItems
-----------------------------------------------------
CREATE TABLE lineitems (
    line_item_id SERIAL PRIMARY KEY,
    order_id INT NOT NULL,
    drink_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    FOREIGN KEY (order_id) REFERENCES Orders(order_id),
    FOREIGN KEY (drink_id) REFERENCES Drinks(drink_id)
);

-----------------------------------------------------
-- 12. Promotions (Bonus)
-----------------------------------------------------
CREATE TABLE promotions (
    promotion_id SERIAL PRIMARY KEY,
    promo_name VARCHAR(255) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL
);

-----------------------------------------------------
-- 13. Passwords
-----------------------------------------------------
CREATE TABLE passwords (
    email VARCHAR(255) NOT NULL PRIMARY KEY,
    password VARCHAR(255) NOT NULL,
    FOREIGN KEY (email) REFERENCES employees(email)
);

INSERT INTO employees (ssn, name, email, salary) VALUES
('111-11-1111', 'Steven Yeun', 'steveny@coffee.com', 85000.00),
('222-22-2222', 'Jonathan Kimble Simmons', 'jonathanks@coffee.com', 95000.00),
('333-33-3333', 'Sandra Oh', 'sandrao@coffee.com', 55000.00),
('555-55-5555', 'Grey Griffin', 'greyg@coffe.com', 47000.00),
('777-77-7777', 'Gillian Jacobs', 'gillianj@coffe.com', 49000.00),
('888-88-8888', 'Walton Goggins', 'waltong@coffe.com', 52000.00),
('999-99-9999', 'Chris Diamantopoulos', 'chrisd@coffe.com', 46000.00);



INSERT INTO managers (ssn, ownership_percentage) VALUES
('111-11-1111', 30.00),  --Steven
('222-22-2222', 70.00);  --JK


INSERT INTO baristas (ssn) VALUES
('222-22-2222'),  -- JK both barista and manager
('333-33-3333'),                
('555-55-5555'),
('777-77-7777'),
('888-88-8888'),
('999-99-9999');   




--Accounting
INSERT INTO accountingentries (entry_timestamp, balance) VALUES
('2025-05-01 20:00:00', 2050.00),
('2025-05-02 20:00:00', 1980.00),
('2025-05-03 20:00:00', 2100.00),
('2025-05-04 20:00:00', 1920.00),
('2025-05-05 20:00:00', 2005.00),
('2025-05-06 20:00:00', 2200.00),
('2025-05-07 20:00:00', 1985.00),
('2025-05-08 20:00:00', 2150.00),
('2025-05-09 20:00:00', 2075.00),
('2025-05-10 20:00:00', 1995.00);


-- raw‐materials
INSERT INTO inventory (ingredient_name, quantity_in_stock, unit, purchase_price) VALUES
  ('Coffee Beans',       5000,   'g', 0.02),    
  ('Water',             10000,  'ml', 0.00),    
  ('Milk',               5000,  'ml', 0.03),    
  ('Sugar',              2000,   'g', 0.01);    


INSERT INTO drinks (name,   size, type,       price, temperature) VALUES
  ('Espresso',        30,   'coffee',     2.50, 'hot'),
  ('Americano',       240,  'coffee',     3.00, 'hot'),
  ('Cappuccino',      180,  'coffee',     4.00, 'hot'),
  ('Latte',           240,  'coffee',     4.50, 'hot');


INSERT INTO drinkingredients (drink_id, ingredient_name, unit, quantity)
  SELECT d.drink_id, 'Coffee Beans','g', 18   FROM drinks d WHERE d.name='Espresso'   UNION ALL
  SELECT d.drink_id, 'Water',       'ml', 30   FROM drinks d WHERE d.name='Espresso'   UNION ALL
  SELECT d.drink_id, 'Coffee Beans','g', 18   FROM drinks d WHERE d.name='Americano'  UNION ALL
  SELECT d.drink_id, 'Water',       'ml', 210  FROM drinks d WHERE d.name='Americano'  UNION ALL
  SELECT d.drink_id, 'Coffee Beans','g', 18   FROM drinks d WHERE d.name='Cappuccino' UNION ALL
  SELECT d.drink_id, 'Milk',        'ml', 120  FROM drinks d WHERE d.name='Cappuccino' UNION ALL
  SELECT d.drink_id, 'Water',       'ml', 42   FROM drinks d WHERE d.name='Cappuccino' UNION ALL
  SELECT d.drink_id, 'Coffee Beans','g', 18   FROM drinks d WHERE d.name='Latte'      UNION ALL
  SELECT d.drink_id, 'Milk',        'ml', 180  FROM drinks d WHERE d.name='Latte'      UNION ALL
  SELECT d.drink_id, 'Water',       'ml', 60   FROM drinks d WHERE d.name='Latte';


INSERT INTO preparation (drink_id, step_number, step_description)
  SELECT d.drink_id, 1, 'Grind coffee beans'                    FROM drinks d WHERE d.name='Espresso'   UNION ALL
  SELECT d.drink_id, 2, 'Tamp firmly'                           FROM drinks d WHERE d.name='Espresso'   UNION ALL
  SELECT d.drink_id, 3, 'Extract espresso shot (30 ml)'         FROM drinks d WHERE d.name='Espresso'   UNION ALL
  SELECT d.drink_id, 1, 'Grind coffee beans'                    FROM drinks d WHERE d.name='Americano'  UNION ALL
  SELECT d.drink_id, 2, 'Extract espresso shot (30 ml)'         FROM drinks d WHERE d.name='Americano'  UNION ALL
  SELECT d.drink_id, 3, 'Add 210 ml hot water'                  FROM drinks d WHERE d.name='Americano'  UNION ALL
  SELECT d.drink_id, 1, 'Grind coffee beans'                    FROM drinks d WHERE d.name='Cappuccino' UNION ALL
  SELECT d.drink_id, 2, 'Extract espresso shot (30 ml)'         FROM drinks d WHERE d.name='Cappuccino' UNION ALL
  SELECT d.drink_id, 3, 'Steam 120 ml milk to microfoam'        FROM drinks d WHERE d.name='Cappuccino' UNION ALL
  SELECT d.drink_id, 4, 'Pour milk over espresso, holding back foam' FROM drinks d WHERE d.name='Cappuccino' UNION ALL
  SELECT d.drink_id, 5, 'Spoon foam on top'                     FROM drinks d WHERE d.name='Cappuccino' UNION ALL
  SELECT d.drink_id, 1, 'Grind coffee beans'                    FROM drinks d WHERE d.name='Latte'      UNION ALL
  SELECT d.drink_id, 2, 'Extract espresso shot (30 ml)'         FROM drinks d WHERE d.name='Latte'      UNION ALL
  SELECT d.drink_id, 3, 'Steam 180 ml milk to a light foam'     FROM drinks d WHERE d.name='Latte'      UNION ALL
  SELECT d.drink_id, 4, 'Pour milk and foam over espresso'      FROM drinks d WHERE d.name='Latte';
