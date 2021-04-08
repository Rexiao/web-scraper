"""
parse content from website into JSONfile
"""
from __future__ import absolute_import

import re
import logging
import time

from urllib.request import urlopen
from bs4 import BeautifulSoup
# dictiontionly to convert property value in html to key in book dictionary
BOOK_PROPERTY_TO_KEY_DICT = {'og:title': 'title',
                             'books:isbn': 'ISBN',
                             'books:author': 'author_url',
                             'og:image': 'image_url'
                            }
AUTHOR_PROPERTY_TO_KEY_DICT = {'og:title': 'name',
                               'og:image':'image_url'
                               }
#prefix string used in get_book_id
PREFIX_BOOK_STR = 'https://www.goodreads.com/book/show/'
PREFIX_AUTHOR_STR = 'https://www.goodreads.com/author/show/'
PREFIX_BOOK_COVER = 'bookCover_'
# PREFIX_AUTHOR_STR = 'https://www.goodreads.com/author/show/'
PREFIX_SIMILAR_AUTHOR_STR = 'https://www.goodreads.com/author/similar/'
PREFIX_REACT_STR = '\"id\":'
class MyBookParser:
    """Class for wrap utility function to parse a url to a dictionary for book
    """
    def __init__(self, soup, url):
        self.url = url
        self.soup = soup
        self.book_dic = self.__parse_html_to_dict()
    def get_book_dic(self):
        """get resulf of parsing

        Returns:
            dictionary: a dictionary containing all required fields
        """
        return self.book_dic
    def __parse_html_to_dict(self):
        """parse a html string to a dictionary which will be converted to JSON

        Args:
            soup (BeautifulSoup): BeautifulSoup object containing info
        Returns:
            book dictionary
        """
        book_dic = dict()
        #deal with book_url and book_id first because they are more complex
        # link_str = self.soup.find_all('link', rel='canonical')[0]['href']
        book_dic['book_url'] = self.url
        book_dic['book_id'] = MyBookParser.get_book_id(PREFIX_BOOK_STR, self.url)
        #for mongodb
        book_dic['_id'] = book_dic['book_id']
        #deal with other attributes
        for property_val in BOOK_PROPERTY_TO_KEY_DICT:
            temp_list = self.soup.find_all('meta', property=property_val)
            # if len(temp_list) != 1:
            #     val = ''
            # else:
            #     val = temp_list[0]['content']
            val = temp_list[0]['content']
            #deal with author seperately since its value is array
            if property_val == 'books:author':
                #arthor url
                author_url_list = []
                for tag in temp_list:
                    author_url_list.append(tag['content'])
                book_dic[BOOK_PROPERTY_TO_KEY_DICT[property_val]] = author_url_list
                #author
                book_dic['author'] = self.get_author_id_array(PREFIX_AUTHOR_STR, author_url_list)
            else:
                book_dic[BOOK_PROPERTY_TO_KEY_DICT[property_val]] = val
        #deal with rating
        tri_list = MyBookParser.get_rating_attributes(self.soup, 'meta')
        for idx, key in enumerate(['rating', 'rating_count', 'review_count']):
            book_dic[key] = tri_list[idx]
        #getsimilarbook
        book_dic['similiar_books'] = self.__get_similar_ids()
        return book_dic
    @staticmethod
    def get_author_id_array(prefix_str, array):
        """remove prefix string from each string in the array

        Args:
            prefix_str (str): common prefix_str which should be exptected to exist in array
            array ([type]): string array

        Returns:
            [int]: array of integer
        """
        res_list = []
        for href_str in array:
            res_list.append(MyBookParser.get_book_id(prefix_str, href_str))
        return res_list
    @staticmethod
    def get_book_id(prefix_str, href_str):
        """get id from a href string

        Args:
            prefix_str (str): string before id
            href_str (str): a string containg a url
        Returns:
            -42 if the function fails because re.findall fails
                if the function fails because id_str is empty
            a list of postive numbers otherwise
        """
        one_element_list = re.findall(prefix_str + '[0-9]*', href_str)
        if len(one_element_list) != 1:
            logging.error("re.findall fails when dealing with id")
            return -42
        #remove all chars afer book_id
        pretty_string = one_element_list[0]
        #get book id str
        id_str = pretty_string[len(prefix_str):]
        if not id_str:
            logging.error("id_str is empty")
            return -42
        return int(id_str)
    @staticmethod
    def get_rating_attributes(soup, rating_number_tag_str):
        """get rating, rating_count, review_count

        Returns:
            list : [float, int, int]
        """
        return_list = []
        #get rating
        rating_tag = soup.find_all('span', itemprop="ratingValue")
        if len(rating_tag) != 1:
            return_list.append('')
        else:
            number_str = rating_tag[0].getText()
            return_list.append(float(number_str.strip()))
        #get number of rating and review count
        for itemprop_val in ['ratingCount', 'reviewCount']:
            rating_nuber_tag = soup.find_all(rating_number_tag_str, itemprop=itemprop_val)
            if len(rating_tag) != 1:
                return_list.append('')
            else:
                # number_str = rating_nuber_tag[0].getText()
                # #remove space commas and new lines
                # number_with_comma = number_str.strip().split("\n ")[0]
                # return_list.append(int(number_with_comma.replace(',', '')))
                number_str = rating_nuber_tag[0]['content']
                return_list.append(int(number_str))
        return return_list
    def __get_similar_ids(self):
        res_list = []
        for tag in self.soup.find_all('li', {'class':'cover'}):
            raw_str = tag['id']
            num_str = raw_str[len(PREFIX_BOOK_COVER):]
            res_list.append(int(num_str))
        return res_list

