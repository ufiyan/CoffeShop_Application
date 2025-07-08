import psycopg2
from datetime import timedelta
 
# Connect to your PostgreSQL database
conn = psycopg2.connect(
    dbname="postgres",     # Default database name (if using default)
    user="postgres",       # Default user (if using default)
    password="mypassword", # Replace with your password
    host="localhost",      # Localhost if running locally
    port="5432"            # Default PostgreSQL port
)
cur = conn.cursor()

#TODO
def baristaView():

    cur.execute("SELECT drink_id, name, price FROM drinks")
    menu = cur.fetchall()
    print("\n--- Menu ---")
    for did, name, price in menu:
        print(f"{did}. {name} - ${price:.2f}")
    print("Type 'done' when finished.\n")

    order_items = {}
    while True:
        choice = input("Enter drink ID (or 'done'): ").strip()
        if choice.lower() == 'done':
            break
        try:
            did = int(choice)
        except ValueError:
            print("Please enter a valid ID or 'done'.")
            continue

        if not any(did == d[0] for d in menu):
            print("Invalid drink ID.")
            continue

        qty = input("  Quantity: ").strip()

        order_items[did] = order_items.get(did, 0) + int(qty)

    if not order_items:
        print("No items ordered. Returning to main menu.\n")
        return

    #prep 
    for did, qty in order_items.items():
        cur.execute(
            "SELECT name FROM drinks WHERE drink_id = %s",
            (did,)
        )
        drink_name = cur.fetchone()[0]

        print(f"Preparation for {drink_name} (x{qty}):")
        cur.execute(
            "SELECT step_number, step_description "
            "FROM preparation WHERE drink_id = %s "
            "ORDER BY step_number",
            (did,)
        )
        for step_no, desc in cur.fetchall():
            print(f"  {step_no}. {desc}")
        print()

    # 3) Payment method
    payment = input("Payment method (cash/credit_card/app): ").strip()
    if payment not in ('cash','credit_card','app'):
        print("Invalid method; defaulting to cash.")
        payment = 'cash'

    cur.execute(
        "INSERT INTO orders (payment_method, order_timestamp) "
        "VALUES (%s, NOW()) RETURNING order_id",
        (payment,)
    )
    order_id = cur.fetchone()[0]

    total_price = 0.0

    for did, qty in order_items.items():
  
        cur.execute("SELECT price, name FROM drinks WHERE drink_id = %s", (did,))
        price, drink_name = cur.fetchone()
        price = float(price)
        total_price += price * qty


        cur.execute(
            "INSERT INTO lineitems (order_id, drink_id, quantity) "
            "VALUES (%s, %s, %s)",
            (order_id, did, qty)
        )

        cur.execute(
            "SELECT ingredient_name, quantity FROM drinkingredients "
            "WHERE drink_id = %s",
            (did,)
        )
        for ing_name, per_qty in cur.fetchall():
            remove_amt = per_qty * qty
            cur.execute(
                "UPDATE inventory "
                "SET quantity_in_stock = quantity_in_stock - %s "
                "WHERE ingredient_name = %s",
                (remove_amt, ing_name)
            )

    # accounting 
    cur.execute(
        "SELECT balance FROM accountingentries "
        "ORDER BY entry_timestamp DESC LIMIT 1"
    )
    last = cur.fetchone()
    last_balance = last[0] if last else 0.0
    new_balance = float(last_balance) + total_price

    cur.execute(
        "INSERT INTO accountingentries (entry_timestamp, balance) "
        "VALUES (NOW(), %s)",
        (new_balance,)
    )

    conn.commit()

    print(f"\nOrder #{order_id} placed. Total = ${total_price:.2f}")
    print(f"New café balance: ${new_balance:.2f}\n")

    

    choice = input("Enter 1 to submit new order, 2 to quit:\n")
    if choice == "1":
        baristaView()
    elif choice == "2":
        return



