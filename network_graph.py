"""module for generating and displaying graph
"""
from __future__ import absolute_import

import json
import networkx as nx
import matplotlib.pyplot as plt

def import_js_file():
    res_dict = None
    try:
        with open('js.json', 'r') as js_file:
            res_dict = json.load(js_file)
    except:
        return None
    return res_dict

def contruct_graph():
    dictionary = import_js_file()
    if not dictionary:
        print("import js.json fails")
        return False
    books = dictionary['books']
    authors = dictionary['authors']
    #create graph
    graph = nx.Graph()
    #create node
    for book in books:
        string = "book" + str(book['_id'])
        graph.add_node(string, **book)
    for author in authors:
        string = "author"+str(author['_id'])
        graph.add_node(string, **author)
    #add book edges
    for book in books:
        string = "book" + str(book['_id'])
        #connect to its authors
        for author_id in book['author']:
            second_str = "author" + str(author_id)
            if graph.has_node(second_str):
                edge = (string, "author" + str(author_id))
                graph.add_edge(*edge)
        for similar_book_id in book['similiar_books']:
            second_str = "book" + str(similar_book_id)
            if graph.has_node(second_str):
                edge = (string, "book" + str(similar_book_id))
                graph.add_edge(*edge)
    #add author edges
    for author in authors:
        string = "author" + str(author['_id'])
        #connect to its authors
        for book_id in author['author_books']:
            second_str = "book" + str(book_id)
            if graph.has_node(second_str):
                edge = (string, "book" + str(book_id))
                graph.add_edge(*edge)
        for related_author_id in author['related_authors']:
            second_str = "author" + str(related_author_id)
            if graph.has_node(second_str):
                edge = (string, "author" + str(related_author_id))
                graph.add_edge(*edge)
    #draw graph
    nx.draw(graph, with_labels=True, font_weight='bold')
    return True

if __name__ == "__main__":
    RES_BOOL = contruct_graph()
    if RES_BOOL:
        plt.show()
