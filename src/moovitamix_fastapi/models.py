import sqlalchemy as sa
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Users(Base):
    __tablename__ = "users"

    id = sa.Column(sa.Integer, primary_key=True, nullable=False, index=True)
    first_name = sa.Column(sa.String(255), nullable=False)
    last_name = sa.Column(sa.String(255), nullable=False)
    email = sa.Column(sa.String(255), nullable=False, unique=True)
    gender = sa.Column(sa.String(50), nullable=False)
    favorite_genres = sa.Column(sa.String(255), nullable=False)
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.current_timestamp(), nullable=False)
    updated_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.current_timestamp(), nullable=False)


class Tracks(Base):
    __tablename__ = "tracks"

    id = sa.Column(sa.Integer, primary_key=True, nullable=False, index=True)
    name = sa.Column(sa.String(255), nullable=False)
    artist = sa.Column(sa.String(255), nullable=False)
    songwriters = sa.Column(sa.String(255), nullable=False)
    duration = sa.Column(sa.String(10), nullable=False)
    genres = sa.Column(sa.String(255), nullable=False)
    album = sa.Column(sa.String(255), nullable=False)
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.current_timestamp(), nullable=False)
    updated_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.current_timestamp(), nullable=False)


class ListenHistory(Base):
    __tablename__ = "listen_history"

    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), primary_key=True, nullable=False, index=True)
    items = sa.Column(sa.String(255), nullable=False)
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.current_timestamp(), nullable=False)
    updated_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.current_timestamp(), nullable=False)
