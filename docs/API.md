# 📡 API Documentation

> Base URL: `http://127.0.0.1:8000`  
> Interactive docs: [Swagger UI](/docs) · [ReDoc](/redoc)

---

## Transactions

### `GET /transactions`

Retrieve all transactions. Supports optional query parameter filtering.

**Query Parameters**

| Name       | Type     | Required | Description                   |
|------------|----------|----------|-------------------------------|
| `category` | `string` | No       | Filter by category name       |
| `type`     | `string` | No       | `income` or `expense`         |
| `month`    | `int`    | No       | Month (1–12)                  |
| `year`     | `int`    | No       | Year (e.g. 2025)              |

**Response** `200 OK`

```json
[
  {
    "id": 1,
    "amount": 45.90,
    "category": "Lebensmittel",
    "type": "expense",
    "date": "2025-03-15",
    "note": "Wocheneinkauf REWE"
  }
]
```

---

### `POST /transactions`

Create a new transaction.

**Request Body**

```json
{
  "amount": 45.90,
  "category": "Lebensmittel",
  "type": "expense",
  "date": "2025-03-15",
  "note": "Wocheneinkauf REWE"
}
```

| Field      | Type     | Required | Description                             |
|------------|----------|----------|-----------------------------------------|
| `amount`   | `float`  | Yes      | Positive number                         |
| `category` | `string` | Yes      | Category name (max 50 chars)            |
| `type`     | `string` | Yes      | `income` or `expense`                   |
| `date`     | `string` | No       | ISO date (defaults to today)            |
| `note`     | `string` | No       | Optional note (max 255 chars)           |

**Response** `201 Created`

```json
{
  "id": 1,
  "amount": 45.90,
  "category": "Lebensmittel",
  "type": "expense",
  "date": "2025-03-15",
  "note": "Wocheneinkauf REWE"
}
```

---

### `GET /transactions/{id}`

Retrieve a single transaction by ID.

**Response** `200 OK` — Transaction object  
**Response** `404 Not Found` — `{"detail": "Transaction not found"}`

---

### `PUT /transactions/{id}`

Update an existing transaction. Only include fields you want to change.

**Request Body** (all fields optional)

```json
{
  "amount": 50.00,
  "note": "Updated note"
}
```

**Response** `200 OK` — Updated transaction object

---

### `DELETE /transactions/{id}`

Delete a transaction by ID.

**Response** `204 No Content`  
**Response** `404 Not Found` — `{"detail": "Transaction not found"}`

---

## Summary

### `GET /summary`

Get a financial summary with total income, total expenses, balance, and a breakdown of expenses by category.

**Query Parameters**

| Name    | Type  | Required | Description          |
|---------|-------|----------|----------------------|
| `month` | `int` | No       | Month (1–12)         |
| `year`  | `int` | No       | Year (e.g. 2025)     |

**Response** `200 OK`

```json
{
  "total_income": 2500.00,
  "total_expenses": 1234.56,
  "balance": 1265.44,
  "transaction_count": 15,
  "categories": [
    { "category": "Miete", "total": 750.00 },
    { "category": "Lebensmittel", "total": 320.50 },
    { "category": "Transport", "total": 89.00 },
    { "category": "Freizeit", "total": 75.06 }
  ]
}
```

---

## Categories

The following default categories are available in the frontend:

| Category       | Icon | Typical Use         |
|----------------|------|---------------------|
| Lebensmittel   | 🛒   | Groceries & food    |
| Miete          | 🏠   | Rent & housing      |
| Freizeit       | 🎮   | Leisure & hobbies   |
| Transport      | 🚌   | Public transit, gas  |
| Gehalt         | 💼   | Salary & income     |
| Sonstiges      | 📦   | Miscellaneous       |

> The API accepts any string as a category — the list above is used by the frontend UI.

---

## Error Responses

All errors follow a consistent format:

```json
{
  "detail": "Human-readable error message"
}
```

| Status Code | Meaning                |
|-------------|------------------------|
| `400`       | Validation error       |
| `404`       | Resource not found     |
| `422`       | Unprocessable entity   |
| `500`       | Internal server error  |
