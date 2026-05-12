
import pytest
from fastapi.testclient import TestClient
from fastapi import Response
from api.main import app

client = TestClient(app)

# def test_generate_fhir() -> None:
#     response: Response = client.get("/info")
#     json = response.json()
    
#     assert response.status_code == 200
#     assert "application" in json
#     assert "version" in json
#     assert json["application"] == app.title
#     assert json["version"] == app.version