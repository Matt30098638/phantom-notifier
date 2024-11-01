from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, timedelta
import logging

# SQLAlchemy setup
DATABASE_URL = "sqlite:///media_database.db"
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

logging.basicConfig(level=logging.INFO)

class MediaItem(Base):
    __tablename__ = 'media_items'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, nullable=False)
    media_type = Column(String, nullable=False)  # e.g., "movie", "tv"
    jellyfin_id = Column(String, unique=True, nullable=False)
    added_date = Column(DateTime, default=datetime.utcnow)


class Recommendation(Base):
    __tablename__ = 'recommendations'

    id = Column(Integer, primary_key=True, index=True)
    media_item_id = Column(Integer, ForeignKey('media_items.id'), nullable=False)
    recommended_title = Column(String, nullable=False)
    recommended_type = Column(String, nullable=False)  # e.g., "movie", "tv"
    tmdb_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    media_item = relationship("MediaItem", back_populates="recommendations")

    def is_expired(self):
        # Check if recommendation data is older than 30 days
        return datetime.utcnow() > self.created_at + timedelta(days=30)


class FailedAttempt(Base):
    __tablename__ = 'failed_attempts'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    failure_reason = Column(String)
    attempted_date = Column(DateTime, default=datetime.utcnow)


# Relationships
MediaItem.recommendations = relationship("Recommendation", order_by=Recommendation.id, back_populates="media_item")

# Create tables
Base.metadata.create_all(engine)

def get_session():
    """Helper to create a new SQLAlchemy session."""
    return SessionLocal()

def add_media_item(title, media_type, jellyfin_id):
    session = get_session()
    try:
        item = MediaItem(title=title, media_type=media_type, jellyfin_id=jellyfin_id)
        session.add(item)
        session.commit()
        logging.info(f"Added media item '{title}' of type '{media_type}'.")
    except Exception as e:
        session.rollback()
        logging.error(f"Error adding media item '{title}': {e}")
    finally:
        session.close()


def add_recommendation(media_item_id, recommended_title, recommended_type, tmdb_id):
    session = get_session()
    try:
        recommendation = Recommendation(
            media_item_id=media_item_id,
            recommended_title=recommended_title,
            recommended_type=recommended_type,
            tmdb_id=tmdb_id
        )
        session.add(recommendation)
        session.commit()
        logging.info(f"Added recommendation '{recommended_title}' for media item ID '{media_item_id}'.")
    except Exception as e:
        session.rollback()
        logging.error(f"Error adding recommendation for media item ID '{media_item_id}': {e}")
    finally:
        session.close()


def cache_recommendation_exists(media_item_id):
    """Check if there are valid recommendations for a media item, ignoring expired entries."""
    session = get_session()
    try:
        recommendation = (
            session.query(Recommendation)
            .filter(Recommendation.media_item_id == media_item_id)
            .filter(Recommendation.created_at > datetime.utcnow() - timedelta(days=30))
            .first()
        )
        return recommendation is not None
    finally:
        session.close()
