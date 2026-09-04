import pytest
pytestmark = pytest.mark.asyncio

async def test_health(client):
    assert (await client.get("/api/health")).json() == {"status": "ok"}

async def test_crud_and_empty_deletes(client):
    created = await client.post("/api/notes", json={"date":"2026-09-04", "text":"  Позвонить Андрею  "})
    assert created.status_code == 201 and created.json()["text"] == "Позвонить Андрею"
    assert (await client.get("/api/notes/2026-09-04")).json()["text"] == "Позвонить Андрею"
    updated = await client.put("/api/notes/2026-09-04", json={"text":"Новый текст"})
    assert updated.json()["text"] == "Новый текст"
    assert (await client.put("/api/notes/2026-09-04", json={"text":"  "})).status_code == 204
    assert (await client.get("/api/notes/2026-09-04")).status_code == 404

async def test_month_search_delete_and_unique_date(client):
    await client.post("/api/notes", json={"date":"2026-09-04", "text":"Позвонить Андрею по договору"})
    await client.post("/api/notes", json={"date":"2026-10-01", "text":"Другой месяц"})
    monthly = await client.get("/api/notes", params={"year":2026,"month":9})
    assert [item["date"] for item in monthly.json()] == ["2026-09-04"]
    found = await client.get("/api/notes/search", params={"q":"андре"})
    assert len(found.json()) == 1
    duplicate = await client.post("/api/notes", json={"date":"2026-09-04", "text":"Дубликат"})
    assert duplicate.status_code == 409
    assert (await client.delete("/api/notes/2026-09-04")).status_code == 204

async def test_empty_create_and_limits(client):
    assert (await client.post("/api/notes", json={"date":"2026-09-04", "text":""})).status_code == 422
    assert (await client.post("/api/notes", json={"date":"2026-09-04", "text":"x"*20001})).status_code == 422
