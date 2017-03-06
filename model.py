from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, Date, Text, Float
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
import os

# Sessions

engine = create_engine(os.environ['DATABASE_URL'], echo=False)
session = scoped_session(sessionmaker(bind=engine, autocommit=False, autoflush=False))

Base = declarative_base()
Base.query = session.query_property()

user_movies_tbl = Table('user_movies', Base.metadata,
                        Column('user_id', Integer, ForeignKey('users.id')),
                        Column('movie_imdb_id', Integer, ForeignKey('movies.id'))
                        )


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(128))
    password = Column(String(128))
    first_name = Column(String(64), nullable=True, default="Bob")
    last_name = Column(String(64), nullable=True, default="Bradley")

    movies = relationship("Movie", secondary=user_movies_tbl,
                          backref="users", lazy="dynamic")

    def __init__(self, email, password, first_name, last_name):
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name

    def __repr__(self):
        return '<User Email:{}>'.format(self.email)


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    movie_imdb_id = Column(Integer)
    user_rating = Column(Integer, default=5)
    name = Column(String(64))

    def __init__(self, movie_imdb_id, name, user_rating):
        self.movie_imdb_id = movie_imdb_id
        self.name = name
        self.user_rating = user_rating

    def __repr__(self):
        return '<Movie:{}>'.format(self.name)


def create_tables():
    Base.metadata.create_all(engine)


def main():
    create_tables()

if __name__ == "__main__":
    main()
