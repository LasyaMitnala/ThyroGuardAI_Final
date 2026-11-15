Open http://localhost:8508 if the browser does not open automatically.

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

Our ThyroAI machine-learning model demonstrated strong performance in classifying thyroid-related patterns using the UCI Thyroid Disease dataset. We trained our model on 3,772 records containing 21 numerical features and evaluated its performance using an official held-out test dataset of 3,428 records.

We compared two machine-learning algorithms, Random Forest and Logistic Regression. Random Forest outperformed Logistic Regression during validation, achieving 99.34% accuracy, 99.76% balanced accuracy, and a 97.36% macro F1-score. Consequently, we selected Random Forest as our final classification model.

On the official test dataset, our model achieved:

Accuracy: 99.10%

Balanced Accuracy: 99.67%

Macro F1-Score: 95.72%

The model correctly classified all 73 Class 1 cases and all 177 Class 2 cases, while correctly identifying 3,147 of 3,178 Class 3 cases. Its 31 misclassifications involved Class 3 records being predicted as Class 1 or Class 2. Although these results demonstrate strong performance on historical test data, they do not establish clinical diagnostic reliability.

Model Limitations and Future Validation

While our initial results were promising, our development timeline limited us primarily to initial model training, algorithm comparison, and preliminary evaluation. Although we evaluated the model using an official held-out test dataset, additional validation is necessary to determine whether its performance generalizes beyond the historical records used in development.

With more time, we would conduct extensive cross-validation, investigate potential data leakage and overlapping records, and perform additional hyperparameter optimization to improve model reliability. We would also evaluate the model using independent clinical datasets to assess its performance across more diverse patient populations and thyroid conditions. Furthermore, we would incorporate explainable AI techniques, such as SHAP (SHapley Additive exPlanations), to better understand which features contribute most significantly to the model's predictions.

An important limitation of our initial model is that its 21 numerical input features are not fully mapped to interpretable clinical measurements. Before implementing the classifier in a patient-facing application, we would need to verify the meaning of each feature, establish reliable input mappings, and conduct further testing to ensure predictions are interpretable and appropriate for the intended use.

Ultimately, these additional steps would allow us to move beyond our initial proof of concept toward a more robust, transparent, and clinically responsible machine-learning system.

## AI Integration into ThyroGuard

The application's primary AI feature, ThyroAI, is designed to integrate our trained Random Forest classifier into an accessible, interactive health-monitoring platform. Our long-term goal is to allow users to enter relevant demographic information, medical history, and thyroid laboratory measurements, which could then be analyzed using machine-learning models trained on compatible clinical datasets.

During our initial development phase, we focused on building and evaluating the underlying machine-learning models alongside the application's user interface. While the initial classifier demonstrated strong performance on historical test data, further feature mapping, validation, and integration testing are required before its predictions can be reliably generated from patient-entered information. As a result, ThyroAI currently represents an early-stage AI-assisted classification system rather than a clinically validated diagnostic tool.

ThyroGuard also includes several supporting features:

ThyroidTrend: Organizes thyroid laboratory measurements and visualizes changes over time to help users recognize trends in their recorded health information.

SymptomWatch: Allows patients to record and monitor symptoms, creating a structured history of changes in their condition.

FollowUpGuard: Tracks follow-up appointments and monitoring plans to support consistent long-term health management.

Patient Management: Organizes patient profiles and associated health records within a centralized interface.

Reports: Generates downloadable PDF summaries and CSV exports of recorded health information to facilitate documentation and communication.

Together, these features establish the foundation for a comprehensive thyroid health-monitoring platform that combines structured recordkeeping, symptom tracking, laboratory visualization, and preliminary machine-learning research. With further development, our goal is to strengthen the connection between these components and introduce more extensively validated AI-assisted insights, helping users better understand their recorded health information while supporting—not replacing—professional medical evaluation.

Together, these features establish a unified platform that combines machine-learning classification with longitudinal health monitoring. Our next steps are to verify end-to-end model inference within the deployed application, improve the interpretability of AI predictions, and integrate classification results into downloadable reports.

Our final binary classification model, developed using a Random Forest algorithm, demonstrated promising preliminary performance on the dataset's held-out test partition. The model achieved 99.69% accuracy, 99.83% balanced accuracy, 95.95% precision, 100% recall, and a 97.93% F1-score. Of the 972 test records, the model correctly classified 898 negative cases and all 71 hypothyroid cases, with three negative cases incorrectly classified as hypothyroid. These results suggest that the model successfully identified distinguishing patterns within the historical dataset, particularly in recognizing records labeled as hypothyroid.

In addition to binary classification, we trained a multiclass Random Forest model to distinguish between different hypothyroid classifications. This model achieved 99.18% test accuracy, 99.70% balanced accuracy, and a 96.64% macro F1-score across the three classes represented in the test set. However, certain diagnostic categories were severely underrepresented, limiting our ability to evaluate performance across all thyroid conditions reliably.

**Limitations:** 
Due to the limited development timeline, our work focused primarily on initial model training, preliminary validation, and evaluation using the available historical datasets. Although the results were encouraging, they do not establish that ThyroAI would perform equally well on new patient populations or in clinical settings. The unusually high performance also warrants further investigation into potential data leakage, overlapping records, and dataset-specific patterns.

With additional development time, we would conduct more extensive cross-validation, systematically investigate data quality and possible leakage, optimize model hyperparameters, and evaluate performance on independent datasets representing more diverse patient populations. We would also explore explainable AI methods, such as SHAP, to identify which clinical features contribute most strongly to individual predictions.

Overall, our initial results demonstrate the technical feasibility of using machine learning to classify thyroid-related records within a historical dataset. While further validation and refinement are necessary, this preliminary proof of concept establishes a foundation for developing ThyroAI into a more reliable, transparent, and responsible AI-assisted thyroid health application.

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
