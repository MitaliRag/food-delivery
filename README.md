# Food Delivery Intelligence

A food analytics dashboard built with FastAPI, Pandas,
JavaScript, Chart.js, and scikit-learn.

## Features

- Food dataset summary and KPIs
- Diet and course distribution charts
- Searchable food explorer
- Diet, course, and region filters
- TF-IDF food similarity model
- Vercel deployment configuration

## Setup

Install dependencies:

    python -m pip install -r requirements.txt

Run the API:

    python -m uvicorn api.index:app --reload --port 8000

Open the dashboard at:

    http://127.0.0.1:8000/api/summary

The API provides food records and analytics. For a full local
dashboard, serve the public directory separately on port 5500.

## Dataset

Place your dataset at data/indian_food.xls.

Check its actual columns before using it. Recipe data alone
does not provide delivery transactions, delivery durations,
or customer purchase histories.

## Deployment

Push the project to GitHub and import the repository into Vercel.

