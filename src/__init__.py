"""start file for flask
"""
from __future__ import absolute_import

import json
import re
import pymongo
import requests

from flask import (Flask, redirect, request, Response, render_template, url_for)
from src import client
import src.backend.db_wrapper as db_wrapper
from . import client

PREFIX_URL = 'http://127.0.0.1:5000'
def create_app(test_config=None):
    """constructor of flask
    """
    app = Flask(__name__)

    # app.run(debug=True)
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.update(test_config)

    client.init_app(app)

    from . import api, query, vis
    app.register_blueprint(api.bp)
    app.register_blueprint(query.bp)
    app.register_blueprint(vis.bp)

    @app.route('/', methods=('GET', 'POST'))
    def hello_world():
        if request.method == 'POST':
            element_id = None
            if 'book_id' in request.form:
                element_id = request.form['book_id']
                return redirect(url_for('crud_book', book_id=element_id))
            elif 'author_id' in request.form:
                element_id = request.form['author_id']
                return redirect(url_for('crud_author', author_id=element_id))
            else:
                render_template('index.html')
        return render_template('index.html')
    @app.route('/books')
    def display_book():
        database = client.get_client().data
        elements = list(database.books.find({}))
        return render_template('display.html', elements=elements)

    @app.route('/authors')
    def display_author():
        database = client.get_client().data
        elements = list(database.authors.find({}))
        return render_template('display.html', elements=elements)

    @app.route('/book/<int:book_id>', methods=('GET', 'PUT', 'POST', 'DELETE'))
    def crud_book(book_id):
        if request.method == 'GET':
            # print(url_for('api.books_func', book_id=book_id))
            res = requests.get(PREFIX_URL + url_for('api.books_func', book_id=book_id))
            # res = requests.get(PREFIX_URL + url_for('api.books_func'))
            js_dict = None
            if res.headers['Content-Type'] == 'application/json':
                js_dict = res.json()
            return render_template('crud.html', elements=js_dict)
    @app.route('/author/<int:author_id>', methods=('GET', 'POST'))
    def crud_author(author_id):
        if request.method == 'GET':
            # print(url_for('api.books_func', book_id=book_id))
            res = requests.get(PREFIX_URL + url_for('api.authors_func', author_id=author_id))
            # res = requests.get(PREFIX_URL + url_for('api.books_func'))
            js_dict = None
            if res.headers['Content-Type'] == 'application/json':
                js_dict = res.json()
            return render_template('crud.html', elements=js_dict)
        # if request.method == 'POST':
        #     js_dict = dict(request.form)
    return app
