'''This module acts as a layer between views and database models.
It provides functions to do relevant database operations.'''

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from database_setup import Base, User, Category, Item


engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


def get_categories():
    categories = session.query(Category).all()
    return categories


def get_category(category_id=None):
    if category_id:
        try:
            category = session.query(Category).filter_by(id=category_id).one()
            return category
        except NoResultFound:
            return None
    else:
        category = session.query(Category).first()
        return category


def get_latest_items(limit=10):
    items = session.query(Item).order_by(Item.id.desc())
    return items[:limit]


def get_items(category_id):
    items = session.query(Item).filter_by(category_id=category_id)
    return items


def get_item_by_id(item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    return item


def get_item(category_id, item_id):
    item = session.query(Item).filter_by(
        category_id=category_id, id=item_id).one()
    return item


def create_item(category_id, user_id, name, description, picture=None):
    item = Item(category_id=category_id,
                user_id=user_id,
                name=name,
                description=description,
                picture=picture)
    session.add(item)
    session.commit()


def edit_item(item_id, category_id, name, description, picture):
    item = get_item_by_id(item_id)
    item.category_id = category_id
    if name:
        item.name = name
    if description:
        item.description = description
    if picture:
        item.picture = picture
    session.add(item)
    session.commit()
    return item


def delete_item(category_id, item_id):
    item = get_item(category_id, item_id)
    session.delete(item)
    session.commit()


def create_user(login_session):
    user = User(name=login_session['username'], email=login_session[
        'email'], picture=login_session['picture'])
    session.add(user)
    session.commit()
    return user.id


def get_user(user_id):
    try:
        user = session.query(User).filter_by(id=user_id).one()
        return user
    except NoResultFound:
        return None


def get_user_id(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except NoResultFound:
        return None
