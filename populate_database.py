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

items = [
    Item(name='Zero to One: Notes on Startups, or How to Build the Future',
         description='Peter Thiel, 2014', picture='item1.jpg', category_id=1, user_id=1),
    Item(name='The Hard Thing About Hard Things: Building a Business When There Are No Easy Answers',
         description='Ben Horowitz, 2014', picture='item2.jpg', category_id=1, user_id=1),
    Item(name='Patterns of Enterprise Application Architecture',
         description='Martin Fowler, 2002', picture='item3.jpg', category_id=1, user_id=1),
    Item(name='The Martian', description='Ridley Scott, 2015\nDuring a manned mission to Mars, Astronaut Mark Watney is presumed dead after a fierce storm and left behind by his crew. But Watney has survived and finds himself stranded and alone on the hostile planet. With only meager supplies, he must draw upon his ingenuity, wit and spirit to subsist and find a way to signal to Earth that he is alive.', picture='item4.jpg', category_id=2, user_id=1),
    Item(name='Star Wars: The Force Awakens', description='J.J. Abrams, 2015\nThree decades after the defeat of the Galactic Empire, a new threat arises. The First Order attempts to rule the galaxy and only a ragtag group of heroes can stop them, along with the help of the Resistance.', picture='item5.jpg', category_id=2, user_id=1),
    Item(name='Inside Out', description='Pete Docter, Ronnie Del Carmen, 2015\nAfter young Riley is uprooted from her Midwest life and moved to San Francisco, her emotions - Joy, Fear, Anger, Disgust and Sadness - conflict on how best to navigate a new city, house, and school.', picture='item6.jpg', category_id=2, user_id=1),
    Item(name='Silicon Valley', description='HBO, 2014- \nIn the high-tech gold rush of modern Silicon Valley, the people most qualified to succeed are the least capable of handling success. A comedy partially inspired by Mike Judge\'s own experiences as a Silicon Valley engineer in the late 1980s.',
         picture='item7.jpg', category_id=3, user_id=1),
    Item(name='Dexter', description='SHO, 2006-2013.\nA Miami police forensics expert moonlights as a serial killer of criminals whom he believes have escaped justice.',
         picture='item8.jpg', category_id=3, user_id=1),
    Item(name='Breaking Bad', description='AMC, 2008-2013\nA chemistry teacher diagnosed with terminal lung cancer teams up with his former student to cook and sell crystal meth.',
         picture='item9.jpg', category_id=3, user_id=1),
    Item(name='The Dark Side of the Moon', description='Pynk Floyd, 1973',
         picture='item10.jpg', category_id=4, user_id=1),
    Item(name='Let It Bleed', description='The Rolling Stones, 1969',
         picture='item11.jpg', category_id=4, user_id=1),
    Item(name='Sgt. Pepper\'s Lonely Hearts Club Band',
         description='The Beatles, 1967', picture='item12.jpg', category_id=4, user_id=1)
]

session.bulk_save_objects(items)
session.commit()

print 'Database is successfully setup and populated.'
