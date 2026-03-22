"""
Student Math Score Prediction API
FastAPI application that serves predictions from the trained Linear Regression model.
"""

import os
import joblib
import numpy as np
import pandas as pd
from enum import Enum
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Student Math Score Predictor API",
    description=(
        "Predicts a student's math exam score based on demographic, "
        "socioeconomic, and academic features using a trained regression model."
    ),
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# CORS — specific origins, NOT wildcard *
# ---------------------------------------------------------------------------
allowed_origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8080",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://math-score-predictor.onrender.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
)

# ---------------------------------------------------------------------------
# Load model artifacts
# ---------------------------------------------------------------------------
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "linear_regression")


def load_artifacts():
    """Load the saved model, scaler, and feature columns."""
    model = joblib.load(os.path.join(MODEL_DIR, "best_model.pkl"))
    scaler = joblib.load(os.path.join(MODEL_DIR, "scaler.pkl"))
    features = joblib.load(os.path.join(MODEL_DIR, "feature_columns.pkl"))
    return model, scaler, features


model, scaler, feature_columns = load_artifacts()

# ---------------------------------------------------------------------------
# Enums for categorical validation
# ---------------------------------------------------------------------------

class GenderEnum(str, Enum):
    female = "female"
    male = "male"


class LunchEnum(str, Enum):
    standard = "standard"
    free_reduced = "free/reduced"


class TestPrepEnum(str, Enum):
    none_ = "none"
    completed = "completed"


class ParentalEducationEnum(str, Enum):
    some_high_school = "some high school"
    high_school = "high school"
    some_college = "some college"
    associates_degree = "associate's degree"
    bachelors_degree = "bachelor's degree"
    masters_degree = "master's degree"


# ---------------------------------------------------------------------------
# Pydantic request / response models with constraints & datatypes
# ---------------------------------------------------------------------------

class PredictionRequest(BaseModel):
    """Input features for predicting a student's math score."""

    gender: GenderEnum = Field(
        ...,
        description="Student's gender",
        examples=["female"],
    )
    parental_level_of_education: ParentalEducationEnum = Field(
        ...,
        description="Highest education level of the student's parent",
        examples=["bachelor's degree"],
    )
    lunch: LunchEnum = Field(
        ...,
        description="Type of lunch the student receives",
        examples=["standard"],
    )
    test_preparation_course: TestPrepEnum = Field(
        ...,
        description="Whether the student completed a test preparation course",
        examples=["completed"],
    )
    reading_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Student's reading exam score (0-100)",
        examples=[72],
    )
    writing_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Student's writing exam score (0-100)",
        examples=[74],
    )

    class Config:
        json_schema_extra = {
            "example": {
                "gender": "female",
                "parental_level_of_education": "bachelor's degree",
                "lunch": "standard",
                "test_preparation_course": "completed",
                "reading_score": 72,
                "writing_score": 74,
            }
        }


class PredictionResponse(BaseModel):
    """Response containing the predicted math score."""

    predicted_math_score: float = Field(
        ..., description="Predicted math exam score (0-100)"
    )
    model_used: str = Field(
        ..., description="Name of the model that produced the prediction"
    )


class RetrainResponse(BaseModel):
    """Response after retraining the model."""

    message: str
    new_test_r2: float
    new_test_rmse: float
    best_model_name: str


# ---------------------------------------------------------------------------
# Encoding maps (must match the notebook)
# ---------------------------------------------------------------------------
GENDER_MAP = {"female": 0, "male": 1}
LUNCH_MAP = {"free/reduced": 0, "standard": 1}
TEST_PREP_MAP = {"none": 0, "completed": 1}
EDU_MAP = {
    "some high school": 0,
    "high school": 1,
    "some college": 2,
    "associate's degree": 3,
    "bachelor's degree": 4,
    "master's degree": 5,
}


