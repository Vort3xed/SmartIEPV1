# SmartIEP
Simple database webapp for student IEP's

## Please note:
~~Due to security risks, the DATABASE_URI has been changed on heroku. This means that the website will not be able to connect to the PostgreSQL database and will not function properly. This functionality will be re-implemented at the end of August.~~

SMARTIEP IS BACK UP!!! The database (and app) are now both deployed on render.com. The app is currently running on a free tier, so it may take a few seconds to load. If you have any questions, please contact me. Render may also expire the database, so please contact me if the database is down (if you get an "internal server error"). The contact email in the contact-us page is also abandoned, do not try to email that (email me instead).

https://smartiep.onrender.com

## Future Reference:
- python3 -m flask shell
- from app import Accounts
- from werkzeug.security import generate_password_hash
- account = Accounts(callname='administrator',username='administrator@mcpsmd.net',password=generate_password_hash('pword'))
- db.session.add(account)
- db.session.commit()

### Place EXTERNAL database URI into .env
