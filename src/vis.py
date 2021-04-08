"""vis blueprint
"""
from __future__ import absolute_import
import json
from flask import (
    Blueprint, render_template
)
from . import client
bp = Blueprint('vis', __name__, url_prefix='/vis')

@bp.route('/rank-authors')
def get_rank_authors():
    """function to get authors rank base on rating
    """
    db = client.get_db()
    collection = db.authors
    pipeline = [
        {'$sort':{"rating":-1}},
        {'$project':{'rating':'$rating', 'name':'$name', '_id': 0}},
        {'$limit':15}
    ]
    res_list = list(collection.aggregate(pipeline))
    # print(res_list)
    return render_template('rank_author.html', elements=json.dumps(res_list))
    # return render_template('display.html', elements=res_list)

@bp.route('/rank-books')
def get_rank_books():
    """function to get books rank base on review number
    """
    db = client.get_db()
    collection = db.books
    pipeline = [
        {'$sort':{"review_count":-1}},
        {'$project':{'review_count':'$review_count', 'name':'$title', '_id': 0}},
        {'$limit':15}
    ]
    res_list = list(collection.aggregate(pipeline))
    # print(res_list)
    return render_template('rank_book.html', elements=json.dumps(res_list))
