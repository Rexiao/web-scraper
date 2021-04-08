"""test module
"""
from __future__ import absolute_import
import re
import pytest
from src import create_app
from src.api import get_wrapped_val
@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # create a temporary file to isolate the database for each test
    app = create_app({"TESTING": True,})

    # create the database and load test data
    yield app


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

def test_index(client):
    """test start page
    """
    # test that viewing the page renders without template errors
    response = client.get("/")
    assert response.status_code == 200

def test_get_book_success(client):
    """test get book without error
    """
    # test that viewing the page renders without template errors
    response = client.get("/api/books?title=harr&ANDtitle=prsadawd")
    assert response.status_code == 200

def test_get_book_fail(client):
    """test get book with ugly data
    """
    # test that viewing the page renders without template errors
    response = client.get("/api/books?title=harr&Andtitle=prsadawd")
    assert response.status_code == 400

def test_put_success_1(client):
    """test put book withour error
    """
    # test that viewing the page renders without template errors
    response = client.put("/api/books?author=48627", data={'rating':4.11})
    # print(response)
    assert response.status_code == 200

def test_put_fail1(client):
    """test put book with ugly data
    """
    # test that viewing the page renders without template errors
    response = client.put("/api/books?author_id=48622", data={'rating':4.3})
    # print(response)
    assert response.status_code == 400

def test_put_fail2(client):
    """test put book with invalid attribute
    """
    # test that viewing the page renders without template errors
    response = client.put("/api/authors?author=48627", data={'rating':4.3})
    # print(response)
    assert response.status_code == 400

def test_put_success_2(client):
    """test put author
    """
    # test that viewing the page renders without template errors
    response = client.put("/api/authors?author_id=48622", data={'rating':4.3})
    # print(response)
    assert response.status_code == 200

def test_get_wrapped_val():
    """test get_wrapped_val when key is author_id
    """
    res = get_wrapped_val('author_id', 2, 'authors')
    assert res == 2

def test_get_wrapped_val_2():
    """test get_wrapped_val when key is title
    """
    res = get_wrapped_val('title', 'daw', 'books')
    assert res == {'$regex': re.compile('daw', re.I)}

def test_get_wrapped_val_3():
    """test get_wrapped_val when key is author_url
    """
    res = get_wrapped_val('author_url', '213,213,152', 'books')
    assert res == {'$in': ['213,213,152']}
