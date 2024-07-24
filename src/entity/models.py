import enum
from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import String, DateTime, func, Enum, ForeignKey, Column, Table
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
	pass


photo_tag_association = Table(
	'photo_tag',
	Base.metadata,
	Column('photo_id', PGUUID(as_uuid=True), ForeignKey('photos.id')),
	Column('tag_id', PGUUID(as_uuid=True), ForeignKey('tags.id'))
)


class Role(enum.Enum):
	admin: str = "admin"
	moderator: str = "moderator"
	user: str = "user"


class User(Base):
	__tablename__ = 'users'
	id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
	username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
	email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
	password: Mapped[str] = mapped_column(String(255), nullable=False)
	created_at: Mapped[date] = mapped_column("created_at", DateTime, default=func.now())
	updated_at: Mapped[date] = mapped_column("updated_at", DateTime, default=func.now(), onupdate=func.now())
	role: Mapped[Role] = mapped_column("role", Enum(Role), default=Role.user)
	photos: Mapped[list['Photo']] = relationship('Photo', back_populates='user')
	comments: Mapped[list['Comment']] = relationship('Comment', back_populates='user')

	@property
	def is_admin(self):
		return self.role == Role.admin

	@property
	def is_moderator(self):
		return self.role == Role.moderator

class Photo(Base):
	"""
	Model for photo information storing.
	"""
	__tablename__ = 'photos'
	id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
	cloudinary_id: Mapped[str] = mapped_column(String(255), nullable=False)
	url: Mapped[str] = mapped_column(String(255), nullable=False)
	description: Mapped[str] = mapped_column(String(255), nullable=True)
	user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey('users.id'))
	created_at: Mapped[date] = mapped_column("created_at", DateTime, default=func.now())
	updated_at: Mapped[date] = mapped_column("updated_at", DateTime, default=func.now(), onupdate=func.now())
	tags: Mapped[list['Tag']] = relationship('Tag', secondary=photo_tag_association, back_populates='photos')
	transformed_images: Mapped[list['TransformedImage']] = relationship('TransformedImage', back_populates='photo')
	comments: Mapped[list['Comment']] = relationship('Comment', back_populates='photo')
	user: Mapped['User'] = relationship('User', back_populates='photos')


class Tag(Base):
	__tablename__ = "tags"
	id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
	name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
	photos: Mapped[list['Photo']] = relationship('Photo', secondary=photo_tag_association, back_populates='tags')


class Comment(Base):
	__tablename__ = 'comments'
	id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
	text: Mapped[str] = mapped_column(String(150), nullable=False)
	created_at: Mapped[date] = mapped_column('created_at', DateTime, default=func.now())
	updated_at: Mapped[date] = mapped_column('updated_at', DateTime, default=func.now(), onupdate=func.now())
	user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey('users.id'))
	photo_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey('photos.id'))
	user: Mapped['User'] = relationship('User', back_populates='comments')
	photo: Mapped['Photo'] = relationship('Photo', back_populates='comments')


class TransformedImage(Base):
	__tablename__ = 'transformed_images'
	id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
	photo_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey('photos.id'))
	transformed_url: Mapped[str] = mapped_column(String, nullable=False)
	photo: Mapped['Photo'] = relationship('Photo', back_populates='transformed_images')
