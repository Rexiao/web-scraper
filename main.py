"""main method where the program start
"""
from __future__ import absolute_import

import json
import time
import logging
import argparse
import sys

from urllib.request import urlopen
from bs4 import BeautifulSoup
import backend.web_parser as web_parser
import backend.db_wrapper as db_wrapper

class ScrapEngine:
    """class to wrap scarping procedure
    """
    def __init__(self, start_book_id, max_book_count, max_author_count):
        self.start_book_id = start_book_id
        self.max_book_count = max_book_count
        self.max_author_count = max_author_count
        self.result_dict = {'books': [], 'authors': []}
        is_normal = self.__scrap()
        if not is_normal:
            self.result_dict = None
    def get_result(self):
        if not self.result_dict:
            logging.error("something went wrong....")
        return self.result_dict
    def __scrap(self):
        is_normal = self.__scrap_book()
        if not is_normal:
            return False
        print("scrap {0} books succeeds".format(self.max_book_count))
        self.__scrap_author()
        print("scrap {0} authors succeeds".format(self.max_author_count))
        return True
    def __scrap_book(self):
        book_id_set = set([self.start_book_id])
        book_id_queue = []
        url = web_parser.PREFIX_BOOK_STR + str(self.start_book_id)
        try:
            page = urlopen(url)
        except:
            logging.error("invalid start book id")
            return False
        while True:
            if not page:
                url = web_parser.PREFIX_BOOK_STR + str(book_id_queue.pop(0))
                page = urlopen(url)
            html = page.read().decode("utf-8")
            soup = BeautifulSoup(html, "html.parser")
            my_book_parser = web_parser.MyBookParser(soup, url)
            book = my_book_parser.get_book_dic()
            self.result_dict['books'].append(book)
            #add next book ids
            for bid in book['similiar_books']:
                if bid not in book_id_set and len(book_id_set) < self.max_book_count:
                    book_id_set.add(bid)
                    book_id_queue.append(bid)
            if len(self.result_dict['books']) >= self.max_book_count or (not book_id_queue):
                break
            time.sleep(2)
            page = None
        return True
    def __scrap_author(self):
        author_id_set = set(self.result_dict['books'][0]['author'])
        author_id_queue = list(author_id_set)
        while True:
            url = web_parser.PREFIX_AUTHOR_STR + str(author_id_queue.pop(0))
            page = urlopen(url)
            html = page.read().decode("utf-8")
            soup = BeautifulSoup(html, "html.parser")
            my_author_parser = web_parser.MyAuthorParser(soup)
            author = my_author_parser.get_author_dic()
            self.result_dict['authors'].append(author)
            #add next author ids
            for aid in author['related_authors']:
                if aid not in author_id_set and len(author_id_set) < self.max_author_count:
                    author_id_set.add(aid)
                    author_id_queue.append(aid)
            if len(self.result_dict['authors']) >= self.max_author_count or (not author_id_queue):
                break
            time.sleep(2)

def import_wrapper(file_name):
    try:
        db_wrapper.import_json_to_db(file_name)
    except:
        logging.error('import failed')
        sys.exit()

if __name__ == "__main__":
    MY_PARSER = argparse.ArgumentParser('Scrap books and authors')
    MY_PARSER.add_argument('action',
                           metavar='import/export/scrap',
                           type=str,
                           help='the action to perform')
    MY_PARSER.add_argument('-f',
                           type=str,
                           help='file name')
    MY_PARSER.add_argument('-p',
                           '--param',
                           nargs=3,
                           type=int,
                           help='start book id, # of book to scrap, # of author to scrap')
    # MY_PARSER.add_argument('-s',
    #                        action='store_true',
    #                        help=('used when action = scrap.'
    #                              + 'Indicator of saving scrap result into js.json')
    #                       )
    ARGS = MY_PARSER.parse_args()
    if ARGS.action == 'export':
        #if args go wrong
        # if ARGS.param or ARGS.s:
        if ARGS.param:
            MY_PARSER.error('export should not have -param')
        if not ARGS.f:
            MY_PARSER.error('no file name specified')
        #perform the action
        try:
            db_wrapper.export_json_from_databse(ARGS.f)
        except:
            logging.error('export failed')
            sys.exit()
        print('export documents into' + ARGS.f)
    elif ARGS.action == 'import':
        #if args go wrong
        # if ARGS.param or ARGS.s:
        if ARGS.param:
            MY_PARSER.error('import should not have -param')
        if not ARGS.f:
            MY_PARSER.error('no file name specified')
        import_wrapper(ARGS.f)
        print('import documents into db.data')
    elif ARGS.action == 'scrap':
        #deal with args
        if not ARGS.param:
            MY_PARSER.error('scrap need three parameters')
        if ARGS.f:
            MY_PARSER.error('scrap does not need file location')
        #scrap
        start_bid, max_book, max_author = ARGS.param
        try:
            SCRAP_ENGINE = ScrapEngine(start_bid, max_book, max_author)
        except:
            print('scrap failed')
        DICT = SCRAP_ENGINE.get_result()
        if not DICT:
            print('scrap failed')
            sys.exit()
        else:
            try:
                with open('js.json', 'w') as js_file:
                    json.dump(DICT, js_file)
            except ValueError:
                print('convert to dict failed')
                sys.exit()
            db_wrapper.import_json_to_db('js.json')
            print('finish scrap and import')
    else:
        MY_PARSER.error("invalid action")

# scrapEngine = ScrapEngine(44936, 3, 2)
# import json
# d = None
# with open('js.json','r') as f:
#     d = json.load(f)
# print(json.dumps(d,indent=4))
