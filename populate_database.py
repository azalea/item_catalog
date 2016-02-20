import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

user = User(name='Azalea', email='azalea@example.com',
            picture='https://octodex.github.com/images/welcometocat.png')
session.add(user)
session.commit()

categories = [
    Category(name='Book', glyphicon='glyphicon-book'),
    Category(name='Movie', glyphicon='glyphicon-film'),
    Category(name='TV series', glyphicon='glyphicon-hd-video'),
    Category(name='Album', glyphicon='glyphicon-music'),
]
session.bulk_save_objects(categories)

items = []
# populate items through json data in 'catalog.json'
json_data = json.loads(open('catalog.json').read())
category_data = json_data['Category']
for category in category_data:
    items.extend([Item(**item_data) for item_data in category['items']])

session.bulk_save_objects(items)
session.commit()

print 'Database is successfully setup and populated.'
