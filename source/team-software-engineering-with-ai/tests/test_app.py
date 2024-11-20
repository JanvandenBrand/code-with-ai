import pytest
from src.app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_app_setup():
    # Test if the Flask app is set up correctly
    assert app is not None

def test_greet_valid_name(client):
    # Test the /api/greet/<name> endpoint with a valid name
    response = client.get('/api/greet/John')
    assert response.status_code == 200
    assert response.get_json() == {'message': 'Hello, John!'}

def test_greet_empty_name(client):
    # Test the /api/greet/<name> endpoint with an empty name
    response = client.get('/api/greet/')
    assert response.status_code == 404  # Expecting a 404 Not Found