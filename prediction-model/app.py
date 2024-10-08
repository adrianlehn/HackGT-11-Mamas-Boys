from flask import Flask, request, jsonify
import joblib
import pandas as pd
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

log_reg_model, scaler, feature_names = joblib.load('logistic_regression_model.pkl'), \
                                       joblib.load('scaler.pkl'), \
                                       joblib.load('feature_names.pkl')

def preprocess_user(user_data, scaler, feature_names):
    df = pd.DataFrame([user_data])

    categorical_cols = df.select_dtypes(include=['object']).columns
    df = pd.get_dummies(df, columns=categorical_cols, drop_first=False)
    
    for col in feature_names:
        if col not in df.columns:
            df[col] = 0
    df = df[feature_names]
        
    # numerical_cols = df.select_dtypes(include=['int64']).columns
    # df[numerical_cols] = scaler.transform(df[numerical_cols])
    return df

@app.route('/predict', methods=['POST'])
def predict():
    user_data = request.json
    print(user_data)
    numeric_fields = ['time_in_hospital', 'n_procedures', 'n_lab_procedures', 'n_medications', 'n_outpatient', 'n_inpatient', 'n_emergency']
    for field in numeric_fields:
        if field in user_data:
            user_data[field] = int(user_data[field])
    preprocessed_input = preprocess_user(user_data, scaler, feature_names)
    print("Preprocessed Input (from Flask):", preprocessed_input)
    probability = log_reg_model.predict_proba(preprocessed_input)[:,1][0]
    print("Probability (from Flask):", probability)
    return jsonify({'prediction': probability})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
