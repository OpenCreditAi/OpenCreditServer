#!/bin/bash

# Initialize migrations if they don't exist
if [ ! -d migrations ]; then
    flask db init
fi

# Create and apply migrations
flask db migrate -m "initial migration"
flask db upgrade

# Populate the database
python -c "
from app import create_app
from app.populate_db import populate
app = create_app()
with app.app_context():
    populate()
"

# Start the server
gunicorn --bind 0.0.0.0:8000 run:app 