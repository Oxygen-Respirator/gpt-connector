#!/bin/bash

# Run the first command
python manage.py runserver 0.0.0.0:8000 &

# Run the second command
python3 manage.py kafka-executor &

# Wait until the above two commands finish
wait