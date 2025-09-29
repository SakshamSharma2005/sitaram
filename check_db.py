import sqlite3

# Connect to database
conn = sqlite3.connect('certs.db')
cursor = conn.cursor()

# Check for USN 1BG19CS100
print("=== Searching for USN 1BG19CS100 ===")
cursor.execute('SELECT usn, name, father_name FROM certificates WHERE usn = ?', ('1BG19CS100',))
results = cursor.fetchall()
print(f'Direct search results: {len(results)} records')
for row in results:
    print(f'USN: {row[0]}, Name: {row[1]}, Father: {row[2]}')

# Check table schema
print("\n=== Table Schema ===")
cursor.execute('PRAGMA table_info(certificates)')
schema = cursor.fetchall()
for col in schema:
    print(f'{col[1]} ({col[2]})')

# Check all USNs starting with 1BG19CS1
print("\n=== All USNs starting with 1BG19CS1 ===")
cursor.execute('SELECT usn, name FROM certificates WHERE usn LIKE ? LIMIT 10', ('1BG19CS1%',))
results = cursor.fetchall()
for row in results:
    print(f'USN: {row[0]}, Name: {row[1]}')

# Check if reg_no column has the USN
print("\n=== Checking reg_no column ===")
cursor.execute('SELECT reg_no, name FROM certificates WHERE reg_no LIKE ? LIMIT 10', ('1BG19CS1%',))
results = cursor.fetchall()
for row in results:
    print(f'Reg No: {row[0]}, Name: {row[1]}')

conn.close()