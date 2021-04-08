# Prerequisites

python version: 3.7 or above  
preferred IDE: Visual Studio Code  
preferred OS: Windows 10

## Installation and Setup

### Get the repository

    git clone https://gitlab.engr.illinois.edu/angl2/fa20-cs242-assignment2
    
### Import packages

    use `pip install -e .` to install app

<div style="page-break-after: always;"></div>

### Running

    set FLASK_APP=src 
    flask run

## Operations and results

### GET

#### get book based on single attribute

![](images/get1.png)

#### get book based on two attributes(and)

![](images/get2.png)

#### get book based on two attributes(or)

![](images/get3.png)

#### get author based on two attributes(and)

![](images/get4.png)

#### get author based on two attributes(or)

![](images/get5.png)

### PUT

#### for book (no new document)

![](images/put1.png)

#### for book (create new document)

![](images/put2.png)

#### if user create agiain, the client will only update insted of creating

![](images/put3.png)

#### for author (create new document)

![](images/put4.png)

### POST

#### post several books

![](images/post2.png)

#### post the same two books agian: return 0

![](images/post3.png)

#### post several authors

![](images/post1.png)

#### if content-type is not json, abort(415)

![](images/post4.png)

#### post a book

![](images/post5.png)

#### post an author
![](images/post6.png)

### DELETE

#### delete author which I created for testing posting an author

![](images/delete1.png)

#### delete book which I created for testing posting a book

![](images/delete2.png)
