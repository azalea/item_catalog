from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from utils import slugify

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    glyphicon = Column(String(80))

    @property
    def slug(self):
        return slugify(self.name)

    @property
    def serialize(self):
        # returns object in an easily serializable format
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'items': [item.serialize for item in self.items]
        }


class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(250))
    picture = Column(String(250))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category, backref='items')
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def slug(self):
        return slugify(self.name)

    @property
    def serialize(self):
        # returns object in an easily serializable format
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'picture': self.picture,
        }


engine = create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)
