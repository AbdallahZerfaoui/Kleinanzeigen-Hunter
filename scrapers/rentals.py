"""Scraper for rental property listings from Kleinanzeigen."""

from typing import Optional, Sequence

from fastapi import HTTPException

from config import KLEINANZEIGEN_BASE_URL
from utils.browser import PlaywrightManager

async def build_search_url(
    postal_code: str,
    category: str,
    location_id: Optional[str],
    radius: int,
    min_price: Optional[int],
    max_price: Optional[int],
    page: int = 1,
) -> str:
    """
    Construct the search URL for rental listings.
    Args:
        postal_code (str): Postal code for the search location.
        category (str): Category code (e.g., c203 for Wohnung Mieten).
        location_id (str, optional): Location ID (e.g., l9245). If None, derived from postal.
        radius (int): Search radius in kilometers.
        min_price (int, optional): Minimum rent price filter.
        max_price (int, optional): Maximum rent price filter.
        page (int): Page number for pagination.
    Returns:
        str: The constructed search URL.
    """
    # Build the price filter part of the path
    price_path = ""
    if min_price is not None or max_price is not None:
        min_price_str = str(min_price) if min_price is not None else ""
        max_price_str = str(max_price) if max_price is not None else ""
        price_path = f"/preis:{min_price_str}:{max_price_str}"

    # Build pagination part
    page_path = f"/seite:{page}" if page > 1 else ""

    # Build the complete path: /s-wohnung-mieten/{postal_code}{price_path}{page_path}/{category}{location_id}r{radius}
    # Example: /s-wohnung-mieten/74072/preis:500:1000/seite:2/c203l9245r5
    location_param = f"{location_id}" if location_id else ""
    search_path = f"/s-wohnung-mieten/s-{postal_code}{price_path}{page_path}/{category}{location_param}r{radius}"

    # Construct the full URL
    search_url = KLEINANZEIGEN_BASE_URL + search_path
    # print(f"Constructed search URL: {search_url}")
    return search_url


async def get_rentals_klaz(
    browser_manager: PlaywrightManager,
    postal_code: str,
    category: str = "c203",  # c203 = Wohnung Mieten
    location_id: Optional[str] = "l9245",  # e.g., l9245
    radius: int = 5,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    page_count: int = 1,
) -> list:
    """
    Scrapes rental listings from Kleinanzeigen for the specified location.

    Args:
        browser_manager (PlaywrightManager): The Playwright browser manager instance.
        postal_code (str): Postal code for the search location (e.g., "74072").
        category (str, optional): Category code. Defaults to "c203" (Wohnung Mieten).
        location_id (str, optional): Location ID (e.g., "l9245"). If None, derived from postal.
        radius (int, optional): Search radius in kilometers. Defaults to 5.
        min_price (int, optional): Minimum rent price filter.
        max_price (int, optional): Maximum rent price filter.
        page_count (int, optional): Number of pages to scrape. Defaults to 1.

    Returns:
        list: A list of dictionaries containing the scraped rental details.
    """
    # base_url = KLEINANZEIGEN_BASE_URL

    # # Build the price filter part of the path
    # price_path = ""
    # if min_price is not None or max_price is not None:
    #     min_price_str = str(min_price) if min_price is not None else ""
    #     max_price_str = str(max_price) if max_price is not None else ""
    #     price_path = f"/preis:{min_price_str}:{max_price_str}"

    # # Build the base path: /s-wohnung-mieten/{postal_code}/{category}{location_id}r{radius}
    # # Example: /s-wohnung-mieten/74072/c203l9245r5
    # location_param = f"{location_id}" if location_id else ""
    # base_path = f"/s-wohnung-mieten/{postal_code}/{category}{location_param}r{radius}"

    # # Add price and pagination
    # search_path = f"{base_path}{price_path}/seite:{{page}}"

    # # Construct the full URL
    # search_url = base_url + search_path

    print(f"[DEBUG] Starting rental scrape for postal_code={postal_code}, category={category}")
    expected_category_id = _normalize_category_id(category)
    allowed_category_ids = [expected_category_id] if expected_category_id else None
    print(f"[DEBUG] Expected category ID: {expected_category_id}")
    
    print("[DEBUG] Creating browser page...")
    browser_page = await browser_manager.new_context_page()
    print("[DEBUG] Browser page created successfully")
    
    try:
        results = []

        for i in range(page_count):
            print(f"[DEBUG] Processing page {i + 1}/{page_count}")
            # Build URL for each page
            search_url = await build_search_url(
                postal_code,
                category,
                location_id,
                radius,
                min_price,
                max_price,
                page=i + 1,
            )
            print(f"[DEBUG] Built search URL: {search_url}")
            
            print("[DEBUG] Navigating to page (timeout=120s)...")
            await browser_page.goto(search_url, timeout=120000, wait_until="domcontentloaded")
            print("[DEBUG] Navigation completed, waiting for ad listings to appear...")
            
            # Wait for the actual ad list container instead of networkidle
            try:
                await browser_page.wait_for_selector(
                    ".ad-listitem",
                    timeout=30000,
                    state="visible"
                )
                print("[DEBUG] Ad listings loaded successfully")
            except Exception as wait_err:
                print(f"[DEBUG] Warning: Could not find ad listings: {wait_err}")
                # Continue anyway - maybe there are no results

            print("[DEBUG] Extracting rental ads from page...")
            page_results = await get_rental_ads(
                browser_page, allowed_category_ids=allowed_category_ids
            )
            print(f"[DEBUG] Found {len(page_results)} rental ads on page {i + 1}")
            results.extend(page_results)
            
        print(f"[DEBUG] Scraping completed. Total results: {len(results)}")
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    finally:
        await browser_manager.close_page(browser_page)


