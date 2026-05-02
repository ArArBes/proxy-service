#!/bin/sh

python manage.py migrate
python manage.py create_test_vms
exec "$@"