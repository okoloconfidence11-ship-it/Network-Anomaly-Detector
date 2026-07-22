import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder

def load_data(train_path, test_path):
    train = pd.read_csv(train_path, low_memory=False)
    test = pd.read_csv(test_path, low_memory=False)
    return train, test

def preprocess_data(train, test):
    train.columns = train.columns.str.strip()
    test.columns = test.columns.str.strip()

    drop_cols = ['Timestamp', 'Flow ID', 'Source IP', 'Destination IP', 'Source Port', 'Protocol']
    train.drop(columns=[c for c in drop_cols if c in train.columns], inplace=True, errors='ignore')
    test.drop(columns=[c for c in drop_cols if c in test.columns], inplace=True, errors='ignore')

    for df in [train, test]:
        df.replace([np.inf, -np.inf], np.nan, inplace=True)
        df.dropna(inplace=True)

    X_train = train.iloc[:, :-1].apply(pd.to_numeric, errors='coerce').fillna(0)
    y_train_raw = train.iloc[:, -1].astype(str)
    
    X_test = test.iloc[:, :-1].apply(pd.to_numeric, errors='coerce').fillna(0)
    y_test_raw = test.iloc[:, -1].astype(str)

    X_test = X_test.reindex(columns=X_train.columns, fill_value=0)

    le = LabelEncoder()
    combined_labels = pd.concat([y_train_raw, y_test_raw])
    le.fit(combined_labels)
    y_train = le.transform(y_train_raw)
    y_test = le.transform(y_test_raw)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    return X_train_scaled, X_test_scaled, y_train, y_test, scaler