def manageEmployees():
    cur.execute("SELECT * FROM employees")
    results = cur.fetchall()
    print("----------------------------------------------------------------------------------------------------")
    index = 1
    for result in results:
        print(f'{index}. Name: {result[1]}, Email: {result[2]}, Salary: {result[3]}, Social Security: {result[0]}')
        index += 1
    print("----------------------------------------------------------------------------------------------------")
    print("1. Hire an employee")
    print("2. Fire an employee")
    print("3. Manage an employee")
    choice = input()
    while choice != '1' and choice != '2' and choice != '3':
        print("Invalid choice")
        print("1. Hire an employee")
        print("2. Fire an employee")
        print("3. Manage an employee")
        choice = input()
    if choice == '1':
        print("Enter the employee information in this format")
        employee = input("Name, Email, Salary, Social Security\n")
        employee = employee.split(',')
        employee = [data.strip() for data in employee]  # trim leading whitespeace
        # Add to the employess
        # TODO handle making a barista or manager and error check

        print("Is the employee a Manager, Barista, or Both? (M/B/Both)")
        role = input().strip().upper()
        while role not in ['M', 'B', 'BOTH']:
            print("Invalid role. Enter M for Manager, B for Barista, or BOTH.")
            role = input().strip().upper()
        # First insert into employees table
        cur.execute("""INSERT INTO employees (ssn, name, email, salary) VALUES
                    (%s, %s, %s, %s)""", (employee[3], employee[0], employee[1], employee[2]))
        conn.commit()
        print("Employee added to employees table.")

        # Then insert roles
        if role in ['M', 'BOTH']:
            ownership = input("Enter the ownership of the employee (e.g., 25)").strip()
            try:
                cur.execute("INSERT INTO managers (ssn, ownership_percentage) VALUES (%s, %s)",
                            (employee[3], float(ownership)))
                conn.commit()
            except Exception as e:
                print("Error adding to managers:", e)

        if role in ['B', 'BOTH']:
            try:
                cur.execute("INSERT INTO baristas (ssn) VALUES (%s)", (employee[3],))
                conn.commit()
            except Exception as e:
                print("Error adding to baristas:", e)

        print("Employee hired successfully.")
        conn.commit()
        print("Employee hired")

    elif choice == '2':
        toFire = int(input("Enter the index of employee to fire\n"))
        while toFire < 1 or toFire > len(results):
            print("Wrong index. Enter another index")
            toFire = int(input())

        toFireSsn = results[toFire - 1][0]

        # Prevent self-deletion
        if toFireSsn == ssn:
            print("Error: You cannot fire yourself.")
            return

        # Remove from roles and password table first
        cur.execute("DELETE FROM baristas WHERE ssn = %s", (toFireSsn,))
        cur.execute("DELETE FROM managers WHERE ssn = %s", (toFireSsn,))
        cur.execute("DELETE FROM passwords WHERE email = %s", (results[toFire - 1][2],))  # delete by email
        cur.execute("DELETE FROM employees WHERE ssn = %s", (toFireSsn,))
        conn.commit()

        cur.execute("DELETE FROM employees WHERE ssn = %s", (toFireSsn,))
        conn.commit()
        print(f'{results[toFire - 1][1]} was fired')

    else:
        # modify the salary
        toModify = int(input("Enter the index of employee to modify\n"))
        while toModify < 1 or toModify > len(results):
            print("Wrong index. Enter another index")
            toModify = int(input())

        toModifySsn = results[toModify - 1][0]
        print("Enter the employee information in this format")
        employee = input("Name, Email, Salary, Social Security\n")
        employee = employee.split(',')
        employee = [data.strip() for data in employee]  # trim leading whitespeace
        cur.execute("""UPDATE employees SET ssn = %s, name = %s, email = %s, salary = %s
                    WHERE ssn = %s""", (employee[3], employee[0], employee[1], employee[2], toModifySsn))
        conn.commit()
        print("Employee updated")

        # Update manager ownership if applicable
        cur.execute("SELECT * FROM managers WHERE ssn = %s", (employee[3],))
        if cur.fetchone():
            updateOwner = input("Update ownership percentage? (Y/N): ").strip().upper()
            if updateOwner == 'Y':
                newOwnership = input("Enter new percentage: ").strip()
                cur.execute("UPDATE managers SET ownership_percentage = %s WHERE ssn = %s",
                            (float(newOwnership), employee[3]))
                conn.commit()
                print("Ownership updated.")

        # Update barista schedule if applicable
        cur.execute("SELECT * FROM baristas WHERE ssn = %s", (employee[3],))
        if cur.fetchone():
            updateSched = input("Update barista work schedule? (Y/N): ").strip().upper()
            if updateSched == 'Y':
                cur.execute("DELETE FROM workschedule WHERE ssn = %s", (employee[3],))
                numShifts = int(input("How many shifts to enter? "))
                for i in range(numShifts):
                    print(f"Shift {i + 1}: Day, StartTime, EndTime (e.g., Monday,08:00,12:00)")
                    shift = input().split(',')
                    shift = [s.strip() for s in shift]
                    cur.execute("""
                        INSERT INTO workschedule (ssn, day_of_week, start_time, end_time)
                        VALUES (%s, %s, %s, %s)
                    """, (employee[3], shift[0], shift[1], shift[2]))
                conn.commit()
                print("Schedule updated.")


