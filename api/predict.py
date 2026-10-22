
from pathlib import Path
from functools import lru_cache

import pandas as pd

# Project paths
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"


# Load the dataset only once
@lru_cache(maxsize=1)
def load_food_data():
    candidates = [
        DATA_DIR / "indian_food.xls",
        DATA_DIR / "indian_food.xlsx",
        DATA_DIR / "indian_food.csv",
        DATA_DIR / "food_orders.csv",
    ]

    file_path = next(
        (path for path in candidates if path.exists()),
        None
    )

    if file_path is None:
        raise FileNotFoundError(
            f"Dataset not found in: {DATA_DIR}"
        )

    try:
        if file_path.suffix.lower() == ".csv":
            df = pd.read_csv(file_path)
        else:
            try:
                df = pd.read_excel(file_path)
            except Exception:
                # Some CSV files are incorrectly named .xls
                df = pd.read_csv(file_path)

    except Exception as exc:
        raise ValueError(
            f"Could not read {file_path.name}: {exc}"
        ) from exc

    # Standardize column names
    df.columns = [
        str(column).strip().lower().replace(" ", "_")
        for column in df.columns
    ]

    # Clean empty rows and duplicates
    df = df.dropna(how="all")
    df = df.drop_duplicates()
    df = df.fillna("Unknown").reset_index(drop=True)

    # Check required column
    if "name" not in df.columns:
        raise ValueError(
            "Expected a 'name' column. "
            f"Available columns: {list(df.columns)}"
        )

    return df


# Generate dashboard summary
def get_food_summary(df):

    def count_values(column):
        if column not in df.columns:
            return {}

        return (
            df[column]
            .astype(str)
            .value_counts()
            .head(10)
            .to_dict()
        )

    def average_numeric(column):
        if column not in df.columns:
            return None

        values = pd.to_numeric(
            df[column], errors="coerce"
        ).dropna()

        if values.empty:
            return None

        return round(float(values.mean()), 1)

    prep = average_numeric("prep_time")
    cook = average_numeric("cook_time")

    return {
        "total_foods": int(len(df)),

        "categories": int(df["course"].nunique())
        if "course" in df.columns else 0,

        "regions": int(df["region"].nunique())
        if "region" in df.columns else 0,

        "vegetarian": int(
            df["diet"].astype(str).str.contains(
                "vegetarian",
                case=False,
                na=False
            ).sum()
        ) if "diet" in df.columns else 0,

        "avg_prep_time": prep,
        "avg_cook_time": cook,

        "diet_distribution": count_values("diet"),
        "course_distribution": count_values("course"),
        "region_distribution": count_values("region"),
    }


# Search and filter food records
def recommend_foods(
    df,
    diet=None,
    course=None,
    region=None,
    search=None,
    max_time=None,
    limit=50
):
    result = df

    # Apply diet, course and region filters
    for column, selected in [
        ("diet", diet),
        ("course", course),
        ("region", region),
    ]:
        if (
            selected
            and selected.lower() != "all"
            and column in result.columns
        ):
            result = result[
                result[column]
                .astype(str)
                .str.lower()
                == selected.lower()
            ]

    # Search food names, ingredients and other details
    if search and search.strip():
        searchable = [
            column
            for column in [
                "name",
                "ingredients",
                "flavor_profile",
                "state",
                "region",
            ]
            if column in result.columns
        ]

        if searchable:
            mask = result[searchable].astype(str).apply(
                lambda col: col.str.contains(
                    search.strip(),
                    case=False,
                    regex=False,
                    na=False
                )
            ).any(axis=1)

            result = result[mask]

    # Filter by preparation and cooking time
    if max_time is not None:
        time_columns = [
            column
            for column in ["prep_time", "cook_time"]
            if column in result.columns
        ]

        if time_columns:
            total_time = pd.Series(
                0,
                index=result.index,
                dtype="float64"
            )

            for column in time_columns:
                total_time += pd.to_numeric(
                    result[column],
                    errors="coerce"
                ).fillna(0)

            result = result[total_time <= max_time]

    # Limit the number of returned records
    safe_limit = max(1, min(int(limit), 200))

    return result.head(safe_limit).copy()

