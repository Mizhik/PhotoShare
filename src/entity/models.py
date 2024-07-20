import enum
from datetime import datetime, date
from uuid import uuid4

from sqlalchemy import Column, String, Integer, DateTime, func, ForeignKey, Table, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped, mapped_column

Base = declarative_base()

photo_tag_association = Table(
    'photo_tag',
    Base.metadata,
    Column('photo_id', Integer, ForeignKey('photos.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)


class Role(enum.Enum):
    admin: str = "admin"
    moderator: str = "moderator"
    user: str = "user"


class User(Base):
    __tablename__ = 'users'
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[date] = mapped_column("created_at", DateTime, default=func.now())
    updated_at: Mapped[date] = mapped_column("updated_at", DateTime, default=func.now(), onupdate=func.now())
    role: Mapped[Enum] = mapped_column("role", Enum(Role), default=Role.user, nullable=True)
    photos: Mapped[list['Photo']] = relationship('Photo', backref='user')
    comments: Mapped[list['Comment']] = relationship('Comment', backref='user')


class Photo(Base):
    __tablename__ = 'photos'
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    url: Mapped[int] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    tags: Mapped[list['Tag']] = relationship('Tag', secondary=photo_tag_association, backref='photos')
    transformed_image: Mapped[list['TransformedImage']] = relationship('TransformedImage', backref='photo')
    comments: Mapped[list['Comment']] = relationship('Comment', backref='photo')


class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)


class Comment(Base):
    __tablename__ = 'comments'
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    text: Mapped[str] = mapped_column(String(150), nullable=False)
    created_at: Mapped[datetime] = mapped_column('created_at', DateTime, default=func.now(), onupdate=func.now())
    updated_at: Mapped[datetime] = mapped_column('updated_at', DateTime, default=func.now(), onupdate=func.now())
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    photo_id: Mapped[int] = mapped_column(Integer, ForeignKey('photos.id'))


class TransformedImage(Base):
    __tablename__ = 'transformed_images'
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    photo_id: Mapped[int] = mapped_column(Integer, ForeignKey('photos.id'))
    transformed_url: Mapped[str] = mapped_column(String, nullable=False)
    qr_code_url: Mapped[str] = mapped_column(String, nullable=False)