class MyAuthorParser:
    """Class for wrap utility function to parse a url to a dictionary for author
    """
    def __init__(self, soup):
        self.soup = soup
        self.author_dic = dict()
        time.sleep(2)
        self.__parse_html_to_dict()
    def get_author_dic(self):
        """get resulf of parsing author url

        Returns:
            dictionary: a dictionary containing all required fields of one author
        """
        return self.author_dic
    def __parse_html_to_dict(self):
        #deal with author_url and author_id first
        link_str = self.soup.find_all('link', rel='canonical')[0]['href']
        self.author_dic['author_url'] = link_str
        self.author_dic['author_id'] = MyBookParser.get_book_id(PREFIX_AUTHOR_STR, link_str)
        #for mongo db
        self.author_dic['_id'] = self.author_dic['author_id']
        #deal with other attributes
        for property_val in AUTHOR_PROPERTY_TO_KEY_DICT:
            temp_list = self.soup.find_all('meta', property=property_val)
            val = temp_list[0]['content']
            self.author_dic[AUTHOR_PROPERTY_TO_KEY_DICT[property_val]] = val
        #deal with rating
        tri_list = MyBookParser.get_rating_attributes(self.soup, 'span')
        for idx, key in enumerate(['rating', 'rating_count', 'review_count']):
            self.author_dic[key] = tri_list[idx]
        #author_books
        author_books_list = []
        tag_list = self.soup.find_all('div', {'class':"u-anchorTarget"})
        for tag in tag_list:
            author_books_list.append(int(tag['id']))
        self.author_dic['author_books'] = author_books_list
        #get related authors and author books
        self.author_dic['related_authors'] = self.__get_related_authors()
    def __get_related_authors(self):
        author_id_str = str(self.author_dic['author_id'])
        url = PREFIX_SIMILAR_AUTHOR_STR + author_id_str
        page = urlopen(url)
        html = page.read().decode("utf-8")
        similar_author_soup = BeautifulSoup(html, "html.parser")
        res_set = set()
        #find all ids
        search_dic = {'data-react-class':"ReactComponents.SimilarAuthorsList"}
        for tag in similar_author_soup.find_all('div', search_dic):
            text = tag['data-react-props']
            raw_list = re.findall("\"id\":[0-9]*", text)
            for raw_str in raw_list:
                num_str = raw_str[len(PREFIX_REACT_STR):]
                if num_str != author_id_str:
                    res_set.add(int(num_str))
        return list(res_set)


#mp = MyBookParser(soup)
#mp.get_book_dic()
#print(json.dumps(mp.get_book_dic(),indent = 4))
# mp = MyAuthorParser(soup)
# print(json.dumps(mp.get_author_dic(),indent = 4))
