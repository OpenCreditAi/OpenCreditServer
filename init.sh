
#!/bin/bash

# Initialize migrations if they don't exist
if [ ! -d migrations ]; then
    flask db init
fi

# Create and apply migrations
flask db migrate -m "initial migration"
flask db upgrade

# Check if database is already populated
python -c "
from app import create_app
from app.models import Organization
app = create_app()
with app.app_context():
    if not Organization.query.first():
        from app.populate_db import populate
        populate()
"

# Start the server
gunicorn --bind 0.0.0.0:5000 run:app