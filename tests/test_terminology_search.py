'''
Temporary test for local env. Test will fail if no terminology search enabled or database is not setup. Not suitable for pipelines.
TODO: Make generic w/ built in DB.
'''
import pytest
from fastapi.testclient import TestClient
from fastapi import Response
from api.main import app

client = TestClient(app)


def test_terminology_search() -> None:
    response: Response = client.get("/terminology/search?term=potassium blood&system=http://loinc.org&page=1&count=20&sort_order=asc")
    json = response.json()
    
    assert response.status_code == 200
    assert "term" in json
    assert "total" in json
    assert json["term"] == "potassium blood"
    assert int(json["total"]) == 11 # type: ignore