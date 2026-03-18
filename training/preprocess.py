import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from training.config import DATA_PATH, TARGET_COLUMN


def load_data():
    df = pd.read_csv(DATA_PATH)
    return df


def preprocess_data(df):
    # Drop unnecessary columns
    if "UDI" in df.columns:
        df = df.drop(columns=["UDI"])
    if "Product ID" in df.columns:
        df = df.drop(columns=["Product ID"])

    # Encode categorical column
    if "Type" in df.columns:
        le = LabelEncoder()
        df["Type"] = le.fit_transform(df["Type"])

    # ✅ Clean column names for XGBoost
    df.columns = df.columns.str.replace("[", "", regex=False)
    df.columns = df.columns.str.replace("]", "", regex=False)
    df.columns = df.columns.str.replace("<", "", regex=False)

    X = df.drop(columns=[TARGET_COLUMN])
    y = df[TARGET_COLUMN]

    return X, y


def split_data(X, y):
    return train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )