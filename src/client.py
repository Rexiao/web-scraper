"""utility module for connecting database with flask
"""
from __future__ import absolute_import
import src.backend.db_wrapper as db_wrapper

CLIENT = None

def get_client():
    """get client object
    """
    global CLIENT
    if not CLIENT:
        CLIENT = db_wrapper.connect_to_database()
    return CLIENT

def get_db():
    """get database object
    """
    client = get_client()
    return client.data

def close_client(e=None):
    """function to close client
    """
    client = get_client()
    if client:
        client.close()

def init_app(app):
    """function used when initializing flask
    """
    app.teardown_appcontext(close_client)
