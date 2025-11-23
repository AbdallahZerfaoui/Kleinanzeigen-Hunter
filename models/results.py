"""Pydantic models describing generic and real-estate listings."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ListingResult(BaseModel):
    """Generic Kleinanzeigen listing as returned by search results."""

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(alias="adid")
    url: str
    title: str
    price: Optional[int] = None
    description: Optional[str] = None

    @field_validator("price", mode="before")
    @classmethod
    def _normalize_price(cls, value: Any) -> Optional[int]:
        if value in (None, "", "-"):
            return None
        if isinstance(value, str):
            digits = value.strip().replace(" ", "")
            return int(digits) if digits.isdigit() else None
        if isinstance(value, (int, float)):
            return int(value)
        return None


class RealEstateResult(ListingResult):
    """Detailed listing for real-estate inserat pages."""

    rental_space: Optional[int] = None
    nbr_rooms: Optional[float] = None
    location: Optional[Dict[str, Any]] = None
    views: Optional[int] = None
    details: Dict[str, Any] = Field(default_factory=dict)
    features: Dict[str, Any] = Field(default_factory=dict)
    old_price: Optional[int] = None
    additional_costs: Optional[int] = None
    deposit: Optional[int] = None
    available_from: Optional[str] = None

    @field_validator("views", mode="before")
    @classmethod
    def _normalize_views(cls, value: Any) -> Optional[int]:
        if value in (None, ""):
            return None
        if isinstance(value, str):
            digits = "".join(ch for ch in value if ch.isdigit())
            return int(digits) if digits else None
        if isinstance(value, (int, float)):
            return int(value)
        return None