def _normalize_category_id(category: Optional[str]) -> Optional[str]:
    """Extract the numeric category ID from strings like 'c203'."""

    if not category:
        return None
    return category.lstrip("cC") or None


def _extract_category_id_from_url(url: str) -> Optional[str]:
    """Parse the category id from a Kleinanzeigen detail URL."""

    last_segment = url.rstrip("/").split("/")[-1]
    parts = last_segment.split("-")
    if len(parts) >= 2:
        return parts[1]
    return None


async def get_rental_ads(page, allowed_category_ids: Optional[Sequence[str]] = None):
    """Extract rental listings from the current page."""

    print("[DEBUG] get_rental_ads: Starting extraction...")
    print("[DEBUG] get_rental_ads: Querying for ad list items...")
    items = await page.query_selector_all(
        ".ad-listitem:not(.is-topad):not(.badge-hint-pro-small-srp)"
    )
    print(f"[DEBUG] get_rental_ads: Found {len(items)} items on the page")

    results = []
    normalized_allowed = {
        cid for cid in (allowed_category_ids or []) if cid
    }
    print(f"[DEBUG] get_rental_ads: Allowed category IDs: {normalized_allowed}")

    for idx, item in enumerate(items):
        print(f"[DEBUG] get_rental_ads: Processing item {idx + 1}/{len(items)}")
        article = await item.query_selector("article")
        if article:
            data_adid = await article.get_attribute("data-adid")
            data_href = await article.get_attribute("data-href")

            # Get title from h2 element
            title_element = await article.query_selector(
                "h2.text-module-begin a.ellipsis"
            )
            title_text = await title_element.inner_text() if title_element else ""

            # Get price (rent)
            price = await article.query_selector(
                "p.aditem-main--middle--price-shipping--price"
            )
            price_text = await price.inner_text() if price else ""
            price_text = (
                price_text.replace("€", "")
                .replace("VB", "")
                .replace(".", "")
                .strip()
            )

            # Get description
            description = await article.query_selector(
                "p.aditem-main--middle--description"
            )
            description_text = await description.inner_text() if description else ""

            if data_adid and data_href:
                data_href = f"{KLEINANZEIGEN_BASE_URL}{data_href}"

                category_id = _extract_category_id_from_url(data_href)
                if normalized_allowed and category_id not in normalized_allowed:
                    print(f"[DEBUG] get_rental_ads: Skipping ad {data_adid} (category {category_id} not in allowed list)")
                    continue

                print(f"[DEBUG] get_rental_ads: Added ad {data_adid} - {title_text[:50]}")
                results.append(
                    {
                        "adid": data_adid,
                        "url": data_href,
                        "title": title_text,
                        "price": price_text,
                        "description": description_text,
                    }
                )
    print(f"[DEBUG] get_rental_ads: Extraction complete, returning {len(results)} results")
    return results
