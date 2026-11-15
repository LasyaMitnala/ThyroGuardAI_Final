Open http://localhost:8503 if the browser does not open automatically.

# ThyroGaurd

** Track: Health
** Team: Pahal Vyas, Lasya Mitnala, Devarshita Karanam

## The Problem
Thyroid disorders, including hypothyroidism and hyperthyroidism, can cause symptoms such as fatigue, mood changes, and difficulty concentrating, which often overlap with other health conditions. Patients may struggle to understand their thyroid laboratory results, recognize changes in their health, and organize information for medical appointments. ThyroGuard aims to make thyroid health information more accessible through AI-powered analysis and personalized tracking.

## What we Built
ThyroGuard is an AI-powered thyroid health management application that combines machine learning with patient-friendly health monitoring tools. Users can enter thyroid laboratory measurements, record symptoms, and track their health over time. The application is designed to use a trained machine-learning classifier to identify thyroid-function patterns, including normal, hypothyroid, and hyperthyroid patterns, while providing visualizations that help users understand their results.

## What we added:
We developed ThyroGuard to go beyond traditional disease classification by combining AI-based thyroid analysis with longitudinal health tracking. Our approach integrates laboratory measurements, symptom monitoring, and explainable machine learning into one accessible application, allowing users to explore their thyroid health rather than receiving only a single prediction.

## How it works
Data: We selected the UCI Thyroid Disease dataset, specifically the new-thyroid.data subset containing 215 observations and five laboratory measurements. The dataset includes three thyroid-function categories: normal, hyperthyroid, and hypothyroid. Our planned preprocessing involves checking missing values, separating input features from class labels, and using a stratified training/test split.

Model: We use a Random Forest classifier implemented with Python and scikit-learn. Random Forest was selected because it can capture nonlinear relationships between thyroid measurements, handle multiple input features, and provide global feature-importance estimates. The model is designed to classify laboratory patterns using measurements such as T3, T4, and TSH-related values. We evaluate its performance using balanced accuracy, macro-F1, and a confusion matrix.

## Results

## Results

Our ThyroAI machine-learning model demonstrated strong performance in classifying thyroid-related patterns using the UCI Thyroid Disease dataset. We trained our model on 3,772 records containing 21 clinical and laboratory features and evaluated its performance using an official held-out test dataset of 3,428 records.

We compared two machine-learning algorithms, Random Forest and Logistic Regression. Random Forest outperformed Logistic Regression during validation, achieving **99.34% accuracy, 99.76% balanced accuracy, and a 97.36% macro F1-score**. Consequently, we selected Random Forest as our final classification model.

On the official test dataset, our model achieved:

- **Accuracy:** 99.10%
- **Balanced Accuracy:** 99.67%
- **Macro F1-Score:** 95.72%

The model correctly classified all 73 Class 1 cases and all 177 Class 2 cases, while correctly identifying 3,147 of 3,178 Class 3 cases. Its 31 misclassifications involved Class 3 records being predicted as Class 1 or Class 2. Although these results demonstrate strong performance on historical test data, they do not establish clinical diagnostic reliability.

**AI Integration into ThyroGuard

The application's primary feature, **ThyroAI**, is designed to use our trained Random Forest classifier to analyze patient-provided demographic information, medical history, and thyroid laboratory measurements. The model produces a classification based on patterns learned from the UCI dataset, providing an AI-powered component beyond traditional symptom tracking.

ThyroGuard also includes several supporting features:

- **ThyroidTrend:** Organizes thyroid laboratory measurements and visualizes changes over time.
- **SymptomWatch:** Allows patients to record and monitor symptoms.
- **FollowUpGuard:** Tracks follow-up appointments and monitoring plans.
- **Patient Management:** Organizes patient profiles and associated health records.
- **Reports:** Generates downloadable PDF summaries and CSV exports of recorded health information.

Together, these features establish a unified platform that combines machine-learning classification with longitudinal health monitoring. Our next steps are to verify end-to-end model inference within the deployed application, improve the interpretability of AI predictions, and integrate classification results into downloadable reports.

**Limitations:** ThyroAI is an educational research prototype, not a clinically validated diagnostic tool. Its predictions require careful interpretation, particularly because the model was trained on historical data that may not represent all patient populations.

## What we'd do next
With more time, we would expand ThyroGuard by training models on larger and more diverse clinical datasets, improving prediction calibration, and incorporating explainable AI techniques such as SHAP to clarify individual predictions. We would also explore longitudinal datasets to develop models capable of identifying changes in thyroid health over time and evaluate the system with clinical experts before considering real-world use.

## Sources

UCI Machine Learning Repository — Thyroid Disease Dataset: https://archive.ics.uci.edu/dataset/102/thyroid+disease

Scikit-learn — Random Forest Classifier: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html

Streamlit — Application Framework: https://streamlit.io/

Pandas — Data Processing: https://pandas.pydata.org/

Plotly — Interactive Data Visualization: https://plotly.com/python/

GitHub — ThyroGuard Repository: https://github.com/alpaca822/ThyroGuard

AI development assistance: OpenAI ChatGPT, used for coding guidance, debugging, and project documentation.
