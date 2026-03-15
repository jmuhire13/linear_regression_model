# Student Math Score Predictor

**Mission:** Predict a student's math score using academic and socioeconomic features to help educators identify students who may need additional support in mathematics.

**Dataset:** [Students Performance in Exams](https://www.kaggle.com/datasets/spscientist/students-performance-in-exams) from Kaggle — 1,000 student records with 8 features including gender, parental education level, lunch type, test preparation status, reading score, and writing score.

**Models:** Linear Regression, Decision Tree, and Random Forest regressors are trained and compared. The best-performing model (lowest test MSE) is saved and used for prediction.

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