def manageInventory():
    

    #get today money and date
    cur.execute("SELECT entry_timestamp FROM accountingentries ORDER BY entry_timestamp DESC LIMIT 1")
    yesterday = cur.fetchone()[0]
    today = yesterday + timedelta(days=1) #increment date
    
    #get last days balance
    cur.execute("SELECT balance FROM accountingentries ORDER BY entry_timestamp DESC LIMIT 1")
    money = float(cur.fetchone()[0]) #yesterday money
    

    while True:
        print("------------------------------")
        print("Inventory:")
        cur.execute("SELECT ingredient_name, quantity_in_stock, unit FROM inventory")
        results = cur.fetchall()
        for result in results:
            print(f'{result[0]}: {result[1]} {result[2]}')
        print("------------------------------")
        toOrder = input("Enter the name of the item to order or X to cancel\n")
        cur.execute("SELECT ingredient_name, quantity_in_stock, unit, purchase_price FROM inventory WHERE ingredient_name = %s", (toOrder,))
        result = cur.fetchone()
        while (toOrder != "X" and not result):
            print("Invalid item name")
            toOrder = input("Enter the name of the item to order or X to cancel\n")
            cur.execute("SELECT ingredient_name, quantity_in_stock, unit, purchase_price FROM inventory WHERE ingredient_name = %s", (toOrder,))
            result = cur.fetchone()
        if toOrder == 'X':
            cur.execute("INSERT INTO accountingentries VALUES (%s, %s)",(today, money))
            conn.commit()
            print("Accounting entries updated")
            return

        print(f'{result[0]}:')
        print(f'Currently in inventory: {result[1]} {result[2]}')
        print(f'Purchase price: ${result[3]} per {result[2]}')
        print(f'How much would you like to purchase?')
        quantity = int(input())
        purchasedPrice = quantity * float(result[3])
        print(f'Purchased {quantity} {result[2]} of {result[0]} for ${purchasedPrice}')
        #Update inventory
        newQuantity = quantity + float(result[1])

        cur.execute("UPDATE inventory SET quantity_in_stock = %s WHERE ingredient_name = %s", (newQuantity, result[0]))
        conn.commit()
        money -= purchasedPrice


def viewReports():
    cur.execute("SELECT entry_timestamp, balance FROM accountingentries ORDER BY entry_timestamp ASC")
    results = cur.fetchall()
    print("------------------------------")
    for result in results:
        print(f'{result[0]}: ${result[1]}')
    print("------------------------------")

#TODO
def managerView():
    while True:
        print("Select option:")
        print("1. Manage employees")
        print("2. Manage inventory")
        print("3. Accounting report")
        print("4. Logout")
        choice = input()
        if (choice == "1"):
            manageEmployees()
        elif (choice == "2"):
            manageInventory()
        elif (choice == "3"):
            viewReports()
        elif (choice == "4"):
            break
        else:
            print("Invalid choice")


#TODO
def baristaManagerView():

    while True:
        print("Select option:")
        print("1. Manage employees")
        print("2. Manage inventory")
        print("3. Accounting report")
        print("4. Prepare drinks")
        print("5. Logout")
        choice = input()
        if (choice == "1"):
            manageEmployees()
        elif (choice == "2"):
            manageInventory()
        elif (choice == "3"):
            viewReports()
        elif (choice == "4"):
            baristaView()
        elif (choice == "5"):
            break
        else:
            print("Invalid choice")







while True:


    print("Welcome to Killer Bean")
    email = input("Enter your email ")
    #Check if email is registered to an employee
    cur.execute("SELECT * FROM employees WHERE email = %s", (email,))
    isWorker = cur.fetchone()

    #not an employee
    if not isWorker:
        print("Invalid email")
    else:
        #email is bound to an emplyee, get the password, if employee is first time using the system create a passwrod for them isntead
        cur.execute("SELECT password FROM passwords WHERE email = %s", (email,))
        password = cur.fetchone()
        # employee not yet registered
        
        if not password:
            newPassword = input("Create your password ")
            cur.execute("INSERT INTO passwords (email, password) VALUES (%s, %s)", (email, newPassword))
            conn.commit()
            print("Password created")
        else:
            #employee is registed ask for password
            userPassword = input("Enter your password ")
            while not userPassword == password[0]:
                print("Invalid password")
                userPassword = input("Enter your password ")

            

    #employee is now past the login phase
    #check wheter the employee is a manager or barista or both

    #get ssn based on email
    cur.execute("SELECT ssn FROM employees WHERE email = %s", (email,))
    ssn = cur.fetchone()[0]
    
    #check if manager
    cur.execute("SELECT * FROM managers WHERE ssn = %s", (ssn,))
    isManager = cur.fetchone()
    #check if barista
    cur.execute("SELECT * FROM baristas WHERE ssn = %s", (ssn,))
    isBarista = cur.fetchone()

    if isBarista and isManager:
        baristaManagerView()
    elif isManager:
        managerView()
    else:
        baristaView()







cur.close()
conn.close()
