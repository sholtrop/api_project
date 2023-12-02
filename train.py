import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from smile import smile

model_filename = './rf_classifier.xz'
def train_model():
    df=pd.read_csv('./dataset.csv')
    df.drop(columns=df.columns[0], axis=1, inplace=True)
    X = df.drop('label', axis=1)  # Features
    y = df['label']  # Labels

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    rf_classifier = RandomForestClassifier(n_estimators=100, random_state=42)

    rf_classifier.fit(X_train, y_train)

    y_pred = rf_classifier.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {accuracy:.3f}")

    from joblib import dump
    dump(rf_classifier, model_filename)
    print('Saved classifier to', model_filename)