from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from api.predict import load_food_data, get_food_summary, recommend_foods

app = FastAPI(title="Food Delivery Intelligence API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:3000",
        "http://localhost:3000",
    ],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"status": "ok", "message": "Food Intelligence API is running"}


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/summary")
def summary():
    try:
        return get_food_summary(load_food_data())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/foods")
def foods(
    diet: str | None = None,
    course: str | None = None,
    region: str | None = None,
    search: str | None = None,
    max_time: int | None = Query(default=None, ge=0, le=1440),
    limit: int = Query(default=100, ge=1, le=200),
):
    try:
        df = load_food_data()
        result = recommend_foods(
            df, diet=diet, course=course, region=region,
            search=search, max_time=max_time, limit=limit
        )
        result = result.astype(object).where(result.notna(), None)
        return {"count": len(result), "foods": result.to_dict(orient="records")}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/options")
def options():
    try:
        df = load_food_data()
        return {
            key: sorted(df[key].astype(str).unique().tolist())
            if key in df.columns else []
            for key in ["diet", "course", "region"]
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
