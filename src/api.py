"""api bluprint
"""
from __future__ import absolute_import
import re
import json
from flask import (
    abort, Response, Blueprint, request
)
from . import client

bp = Blueprint('api', __name__, url_prefix='/api')

BOOKS_ATTRIBUTS_LIST = ['book_url', 'book_id', 'title', 'ISBN', 'author_url', 'author',
                        'image_url', 'rating', 'rating_count', 'review_count', 'similiar_books']
AUTHORS_ATTRIBUTES_LIST = ['author_url', 'author_id', 'name', 'image_url', 'rating', 'rating_count',
                           'review_count', 'author_books', 'related_authors']
SINGLE_INT_LIST = ['book_id', 'ISBN', 'rating_count', 'review_count', 'author_id']
SINGLE_FLOAT_LIST = ['rating']
@bp.route('/test', methods=('GET', 'PUT'))
def test_func():
    """test function
    """
    # js = request.get_json()
    test_helper()
    return Response(
        response=json.dumps({'s':'s'}),
        status=200,
        mimetype="application/json"
    )
def test_helper():
    """utility function for test
    """
    abort(401)

@bp.route('/books', methods=('GET', 'POST', 'PUT'))
def books_func():
    """function for get/post/put books
    """
    database = client.get_db()
    if request.method == 'GET':
        cursor = get_cursor(database.books, request.args, 'books')
        if not cursor:
            abort(400)
        res = list(cursor)
        return Response(
            response=json.dumps(res),
            status=200,
            mimetype="application/json"
        )
    if request.method == 'PUT':
        js_dict = get_js_dict()
        return books_or_arthors_put_func(database.books, 'books', js_dict)
    if request.method == 'POST':
        return authors_or_books_post(database.books, 'books')

def get_js_dict():
    """helper function to get json file
    """
    if (request.content_type == 'application/json') ^ (request.get_json() is not None):
        abort(415)
    return request.get_json()
def authors_or_books_post(collection, colleciton_name):
    """helper function for POST for authors or books
    """
    js_dict = get_js_dict()
    if not js_dict:
        abort(415)
    success_num = 0
    for book in js_dict[colleciton_name]:
        if colleciton_name == 'books':
            book['_id'] = book['book_id']
        else:
            book['_id'] = book['author_id']
        try:
            insert_book_or_author(collection, colleciton_name, book)
            success_num += 1
        except:
            pass
    return Response(response=json.dumps({'success_num_of_insert':success_num}),
                    status=200 + (success_num != 0),
                    mimetype="application/json")

def insert_book_or_author(collection, collection_name, js_dict=None):
    """insert a single document into colleciton
    """
    pretty_form = js_dict
    if not pretty_form:
        is_valid_form, pretty_form = check_validity(dict(request.form), collection_name)
        if not is_valid_form: #bad request beacause of form data
            print("false")
            abort(400)
    else:
        if collection_name == 'books':
            js_dict['_id'] = js_dict['book_id']
        elif collection_name == 'authors':
            js_dict['_id'] = js_dict['author_id']
    if (collection_name == 'books' and len(pretty_form) != len(BOOKS_ATTRIBUTS_LIST) + 1) or \
            (collection_name == 'authors' and len(pretty_form) != len(AUTHORS_ATTRIBUTES_LIST) + 1):
        print(len(pretty_form))
        print(collection_name)
        abort(400, "lack of field when trying to insert")
    #try insert
    try:
        # insert_res = collection.insert_one(pretty_form)
        collection.insert_one(pretty_form)
    except:
        return Response(response=json.dumps({'message':"already exist"}),
                        status=200,
                        mimetype="application/json")
    return Response(response=json.dumps({'message':"create"}),
                    status=201,
                    mimetype="application/json")

def books_or_arthors_put_func(collection, collection_name, js_dict=None):
    """function used in PUT of books/authors
    """
    #number of arg must be 1
    if len(request.args) != 1:
        abort(400)
    cursor = get_cursor(collection, request.args, collection_name)
    if cursor is None:
        abort(400)
    res = list(cursor)
    if len(res) != 0: #no new document
        parsed_dict = parse_args(dict(request.args), collection_name)
        parsed_form = js_dict
        if not parsed_form:
            is_valid, parsed_form = check_validity(dict(request.form), collection_name)
            if not is_valid:
                abort(400)
        # raw_res = collection.update_one(parsed_dict, {'$set':parsed_form})
        collection.update_one(parsed_dict, {'$set':parsed_form})
        # print(raw_res)
        return Response(response=json.dumps({'message':'update'}),
                        status=200,
                        mimetype="application/json"
                       )
    #no macth
    return insert_book_or_author(collection, collection_name, js_dict)