def encode_input(req: PredictionRequest) -> np.ndarray:
    """Convert a PredictionRequest into a scaled feature array."""
    raw = pd.DataFrame(
        [
            {
                "gender": GENDER_MAP[req.gender.value],
                "parental level of education": EDU_MAP[
                    req.parental_level_of_education.value
                ],
                "lunch": LUNCH_MAP[req.lunch.value],
                "test preparation course": TEST_PREP_MAP[
                    req.test_preparation_course.value
                ],
                "reading score": req.reading_score,
                "writing score": req.writing_score,
            }
        ]
    )
    # Ensure column order matches training
    raw = raw[feature_columns]
    scaled = scaler.transform(raw)
    return scaled


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/", tags=["Health"])
def root():
    """Health check — confirms the API is running."""
    return {"status": "healthy", "model": "Student Math Score Predictor"}


@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
def predict(request: PredictionRequest):
    """
    Predict a student's math score.

    Accepts demographic, socioeconomic, and academic features and returns
    the predicted math exam score (0-100).
    """
    try:
        scaled_input = encode_input(request)
        prediction = model.predict(scaled_input)[0]
        prediction = float(np.clip(prediction, 0, 100))
        return PredictionResponse(
            predicted_math_score=round(prediction, 2),
            model_used=type(model).__name__,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/retrain", response_model=RetrainResponse, tags=["Model Management"])
def retrain():
    """
    Retrain the model when new data is available.

    Runs the full training pipeline: loads data, encodes features,
    trains all three models, picks the best by test MSE, saves it,
    and hot-reloads the artifacts so subsequent /predict calls use
    the updated model.
    """
    global model, scaler, feature_columns

    try:
        csv_path = os.path.join(MODEL_DIR, "StudentsPerformance.csv")
        if not os.path.exists(csv_path):
            raise HTTPException(
                status_code=404, detail="Dataset CSV not found for retraining."
            )

        df = pd.read_csv(csv_path)

        # --- same pipeline as the notebook ---
        df.drop(columns=["race/ethnicity"], inplace=True, errors="ignore")
        df["gender"] = df["gender"].map({"female": 0, "male": 1})
        df["lunch"] = df["lunch"].map({"free/reduced": 0, "standard": 1})
        df["test preparation course"] = df["test preparation course"].map(
            {"none": 0, "completed": 1}
        )
        df["parental level of education"] = df["parental level of education"].map(
            EDU_MAP
        )

        X = df.drop(columns=["math score"])
        y = df["math score"].values

        from sklearn.preprocessing import StandardScaler as SS
        from sklearn.model_selection import train_test_split
        from sklearn.linear_model import LinearRegression
        from sklearn.tree import DecisionTreeRegressor
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.metrics import mean_squared_error, r2_score

        new_scaler = SS()
        X_scaled = pd.DataFrame(new_scaler.fit_transform(X), columns=X.columns)
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )

        results = {}
        for name, est in [
            ("Linear Regression", LinearRegression()),
            ("Decision Tree", DecisionTreeRegressor(max_depth=5, random_state=42)),
            (
                "Random Forest",
                RandomForestRegressor(
                    n_estimators=200, max_depth=5, random_state=42
                ),
            ),
        ]:
            est.fit(X_train.values, y_train)
            preds = est.predict(X_test.values)
            mse = mean_squared_error(y_test, preds)
            results[name] = {
                "model": est,
                "mse": mse,
                "r2": r2_score(y_test, preds),
            }

        best_name = min(results, key=lambda k: results[k]["mse"])
        best_est = results[best_name]["model"]

        joblib.dump(best_est, os.path.join(MODEL_DIR, "best_model.pkl"))
        joblib.dump(new_scaler, os.path.join(MODEL_DIR, "scaler.pkl"))
        joblib.dump(
            list(X_train.columns),
            os.path.join(MODEL_DIR, "feature_columns.pkl"),
        )

        # Hot-reload
        model, scaler, feature_columns = load_artifacts()

        return RetrainResponse(
            message="Model retrained and reloaded successfully.",
            new_test_r2=round(results[best_name]["r2"], 4),
            new_test_rmse=round(float(np.sqrt(results[best_name]["mse"])), 4),
            best_model_name=best_name,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Retraining failed: {str(e)}"
        )
