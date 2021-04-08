"""query blueprint
"""
from __future__ import absolute_import
from flask import (
    Blueprint, render_template
)
from . import client
bp = Blueprint('query', __name__, url_prefix='/query')

@bp.route('/most-book-authors')
def get_most_book_authors():
    """function for getting most-book-authors
    """
    db = client.get_db()
    collection = db.authors
    pipeline = [
        {'$project':{'answers_count':{'$size':'$author_books'}}},
        {'$sort':{"answers_count":-1}}
    ]
    res_list = list(collection.aggregate(pipeline))
    max_count = res_list[0]['answers_count']
    # print(res_list)
    cursor = collection.find({'author_books':{'$size': max_count}})
    return render_template('display.html', elements=list(cursor))

@bp.route('/most-similar-books')
def get_most_similar_books():
    """function for gettting most_similar_books
    """
    db = client.get_db()
    collection = db.books
    pipeline = [
        {'$project':{'answers_count':{'$size':'$similiar_books'}}},
        {'$sort':{"answers_count":-1}}
    ]
    res_list = list(collection.aggregate(pipeline))
    max_count = res_list[0]['answers_count']
    # print(res_list)
    cursor = collection.find({'similiar_books':{'$size': max_count}})
    return render_template('display.html', elements=list(cursor))
