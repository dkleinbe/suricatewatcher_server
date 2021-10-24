web: gunicorn --worker-class eventlet -w 1 server:app --log-level=debug --error-logfile gunicorn.error.log --access-logfile gunicorn.log --capture-output

