"""Database utilities using SQLAlchemy ORM for storing rental listings.

Provides simple helpers for creating the SQLite file and inserting/querying
rental records. This mirrors the earlier sqlite3 helpers but uses SQLAlchemy
ORM for clarity.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Text,
    create_engine,
    func,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


DATA_DIR = Path(__file__).parent.parent / "data"
DB_PATH = DATA_DIR / "rentals.db"


class Base(DeclarativeBase):
    pass


class Rental(Base):
    __tablename__ = "rentals"
    __table_args__ = (UniqueConstraint("adid", name="uix_adid"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    adid = Column(String(128), nullable=False, unique=True, index=True)
    url = Column(Text, nullable=False)
    title = Column(String(512), nullable=False)
    price = Column(String(64), nullable=False)
    old_price = Column(String(64), nullable=False, default="0")
    description = Column(Text, nullable=True)
    postal_code = Column(String(32), nullable=True)
    category = Column(String(64), nullable=True)
    location_id = Column(String(64), nullable=True)
    radius = Column(Integer, nullable=True)
    scraped_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)


def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _create_engine():
    _ensure_data_dir()
    sqlite_url = f"sqlite:///{DB_PATH}"
    return create_engine(sqlite_url, echo=False, future=True)


_engine = _create_engine()
SessionLocal = sessionmaker(bind=_engine, expire_on_commit=False)


def init_database() -> None:
    """Create database tables if they don't exist."""
    Base.metadata.create_all(bind=_engine)


def get_session() -> Session:
    """Return a new SQLAlchemy session. Use as: with get_session() as s:"""
    return SessionLocal()


def insert_rental(
    adid: str,
    url: str,
    title: str,
    price: str,
    old_price: str,
    description: Optional[str] = None,
    postal_code: Optional[str] = None,
    category: Optional[str] = None,
    location_id: Optional[str] = None,
    radius: Optional[int] = None,
) -> bool:
    """Insert or update a single rental. Returns True if inserted, False if updated."""
    with get_session() as session:
        existing = session.query(Rental).filter_by(adid=adid).one_or_none()
        if existing is None:
            r = Rental(
                adid=adid,
                url=url,
                title=title,
                price=price,
                old_price=old_price or "0",
                description=description,
                postal_code=postal_code,
                category=category,
                location_id=location_id,
                radius=radius,
            )
            session.add(r)
            session.commit()
            return True
        else:
            existing.url = url
            existing.title = title
            existing.price = price
            existing.old_price = old_price or "0"
            existing.description = description
            existing.postal_code = postal_code
            existing.category = category
            existing.location_id = location_id
            existing.radius = radius
            session.commit()
            return False


def bulk_insert_rentals(
    rentals: Iterable[Dict[str, Any]],
    postal_code: Optional[str] = None,
    category: Optional[str] = None,
    location_id: Optional[str] = None,
    radius: Optional[int] = None,
) -> Tuple[int, int]:
    """Bulk insert/update rentals. Returns (inserted_count, updated_count)."""
    inserted = 0
    updated = 0
    with get_session() as session:
        for r in rentals:
            adid = r.get("adid")
            if not adid:
                continue
            existing = session.query(Rental).filter_by(adid=adid).one_or_none()
            if existing is None:
                new_r = Rental(
                    adid=adid,
                    url=r.get("url") or "",
                    title=r.get("title") or "",
                    price=r.get("price") or "",
                    old_price=r.get("old_price") or "0",
                    description=r.get("description"),
                    postal_code=postal_code,
                    category=category,
                    location_id=location_id,
                    radius=radius,
                )
                session.add(new_r)
                inserted += 1
            else:
                existing.url = r.get("url") or existing.url
                existing.title = r.get("title") or existing.title
                existing.price = r.get("price") or existing.price
                existing.old_price = r.get("old_price") or existing.old_price or "0"
                existing.description = r.get("description") or existing.description
                existing.postal_code = postal_code or existing.postal_code
                existing.category = category or existing.category
                existing.location_id = location_id or existing.location_id
                existing.radius = radius or existing.radius
                updated += 1
        session.commit()
    return inserted, updated


def get_rental_by_adid(adid: str) -> Optional[Dict[str, Any]]:
    with get_session() as session:
        r = session.query(Rental).filter_by(adid=adid).one_or_none()
        if r is None:
            return None
        return {
            "id": r.id,
            "adid": r.adid,
            "url": r.url,
            "title": r.title,
            "price": r.price,
            "old_price": r.old_price,
            "description": r.description,
            "postal_code": r.postal_code,
            "category": r.category,
            "location_id": r.location_id,
            "radius": r.radius,
            "scraped_at": r.scraped_at,
            "updated_at": r.updated_at,
        }


def get_all_rentals(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    with get_session() as session:
        rows = (
            session.query(Rental)
            .order_by(Rental.scraped_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )
        return [
            {
                "id": r.id,
                "adid": r.adid,
                "url": r.url,
                "title": r.title,
                "price": r.price,
                "old_price": r.old_price,
                "description": r.description,
                "postal_code": r.postal_code,
                "category": r.category,
                "location_id": r.location_id,
                "radius": r.radius,
                "scraped_at": r.scraped_at,
                "updated_at": r.updated_at,
            }
            for r in rows
        ]


def count_rentals() -> int:
    with get_session() as session:
        return session.query(func.count(Rental.id)).scalar() or 0
