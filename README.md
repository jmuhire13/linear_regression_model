# Student Math Score Predictor

**Mission:** Build a regression model to predict a student’s math score using academic and socioeconomic features in order to help educators identify students who may need additional academic support.

**Dataset:** [Students Performance in Exams](https://www.kaggle.com/datasets/spscientist/students-performance-in-exams) from Kaggle. The dataset contains 1,000 student records and 8 variables including gender, parental level of education, lunch type, test preparation course, reading score, writing score, and math score.

**Problem:** Predict the continuous variable `math_score` using multiple input features through regression analysis.

**Models:** Linear Regression, Decision Tree Regressor, and Random Forest Regressor are trained using scikit-learn. The model with the lowest test Mean Squared Error (MSE) is saved and used for prediction.

---

**API Endpoint:** https://math-score-predictor-d8z2.onrender.com/predict
**Swagger UI:** https://math-score-predictor-d8z2.onrender.com/docs
**Video Demo:** https://youtu.be/2ez8jhAssXU

## How to run the mobile app

1. Navigate to the summative/FlutterApp directory.
2. Run Flutter pub get and then Flutter run.

---

## Repository Structure

```
linear_regression_model/
│
├── summative/
│   ├── linear_regression/
│   │   ├── multivariate.ipynb
│   │   ├── StudentsPerformance.csv
│   │   ├── best_model.pkl
│   │   ├── scaler.pkl
│   │   └── feature_columns.pkl
│   ├── API/
│   └── FlutterApp/
```
