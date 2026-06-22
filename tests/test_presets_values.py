'''
Temporary test for local env. Test will fail if database is not setup. Not suitable for pipelines.
TODO: Make generic w/ built in DB/mock.
'''
import pytest
from fastapi.testclient import TestClient
from fastapi import Response
from api.main import app

client = TestClient(app)


def test_preset_value_search() -> None:
    code = "2823-3"
    system = "http://loinc.org"
    query = f"/presets/observation/value?code={code}&system={system}"
    response: Response = client.get(query)
    json = response.json()
    
    assert response.status_code == 200
    assert "parameters" in json
    assert "code" in json["parameters"]
    assert "count" in json
    assert json["parameters"]["code"] == code
    assert int(json["count"]) == 3 # type: ignore