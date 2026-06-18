description	Create a single dummy user in the database
allowed-tools	Read, Bash(python3:*)
Read spendly.db to understand the users table schema and the get_db() helper.
Then write and run a Python script using Bash that:
1.	Generates a realistic random Indian user using your own knowledge of common Indian names across regions: 
o	Name: a realistic Indian first + last name
o	Email: derived from the name with a random 2-3 digit number suffix (e.g. rahul.sharma91@gmail.com)
o	Password: "password123" hashed with werkzeug's generate_password_hash
o	created_at: current datetime
2.	Checks if the generated email already exists in the users table. If it does, regenerate until unique.
3.	Inserts the user into the database using the same get_db() pattern found in db.py.
4.	Prints confirmation: 
o	id
o	name
o	email
