import os

CSRF_ENABLED = True
SECRET_KEY = 'fhg503SLd34SFFKA45876VMB667'

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'mysql://password:username@localhost/panSocial'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
