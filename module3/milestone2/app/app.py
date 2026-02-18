"""
Simple ML inference service for containerization demo.
"""
from flask import Flask, request, jsonify
import joblib
import numpy as np
import os

app = Flask(__name__)

# Load model at startup (deterministic)
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model.pkl')
model = joblib.load(MODEL_PATH)

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'ML Inference Service',
        'version': '1.0.0'
    })

@app.route('/predict', methods=['POST'])
def predict():
    """Prediction endpoint."""
    try:
        data = request.get_json()
        
        if 'features' not in data:
            return jsonify({'error': 'Missing features'}), 400
        
        features = np.array(data['features']).reshape(1, -1)
        
        if features.shape[1] != 4:
            return jsonify({'error': 'Expected 4 features'}), 400
        
        prediction = int(model.predict(features)[0])
        probabilities = model.predict_proba(features)[0]
        confidence = float(max(probabilities))
        
        class_names = {0: "setosa", 1: "versicolor", 2: "virginica"}
        
        return jsonify({
            'prediction': prediction,
            'prediction_label': class_names.get(prediction, 'unknown'),
            'confidence': round(confidence, 4),
            'version': '1.0.0'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)