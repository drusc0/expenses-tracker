# ./config.py
# Using this file and class to store some secrets
# Will add defaults, but this should be changed according to the stage

import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # debugging flask on
    DEBUG = True

    # secret key to avoid CSRF attacks
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    GOOGLE_APPLICATION_CREDENTIALS_FN = 'chase-expenses-6c9036e3b68b.json'
    if not os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.join.path(basedir, GOOGLE_APPLICATION_CREDENTIALS_FN)