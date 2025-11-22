# Ebay Kleinanzeigen API

<div align="center">
  <h3 align="center">Ebay Kleinanzeigen API</h3>

  <p align="center">
    A powerful API interface for Ebay-Kleinanzeigen.de that enables you to fetch listings and specific data.
  </p>

  <p align="center">
    <b>🚀 Looking for a ready-to-use solution?</b>
    <br />
    Try it at <a href="https://kleinanzeigen-agent.de/features/developer-api"><strong>kleinanzeigen-agent.de »</strong></a>
    <br />
    ✓ Automated Search Agents
    <br />
    ✓ Search & Detail API
    <br />
    <a href="https://github.com/DanielWTE/ebay-kleinanzeigen-api/issues">Report Bug</a>
    ·
    <a href="https://github.com/DanielWTE/ebay-kleinanzeigen-api/issues">Request Feature</a>
  </p>
</div>

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Getting Started

### Want to skip the setup?
Visit [kleinanzeigen-agent.de](https://kleinanzeigen-agent.de/features/developer-api) for our hosted solution with additional features and zero configuration required.

### Prerequisites
- Python 3.12 or higher
- pip (Python package manager)
- Playwright
- Redis (local install, Docker container, or cloud instance)

### Installation

1. Clone the repository
```sh
git clone https://github.com/DanielWTE/ebay-kleinanzeigen-api.git
cd ebay-kleinanzeigen-api
```

2. Install dependencies
```sh
pip install -r requirements.txt
playwright install chromium
```

> **Tip:** If you plan to use Docker, simply run `docker compose up --build` and Redis will be provisioned automatically.

3. Start the API
```sh
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### API Endpoints

#### 1. Fetch Listings
**Endpoint:** `GET /inserate`

**Description:** Retrieves a list of listings based on search criteria.

##### Query Parameters:
- **`query`** *(string, optional)*: The search term (e.g., "fahrrad" to search for bicycles).
- **`location`** *(string, optional)*: The location or postal code to narrow the search (e.g., `10178` for Berlin).
- **`radius`** *(integer, optional)*: The search radius in kilometers from the specified location (e.g., `5` for a 5 km radius).
- **`min_price`** *(integer, optional)*: The minimum price in Euros for the listings (e.g., `200` for at least 200 Euros).
- **`max_price`** *(integer, optional)*: The maximum price in Euros for the listings (e.g., `500` for at most 500 Euros).
- **`page_count`** *(integer, optional)*: The number of pages to search or return (e.g., `5` for the first 5 pages, default is 1, max: 20 pages).

##### Example Request:
```http
GET /inserate?query=fahrrad&location=10178&radius=5&min_price=200&page_count=5
```

#### 2. Fetch Listing Details
**Endpoint:** `GET /inserat/{inserat_id}`

**Description:** Retrieves detailed information about a specific listing.

##### Path Parameters:
- **`inserat_id`** *(string)*: The unique identifier of the listing to fetch details for.

##### Example Request:
```http
GET /inserat/12345
```

### Response Caching
- Both `/inserate` and `/inserat/{inserat_id}` responses are cached in Redis for **1 hour**.
- Cache keys are built from all query parameters to ensure unique entries per search.
- You can control caching behaviour via environment variables:

| Variable | Default | Description |
| --- | --- | --- |
| `CACHE_ENABLED` | `true` | Toggle caching globally |
| `CACHE_TTL_SECONDS` | `3600` | Cache lifetime in seconds |
| `REDIS_HOST` | `localhost` (or `redis` in Docker) | Hostname for Redis |
| `REDIS_PORT` | `6379` | Port number for Redis |
| `REDIS_DB` | `0` | Numeric Redis database to use |
| `REDIS_URL` | `redis://<host>:<port>/<db>` | Override connection string entirely |


### Documentation

#### API Response Format
All API endpoints return responses in the following JSON format:
```json
{
  "success": true,
  "data": [
    ...
  ]
}
```

API documentation is available at `http://localhost:8000/docs` when running locally.

## License
Distributed under the MIT License. See `LICENSE` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>
