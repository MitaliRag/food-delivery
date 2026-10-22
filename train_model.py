from pathlib import Path
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from api.predict import load_food_data

ROOT = Path(__file__).resolve().parent
MODEL_DIR = ROOT / "model"
MODEL_DIR.mkdir(exist_ok=True)


def main():
    df = load_food_data()

    name = df["name"].astype(str)
    ingredients = (
        df["ingredients"].astype(str)
        if "ingredients" in df.columns
        else name
    )

    text_data = (name + " " + ingredients).tolist()

    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=5000,
        ngram_range=(1, 2)
    )

    matrix = vectorizer.fit_transform(text_data)

    model_data = {
        "vectorizer": vectorizer,
        "matrix": matrix,
        "foods": df.to_dict(orient="records")
    }

    output = MODEL_DIR / "food_recommender.pkl"
    joblib.dump(model_data, output)

    print(f"Dataset records: {len(df)}")
    print(f"Feature count: {len(vectorizer.get_feature_names_out())}")
    print(f"Model saved to: {output}")


if __name__ == "__main__":
    main()
