# Item Catalog

This is Project 3 of Full Stack Web Developer Nanodegree.

It implements a web application that allows authenticated user to add, edit or delete items to four categories: book, movie, TV series, and album. Unauthenticated user is only able to view the items. It can be viewed as an extremely simplified version of the Chinese website: [douban](http://www.douban.com).

This project is developed with HTML, CSS and javascript in the front end, and Python (Flask and SQLAlchemy) in the back end.

## Installation

1. Install Vagrant and VirtualBox.

2. Clone the [fullstack-nanodegree-vm](https://github.com/udacity/fullstack-nanodegree-vm) repository.

3. Download this repository

Click either "Clone in Desktop" or "Download ZIP" to the right, and move the repository to fullstack-nanodegree-vm/vagrant folder (Step 2).

4. Setup the database
```
    # In the terminal:
    # Go to the downloaded repository folder.
    cd item_catalog
    # Set up and populate the database
    python populate_database.py
```
It should print "Database is successfully setup and populated."

5. Run the application
```
    # In the terminal:
    # Launch and connect to the Vagrant VM
    vagrant up
    vagrant ssh
    # Run the application
    cd /vagrant/item_catalog
    python application.py
```
6. Access the application

Visit [http://localhost:8000](http://localhost:8000)

## Features

1. CRUD functionalities

Straightforward interface for user to create, read, update or delete items.
It fully supports uploading, changing and displaying an item image.

2. Authentication and authorization

Support third-party (Google and Facebook) log-in. Only authenticated user is able to create, edit or delete items. Unauthenticated user can view the items. User can only edit or delete his/her own items.

3. API

User can access all the data through JSON endpoints.

All data:

[http://localhost:8000/catalog.json](http://localhost:8000/catalog.json)

Single category data:

[http://localhost:8000/category/1/book/items.json](http://localhost:8000/category/1/book/items.json)
[http://localhost:8000/category/2/movie/items.json](http://localhost:8000/category/2/movie/items.json)
[http://localhost:8000/category/3/tv-series/items.json](http://localhost:8000/category/3/tv-series/items.json)
[http://localhost:8000/category/4/album/items.json](http://localhost:8000/category/4/album/items.json)

Single item data:

[http://localhost:8000/category/1/book/1.json](http://localhost:8000/category/1/book/1.json)
[http://localhost:8000/category/2/movie/4.json](http://localhost:8000/category/2/movie/4.json)
