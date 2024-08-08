from app import db,create_app

# Check the registered Flask app
app = create_app('testing')
registered_app = app

if registered_app is None:
    print("No Flask app is currently registered with this SQLAlchemy instance.")
else:
    print("Registered Flask app:", registered_app.name)