def check_validity(form_dict, collection_name):
    """check if dict is valid to use based on collection name
    """
    res_dict = dict(form_dict)
    if collection_name == 'books':
        for key in form_dict:
            if key not in BOOKS_ATTRIBUTS_LIST:
                return False, None
            if key in ['author_url', 'author', 'similiar_books']:
                if key == 'author_url':
                    res_dict[key] = form_dict[key].split(',')
                else:
                    try:
                        res_dict[key] = [int(string) for string in form_dict[key].split(',')]
                    except ValueError:
                        return False, None
            elif key in SINGLE_INT_LIST:
                try:
                    res_dict[key] = int(form_dict[key])
                except ValueError:
                    return False, None
            elif key in SINGLE_FLOAT_LIST:
                try:
                    res_dict[key] = float(form_dict[key])
                except ValueError:
                    return False, None
        if 'book_id' in res_dict:
            res_dict['_id'] = res_dict['book_id']
    else:
        for key in form_dict:
            if key not in AUTHORS_ATTRIBUTES_LIST:
                return False, None
            if key in ['author_books', 'related_authors']:
                try:
                    res_dict[key] = [int(string) for string in form_dict[key].split(',')]
                except ValueError:
                    return False, None
            elif key in SINGLE_INT_LIST:
                try:
                    res_dict[key] = int(form_dict[key])
                except ValueError:
                    return False, None
            elif key in SINGLE_FLOAT_LIST:
                try:
                    res_dict[key] = float(form_dict[key])
                except ValueError:
                    return False, None
        if 'author_id' in res_dict:
            res_dict['_id'] = res_dict['author_id']
    return True, res_dict


def get_cursor(collection, arguments, colletion_name):
    """get cursor based on request.args
    """
    if len(arguments) > 2:
        return None
    parsed_dict = parse_args(dict(arguments), colletion_name)
    if parsed_dict is None: #cannot parse args
        return None
    # print(parsed_dict)
    cursor = collection.find(parsed_dict)
    return cursor

@bp.route('/authors', methods=('GET', 'POST', 'PUT'))
def authors_func():
    """function for get/post/put authors
    """
    database = client.get_db()
    if request.method == 'GET':
        cursor = get_cursor(database.authors, request.args, 'authors')
        if not cursor:
            abort(400)
        res = list(cursor)
        return Response(
            response=json.dumps(res),
            status=200,
            mimetype="application/json"
        )
    if request.method == 'PUT':
        return books_or_arthors_put_func(database.authors, 'authors')
    if request.method == 'POST':
        return authors_or_books_post(database.authors, 'authors')

def get_wrapped_val(key, val, collection_name):
    """wrap val to fit in mongodb style

    Args:
        key (string): original key
        val (int/string): original val

    Returns:
        int/string: modified val
    """
    if key == 'title': #substring
        pattern = re.compile(val, re.I)
        return {'$regex': pattern}
    if key in ['book_url', 'image_url', 'name'] or\
        (key == 'author_url' and collection_name == 'authors'): #exact string
        return val
    if (key == 'author_url' and collection_name == 'books'): #seach in array of string
        return {'$in': [val]}
    if key in ['rating']: #float
        try:
            float_val = float(val)
        except ValueError:
            return None
        return float_val
    if key in ['author_id', 'rating_count', 'review_count', 'book_id', 'ISBN']: #int
        try:
            int_val = int(val)
        except ValueError:
            return None
        return int_val
    if key in ['author_books', 'related_authors', 'author',
               'similiar_books']: #array of int
        try:
            int_val = int(val)
        except ValueError:
            return None
        return {'$in': [int_val]}
    #key is not valid
    return None

def parse_args(dictionary, colletion_name):
    """get dict used in db.find

    Args:
        dictionary (dict): raw dict

    Returns:
        dict: parsed dict
    """
    if len(dictionary) == 1: #only one attribute
        key_list = list(dictionary)
        key = key_list[0]
        val = get_wrapped_val(key, dictionary[key], colletion_name)
        return {key: val}
    op_str = None
    keys = []
    vals = []
    #extract operator: and / or
    for key in dictionary:
        if 'AND' in key:
            op_str = 'and'
            keys.append(key[3:])
        elif 'OR' in key:
            op_str = 'or'
            keys.append(key[2:])
        else:
            keys.append(key)
        new_val = get_wrapped_val(keys[-1], dictionary[key], colletion_name)
        if not new_val:
            return None
        else:
            vals.append(new_val)
    #two arrtibutes and no operator
    if not op_str:
        return None
    return {('$' + op_str): [{key: val} for key, val in zip(keys, vals)]}

@bp.route('/book', methods=('POST', 'DELETE'))
def book_func():
    """function for posting or deleting a single book
    """
    database = client.get_db()
    if request.method == 'POST':
        js_dict = get_js_dict()
        return insert_book_or_author(database.books, 'books', js_dict)
    if request.method == 'DELETE':
        return delete_wrapper(database.books, 'books')

def delete_wrapper(collection, colletion_name):
    """helper function used in delete
    """
    if len(request.args) != 1:
        abort(400, "too many or too few args")
    parsed_dict = parse_args(dict(request.args), colletion_name)
    delete_res = collection.delete_one(parsed_dict)
    if delete_res.deleted_count != 1:
        abort(400, "delete failed")
    else:
        return Response(response=json.dumps({'message':'delete succeed'}),
                        status=200,
                        mimetype="application/json"
                       )


@bp.route('/author', methods=('POST', 'DELETE'))
def author_func():
    """function for posting or deleting a single author
    """
    database = client.get_db()
    if request.method == 'POST':
        js_dict = get_js_dict()
        return insert_book_or_author(database.authors, 'authors', js_dict)
    if request.method == 'DELETE':
        return delete_wrapper(database.authors, 'authors')
        