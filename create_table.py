import sqlite3

def create_tables():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Create the users table
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')

    # Create the donor_details table
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS donor_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            blood_type TEXT NOT NULL,
            dob TEXT NOT NULL,
            gender TEXT NOT NULL,
            age INTEGER NOT NULL,
            contact TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Create the hospital_requests table
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS hospital_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hospital_name TEXT NOT NULL,
            hospital_address TEXT NOT NULL,
            blood_type TEXT NOT NULL,
            units INTEGER NOT NULL,
            deadline DATE NOT NULL,
            status TEXT NOT NULL,
            contact TEXT NOT NULL
        )
    ''')

    # Create the blood_availability table
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS blood_availability (
            blood_type TEXT PRIMARY KEY,
            available_units INTEGER NOT NULL
        )
    ''')

    # Create the trigger to update blood availability when a hospital request is added
    cursor.execute(''' 
        CREATE TRIGGER IF NOT EXISTS update_blood_availability
        AFTER INSERT ON hospital_requests
        FOR EACH ROW
        BEGIN
            -- Update the available units in blood_availability
            UPDATE blood_availability
            SET available_units = (
                SELECT COUNT(*) FROM donor_details WHERE blood_type = NEW.blood_type
            )
            WHERE blood_type = NEW.blood_type;

            -- If there is no record for that blood type, insert one
            INSERT INTO blood_availability (blood_type, available_units)
            SELECT NEW.blood_type, COUNT(*) 
            FROM donor_details WHERE blood_type = NEW.blood_type
            ON CONFLICT(blood_type) DO NOTHING;
        END;
    ''')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    print("Tables 'users', 'donor_details', 'hospital_requests', 'blood_availability', and trigger 'update_blood_availability' created successfully.")

# Run this function to create all the tables and trigger
create_tables()
