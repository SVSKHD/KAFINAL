# models/model_training.py
from sklearn.ensemble import RandomForestClassifier

def train_model(X, y):
    model = RandomForestClassifier()
    model.fit(X, y)
    return model

def make_prediction(model, X):
    return model.predict(X)
