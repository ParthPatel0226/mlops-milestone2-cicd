"""
Unit tests for ML inference service.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

import pytest
import json
from app import app

@pytest.fixture
def client():
    """Create test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert 'version' in data

def test_predict_valid_input(client):
    """Test prediction with valid input."""
    payload = {'features': [5.1, 3.5, 1.4, 0.2]}
    response = client.post('/predict',
                          data=json.dumps(payload),
                          content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'prediction' in data
    assert 'prediction_label' in data
    assert 'confidence' in data

def test_predict_missing_features(client):
    """Test prediction with missing features."""
    payload = {}
    response = client.post('/predict',
                          data=json.dumps(payload),
                          content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

def test_predict_wrong_feature_count(client):
    """Test prediction with wrong number of features."""
    payload = {'features': [5.1, 3.5]}  # Only 2 features instead of 4
    response = client.post('/predict',
                          data=json.dumps(payload),
                          content_type='application/json')
    assert response.status_code == 400