from pymongo import MongoClient
from bson.objectid import ObjectId
import hashlib
import uuid


class UserAuthDB:
    def __init__(self, uri="mongodb+srv://akshatcbr05:iZV9JOcTrmMMj6mm@cluster0.kl3i9.mongodb.net/"):
        self.client = MongoClient(uri)
        self.db = self.client["WaspAdmin"]
        self.users = self.db["User"]
        self.sessions = self.db["Sessions"]

    # -------------------------
    # HASH PASSWORD
    # -------------------------
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    # -------------------------
    # SIGNUP
    # -------------------------
    def signup(self, name, email, password, role="User"):
        # Prevent duplicate account
        if self.users.find_one({"email": email}):
            return {"success": False, "message": "Email already registered"}

        hashed = self.hash_password(password)

        user = {
            "name": name,
            "email": email,
            "password": hashed,
            "role": role  # "Admin" or "User"
        }

        user_id = self.users.insert_one(user).inserted_id
        return {"success": True, "user_id": str(user_id)}

    # -------------------------
    # SIGNIN
    # -------------------------
    def signin(self, email, password):
        hashed = self.hash_password(password)

        user = self.users.find_one({"email": email, "password": hashed})
        if not user:
            return {"success": False, "message": "Invalid credentials"}

        # Create session token
        token = str(uuid.uuid4())
        self.sessions.insert_one({
            "user_id": str(user["_id"]),
            "token": token
        })

        return {
            "success": True,
            "token": token,
            "user": {
                "id": str(user["_id"]),
                "name": user["name"],
                "email": user["email"],
                "role": user["role"]
            }
        }

    # -------------------------
    # SIGNOUT
    # -------------------------
    def signout(self, token):
        result = self.sessions.delete_one({"token": token})
        if result.deleted_count > 0:
            return {"success": True, "message": "Signed out successfully"}
        else:
            return {"success": False, "message": "Invalid token"}

    # -------------------------
    # CHECK LOGIN
    # -------------------------
    def is_logged_in(self, token):
        session = self.sessions.find_one({"token": token})
        return session is not None

    # -------------------------
    # CHECK IF USER IS ADMIN
    # -------------------------
    def is_admin(self, token):
        session = self.sessions.find_one({"token": token})
        if not session:
            return False  # Not logged in

        user = self.users.find_one({"_id": ObjectId(session["user_id"])})
        if user and user.get("role") == "Admin":
            return True

        return False

    # -------------------------
    # CLOSE DB
    # -------------------------
    def __del__(self):
        self.client.close()
