from httpx import AsyncClient


async def test_get_languages(client: AsyncClient) -> None:
    resp = await client.get('/languages')
    assert resp.status_code == 200
    languages = resp.json()
    assert len(languages) > 0
