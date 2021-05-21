from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from sqlalchemy import Column, Index, Integer, String, ForeignKey, Boolean, BigInteger, Table, DateTime

Base = declarative_base()

tag_post = Table(
    "tag_post",
    Base.metadata,
    Column("post_id", Integer, ForeignKey("post.id")),
    Column("tag_id", Integer, ForeignKey("tag.id"))
)


class UrlMixin:
    url = Column(String, unique=True, nullable=False)


class Post(Base, UrlMixin):
    __tablename__ = "post"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(250), nullable=False, unique=False)
    author_id = Column(Integer, ForeignKey("author.id"), nullable=True)
    author = relationship("Author")
    # tags = relationship("Tag", secondary="tag_post", backref='posts')
    tags = relationship("Tag", secondary=tag_post)


class Author(Base, UrlMixin):
    __tablename__ = "author"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False)


class Tag(Base, UrlMixin):
    __tablename__ = "tag"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    posts = relationship(Post, secondary="tag_post")


class Comment(Base, UrlMixin):
    __tablename__ = "comment"
    id = Column(Integer, primary_key=True, autoincrement=True)
    parent_id = Column(Integer, ForeignKey("comment.id"), nullable=True)
    post_id = Column(Integer, ForeignKey("post.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("author.id"), nullable=False)

    likes_count = Column(Integer)
    body = Column(String)
    created_at = Column(DateTime, nullable=False)

    post = relationship(Post, backref='comments')
    author = relationship(Author, backref='comments')

    def __init__(self, **kwargs):
        self.id = kwargs['id']
        self.parent_id = kwargs['parent_id']
        self.post_id = kwargs['post']
        self.author_id = kwargs['author']

        self.likes_count = kwargs["likes_count"]
        self.body = kwargs["body"]
        self.created_at = kwargs["created_at"]

