1. Install python3 + pip (eventually in conda environment)
2. Install the packages in 'python_packages.txt' using 'pip install'
3. Install the redis server (Debian: sudo apt install redis-server)
4. Setup the Django-System using 'python manage.py migrate' in 'shoppinglist'
5. Add an Admin-User using 'python manage.py creatsuperuser'
6. Start server using 'python manage.py runserver'

Optional:
6. Eventually activate the email sending service.
7. Add stores in your browser via ('http://serveradress/admin', for debugging: 'http://localhost/admin)
