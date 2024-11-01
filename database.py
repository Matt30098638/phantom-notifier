from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import logging

# Database setup
DATABASE_URL = "sqlite:///media_database.db"
engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)
Base = declarative_base()

# Define MediaItem model
class MediaItem(Base):
    __tablename__ = 'media_items'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    media_type = Column(String, nullable=False)
    jellyfin_id = Column(String, unique=True, nullable=False)
    added_date = Column(DateTime, default=datetime.utcnow)

# Define Recommendation model
class Recommendation(Base):
    __tablename__ = 'recommendations'

    id = Column(Integer, primary_key=True)
    media_item_id = Column(Integer, ForeignKey('media_items.id'))
    recommended_title = Column(String, nullable=False)
    recommended_type = Column(String, nullable=True)
    tmdb_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    media_item = relationship("MediaItem", back_populates="recommendations")

MediaItem.recommendations = relationship("Recommendation", back_populates="media_item")

# Create tables
Base.metadata.create_all(engine)

# Function to add a media item with duplicate handling
def add_media_item(title, media_type, jellyfin_id, added_date=datetime.utcnow()):
    session = Session()
    try:
        # Check for duplicate based on title
        existing_item = session.query(MediaItem).filter_by(title=title).first()
        if existing_item:
            logging.info(f"Skipping duplicate entry: {title}")
            return
        
        # Create new media item
        media_item = MediaItem(title=title, media_type=media_type, jellyfin_id=jellyfin_id, added_date=added_date)
        session.add(media_item)
        session.commit()
        logging.info(f"Inserted item: {title}")
    except IntegrityError:
        session.rollback()
        logging.error(f"Duplicate entry detected for title '{title}'. Skipping insertion.")
    finally:
        session.close()

# Function to add a recommendation
def add_recommendation(media_item_id, recommended_title, recommended_type=None, tmdb_id=None):
    session = Session()
    try:
        recommendation = Recommendation(
            media_item_id=media_item_id,
            recommended_title=recommended_title,
            recommended_type=recommended_type,
            tmdb_id=tmdb_id
        )
        session.add(recommendation)
        session.commit()
    except IntegrityError:
        session.rollback()
        logging.error(f"Duplicate recommendation detected for '{recommended_title}'. Skipping insertion.")
    finally:
        session.close()

# Function to get all media items
def get_all_media_items():
    session = Session()
    items = session.query(MediaItem).all()
    session.close()
    return [{'id': item.id, 'title': item.title, 'type': item.media_type} for item in items]

# Function to get all recommendations
def get_new_recommendations():
    session = Session()
    recommendations = session.query(Recommendation).all()
    session.close()
    return [{'recommended_title': rec.recommended_title, 'recommended_type': rec.recommended_type} for rec in recommendations]
