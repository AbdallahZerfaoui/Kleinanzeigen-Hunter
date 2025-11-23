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

    rental_space: Optional[float] = None
    nbr_rooms: Optional[float] = None
    location: Optional[str] = None
    views: Optional[int] = None
    details: Dict[str, Any] = Field(default_factory=dict)
    features: Dict[str, Any] = Field(default_factory=dict)
    old_price: Optional[int] = None
    additional_costs: Optional[float] = None
    deposit: Optional[float] = None
    available_from: Optional[str] = None

    @field_validator("rental_space", mode="before")
    @classmethod
    def _normalize_rental_space(cls, value: Any) -> Optional[float]:
        if value in (None, ""):
            return None
        if isinstance(value, str):
            # Handle European decimal notation (comma separator)
            normalized = value.replace(",", ".").strip()
            # Remove any non-numeric characters except decimal point
            cleaned = "".join(ch for ch in normalized if ch.isdigit() or ch == ".")
            try:
                return float(cleaned) if cleaned else None
            except ValueError:
                return None
        if isinstance(value, (int, float)):
            return float(value)
        return None

    @field_validator("nbr_rooms", mode="before")
    @classmethod
    def _normalize_nbr_rooms(cls, value: Any) -> Optional[float]:
        if value in (None, ""):
            return None
        if isinstance(value, str):
            # Replace comma with dot for German decimal format
            normalized = value.replace(",", ".").strip()
            # Remove any non-numeric characters except decimal point
            cleaned = "".join(ch for ch in normalized if ch.isdigit() or ch == ".")
            try:
                return float(cleaned) if cleaned else None
            except ValueError:
                return None
        if isinstance(value, (int, float)):
            return float(value)
        return None

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

    @field_validator("additional_costs", "deposit", mode="before")
    @classmethod
    def _normalize_cost_like(cls, value: Any) -> Optional[float]:
        """Normalize Nebenkosten / Kaution values with European decimal notation."""
        if value in (None, "", "-"):
            return None
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            # Remove currency symbols and spaces first
            cleaned = (
                value.replace("€", "")
                .replace("EUR", "")
                .replace("VB", "")
                .replace(" ", "")
                .strip()
            )
            # Handle European notation: thousand separator (.) and decimal separator (,)
            # Remove thousand separators (dots) then convert decimal comma to dot
            if "," in cleaned and "." in cleaned:
                # Both present: dot is thousand separator, comma is decimal
                cleaned = cleaned.replace(".", "").replace(",", ".")
            elif "," in cleaned:
                # Only comma: it's the decimal separator
                cleaned = cleaned.replace(",", ".")
            elif "." in cleaned:
                # Only dot: check if it's likely a thousand separator or decimal
                parts = cleaned.split(".")
                if len(parts) == 2 and len(parts[1]) == 3:
                    # Likely thousand separator (e.g., "1.200")
                    cleaned = cleaned.replace(".", "")
                # Otherwise treat as decimal separator
            
            # Extract numeric value
            try:
                return float(cleaned) if cleaned else None
            except ValueError:
                return None
        return None
