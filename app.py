from flask import Flask, render_template, request, jsonify, redirect, url_for
from config import Config
from User.Login import UserAuthDB

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    @app.route("/")
    def home():
        return render_template("login.html")

    @app.route("/api/echo", methods=["POST"])
    def echo():
        data = request.json
        return jsonify({"received": data})

    @app.route("/login", methods=["POST"])
    def login():
        try:
            user = UserAuthDB()
            # match form 'name' attributes from login.html
            email = request.form.get('email')
            password = request.form.get('password')

            if not email or not password:
                return redirect(url_for('home'))

            data = user.signin(email=email, password=password)
            if data.get('success'):
                user_info = data.get('user') or {}
                role = str(user_info.get('role') or '').lower()
                if role == 'admin':
                    return render_template("admin.html", user=user_info)
                return render_template("front.html", user=user_info)
            else:
                return redirect(url_for('home'))
        except Exception:
            return redirect(url_for('home'))

    @app.route("/signup", methods=["POST"])
    def signup():
        try:
            user = UserAuthDB()
            name = request.form.get('full_name')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm = request.form.get('confirm_password')

            if not (name and email and password and confirm):
                return redirect(url_for('home'))

            if password != confirm:
                return redirect(url_for('home'))

            # call whichever signup/register method exists on UserAuthDB
            if hasattr(user, 'signup'):
                data = user.signup(name=name, email=email, password=password)
            elif hasattr(user, 'register'):
                data = user.register(name=name, email=email, password=password)
            else:
                return jsonify({'error': 'Signup not implemented on backend'}), 501

            if data.get('success'):
                return render_template("front.html", user=data.get('user'))
            else:
                return redirect(url_for('home'))
        except Exception:
            return redirect(url_for('home'))
        
    @app.route("/admin")
    def admin_panel():
        # load users from backend (try multiple possible method names)
        try:
            userdb = UserAuthDB()
            if hasattr(userdb, 'list_users'):
                users = userdb.list_users()
            elif hasattr(userdb, 'get_all'):
                users = userdb.get_all()
            elif hasattr(userdb, 'all_users'):
                users = userdb.all_users()
            elif hasattr(userdb, 'fetch_users'):
                users = userdb.fetch_users()
            else:
                users = []
        except Exception:
            users = []
        return render_template("admin.html", users=users)

    @app.route("/admin/remove_user", methods=["POST"])
    def admin_remove_user():
        try:
            userdb = UserAuthDB()
            # prefer an id, fallback to email
            user_id = request.form.get('user_id')
            email = request.form.get('email')

            # try common deletion method names
            result = None
            if user_id:
                if hasattr(userdb, 'delete_user'):
                    result = userdb.delete_user(user_id=user_id)
                elif hasattr(userdb, 'remove'):
                    result = userdb.remove(id=user_id)
                elif hasattr(userdb, 'delete'):
                    result = userdb.delete(user_id)
            elif email:
                if hasattr(userdb, 'delete_user'):
                    result = userdb.delete_user(email=email)
                elif hasattr(userdb, 'remove_user'):
                    result = userdb.remove_user(email=email)
                elif hasattr(userdb, 'delete_by_email'):
                    result = userdb.delete_by_email(email)
                elif hasattr(userdb, 'delete'):
                    result = userdb.delete(email)
            else:
                return redirect(url_for('admin_panel', msg="No identifier provided"))

            # interpret result
            if result is None:
                # assume success if method returned nothing but didn't raise
                return redirect(url_for('admin_panel', msg="User removed"))
            if isinstance(result, dict):
                if result.get('success'):
                    return redirect(url_for('admin_panel', msg="User removed"))
                else:
                    return redirect(url_for('admin_panel', msg=result.get('message') or 'Remove failed'))
            # otherwise assume truthy means success
            if result:
                return redirect(url_for('admin_panel', msg="User removed"))
            return redirect(url_for('admin_panel', msg="Remove failed"))
        except Exception as e:
            return redirect(url_for('admin_panel', msg="Error removing user"))

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
