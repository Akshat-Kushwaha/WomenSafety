from pymongo import MongoClient
import hashlib

# Dummy credentials
admin_id = "admin"
password = "admin123"  # dummy password

# Hash the password (recommended)
hashed_password = hashlib.sha256(password.encode()).hexdigest()

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["WaspAdmin"]
users = db["User"]

admin_data = {
    "_id": admin_id,
    "name": "Super Admin",
    "email": "admin@wasp.com",
    "password": hashed_password,
    "role": "Admin"
}
client.close()

# Insert admin
users.insert_one(admin_data)

print("Dummy Admin Created!")
print("ID:", admin_id)
print("Password:", password)

