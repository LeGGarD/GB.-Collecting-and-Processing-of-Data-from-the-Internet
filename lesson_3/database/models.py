from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from sqlalchemy import Column, Index, Integer, String, ForeignKey, Boolean, BigInteger, Table

Base = declarative_base()

tag_post = Table(
    "tag_post",
    Base.metadata,
    Column("post_id", BigInteger, ForeignKey("post.id")),
    Column("tag_id", BigInteger, ForeignKey("tag.id"))
)


class UrlMixin:
    url = Column(String, unique=True, nullable=False)


class Post(Base, UrlMixin):
    __tablename__ = "post"
    id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True)
    title = Column(String(250), nullable=False, unique=False)
    author_id = Column(BigInteger, ForeignKey("author.id"))
    author = relationship("Author")
    # tags = relationship("Tag", secondary="tag_post", backref='posts')
    tags = relationship("Tag", secondary="tag_post")


class Author(Base, UrlMixin):
    __tablename__ = "author"
    id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String(150), nullable=False)


class Tag(Base, UrlMixin):
    __tablename__ = "tag"
    id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String(150), nullable=False)
    posts = relationship(Post, secondary="tag_post")
