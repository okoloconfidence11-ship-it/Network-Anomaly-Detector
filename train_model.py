import numpy as np
import joblib
from preprocess import load_data, preprocess_data
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, MaxPooling1D, Flatten, Dense, Dropout

def build_cic_cnn(input_shape, num_classes):
    model = Sequential([
        Conv1D(64, kernel_size=3, activation='relu', input_shape=input_shape),
        MaxPooling1D(pool_size=2),
        Dropout(0.2),
        Conv1D(128, kernel_size=3, activation='relu'),
        MaxPooling1D(pool_size=2),
        Dropout(0.3),
        Flatten(),
        Dense(128, activation='relu'),
        Dense(num_classes, activation='softmax' if num_classes > 2 else 'sigmoid')
    ])
    
    loss_func = 'sparse_categorical_crossentropy' if num_classes > 2 else 'binary_crossentropy'
    model.compile(optimizer='adam', loss=loss_func, metrics=['accuracy'])
    return model

if __name__ == "__main__":
    train_df, test_df = load_data("data/train.csv", "data/test.csv")
    X_train, X_test, y_train, y_test, scaler = preprocess_data(train_df, test_df)

    num_features = X_train.shape[1]
    num_classes = len(np.unique(y_train))
    
    X_train_cnn = X_train.reshape(X_train.shape[0], num_features, 1)
    X_test_cnn = X_test.reshape(X_test.shape[0], num_features, 1)

    model = build_cic_cnn((num_features, 1), num_classes)
    model.fit(X_train_cnn, y_train, epochs=10, batch_size=256, validation_split=0.2)

    model.save("model.h5")
    joblib.dump(scaler, "scaler.pkl")
    print("Model and Scaler Saved Successfully")