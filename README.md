## https://thyroguard.streamlit.app/
Here is the app deployed on streamlit!

## THYROGUARD IS NOT A MEDICAL PROFESSIONAL AND ONLY A PROTOTYPE. DO NOT USE FOR MEDICAL DIAGNOSES.

## ThyroGuard

**Track:** Health  
**Team:** Pahal Vyas, Lasya Mitnala, Devarshita Karanam

## The Problem

Thyroid disorders, including hypothyroidism and hyperthyroidism, can cause symptoms such as fatigue, mood changes, and difficulty concentrating, which often overlap with other health conditions. Patients may struggle to understand their thyroid laboratory results, recognize changes in their health, and organize information for medical appointments.

ThyroGuard aims to make thyroid health information more accessible through AI-powered research tools, laboratory visualization, symptom tracking, and organized health records.

## What We Built

ThyroGuard is an AI-powered thyroid health management application that combines machine learning with patient-friendly health monitoring tools. Users can enter thyroid laboratory measurements, record symptoms, and track their health over time.

The application's primary AI feature, **ThyroAI**, incorporates a trained Random Forest classifier designed to identify patterns associated with three historical thyroid dataset categories: negative, hypothyroid, and hyperthyroid.

Rather than relying exclusively on a single prediction, ThyroGuard integrates thyroid-related information into an accessible dashboard that supports longitudinal monitoring and structured recordkeeping.

The application is built using Python, Streamlit, pandas, NumPy, scikit-learn, and Plotly, with GitHub used for version control.

## What Makes ThyroGuard Different?

We developed ThyroGuard to go beyond traditional disease classification by combining AI-based thyroid analysis with longitudinal health tracking.

Our approach integrates:

- Machine-learning classification of historical thyroid records
- Thyroid laboratory measurement tracking
- Symptom monitoring
- Follow-up appointment organization
- Patient record management
- Data visualization and downloadable reports

By combining these features, ThyroGuard provides a foundation for exploring thyroid health information over time rather than focusing solely on individual predictions.

## Machine Learning Development

### 1. Dataset Selection and Initial Experiments

We began our machine-learning development using the UCI Thyroid Disease dataset.

Our initial research considered the `new-thyroid.data` subset, containing 215 observations and five laboratory measurements. We subsequently explored larger datasets to improve the amount of training data available and investigate different thyroid classification tasks.

One early multiclass experiment used 3,772 training records with 21 numerical features and an official held-out test partition containing 3,428 records.

We compared Random Forest and Logistic Regression during model development. Random Forest demonstrated stronger validation performance, achieving:

- **Validation accuracy:** 99.34%
- **Validation balanced accuracy:** 99.76%
- **Validation macro F1-score:** 97.36%

On the official held-out test partition, this experimental model achieved:

- **Test accuracy:** 99.10%
- **Test balanced accuracy:** 99.67%
- **Test macro F1-score:** 95.72%

However, the 21 input features were not fully mapped to interpretable clinical measurements, and the numerical class labels could not be reliably translated into patient-facing thyroid diagnoses.

Consequently, we retained this experiment as an initial machine-learning benchmark and developed additional models using datasets with identifiable clinical features.

### 2. Binary Hypothyroidism Classification

Our next model used the UCI `allhypo` dataset to distinguish between records labeled negative and hypothyroid.

We trained a Random Forest classifier using clinically named features, including age, sex, thyroid-related medical history, medication information, and laboratory measurements.

The binary classifier achieved the following performance on 972 held-out test records:

- **Accuracy:** 99.69%
- **Balanced accuracy:** 99.83%
- **Precision:** 95.95%
- **Recall:** 100%
- **F1-score:** 97.93%

The model correctly classified all 71 hypothyroid test records, while three negative records were incorrectly classified as hypothyroid.

Although these results were encouraging, this model could not distinguish hyperthyroidism from other thyroid-function categories. We therefore expanded our approach to three-class classification.

### 3. Development of Our Three-Class Thyroid Classifier

Our most recent machine-learning development focused on creating a Random Forest classifier capable of distinguishing between three historical dataset categories:

1. Negative
2. Hypothyroid
3. Hyperthyroid

To accomplish this, we combined four files from the UCI Thyroid Disease dataset:

- `allhypo.data`
- `allhyper.data`
- `allhypo.test`
- `allhyper.test`

Rather than simply concatenating the datasets, we paired records using their original dataset record identifiers.

This allowed us to combine the hypothyroid and hyperthyroid classification information while checking that corresponding records contained consistent input features.

We also implemented safeguards to detect duplicate identifiers, mismatched records, unrecognized labels, and conflicting thyroid classifications.

The resulting dataset contained:

| Dataset partition | Negative | Hypothyroid | Hyperthyroid | Total |
|---|---:|---:|---:|---:|
| Training | 2,503 | 220 | 77 | 2,800 |
| Testing | 876 | 71 | 25 | 972 |
| **Total** | **3,379** | **291** | **102** | **3,772** |

This distribution highlights a significant challenge: the negative category is substantially more common than the hypothyroid and hyperthyroid categories.

As a result, overall accuracy alone is insufficient for evaluating model performance.

### 4. Feature Engineering and Data Preprocessing

Our three-class classifier uses 28 input features from the original UCI dataset.

These include:

**Demographic information:** Age and sex.

**Medical history:** Thyroid surgery, radioactive iodine treatment, thyroid hormone replacement, antithyroid medication, lithium use, goiter, and other recorded clinical indicators.

**Laboratory measurements:** TSH, T3, TT4, T4U, and FTI.

**Additional dataset information:** Laboratory measurement indicators and referral-source categories.

We developed a preprocessing pipeline using scikit-learn's `ColumnTransformer` and `Pipeline` classes.

Numerical features are converted into numeric values, with missing measurements imputed using the median learned from the training data.

Categorical features are processed using most-frequent-value imputation and one-hot encoding.

This preprocessing pipeline is included in the saved model, ensuring that the same transformations are applied during training and inference.

We also excluded the original TBG measurement value from the model's input features.

### 5. Random Forest Model Training

We selected a Random Forest classifier because it can model nonlinear relationships, accommodate numerical and categorical inputs after preprocessing, and capture interactions among multiple thyroid-related variables.

Our final three-class model uses:

- **Algorithm:** Random Forest
- **Number of trees:** 300
- **Class weighting:** Balanced
- **Random state:** 42
- **Preprocessing:** Numerical imputation and categorical encoding

To improve validation reliability, we implemented a grouped, stratified validation strategy using `StratifiedGroupKFold`.

This approach keeps records with identical feature patterns together within the training or validation partition, reducing the risk that repeated input patterns artificially improve validation performance.

We trained the validation model using 2,240 records and evaluated it using 560 validation records.

After validation, the final model was retrained on all 2,800 records in the official training partition.

### 6. Data Quality and Overlap Investigation

During model development, we investigated whether identical feature patterns appeared in both the official training and test partitions.

Our initial overlap investigation identified 11 matching feature patterns involving 20 training records and 13 test records. All identified records belonged to the negative category, and no conflicting classifications were detected.

After revising the feature-pattern comparison procedure, our updated script reported zero shared patterns across the official training and test partitions.

The updated investigation also identified 2,753 unique feature patterns among 2,800 training records and 969 unique patterns among 972 test records.

Because the initial and updated overlap checks produced different results, further verification is necessary before drawing definitive conclusions about cross-partition duplication or potential leakage.

We retained these checks as part of our development process to improve transparency and evaluation reliability.

## Three-Class Model Results

### Grouped Validation Results

Our grouped validation evaluation produced:

- **Accuracy:** 97.86%
- **Balanced accuracy:** 92.04%
- **Macro F1-score:** 89.78%

These metrics demonstrate that the model learned distinguishing patterns across the three historical thyroid categories, although performance differed among classes.

### Official Test Results

On the official held-out test partition containing 972 records, our final model achieved:

- **Accuracy:** 98.66%
- **Balanced accuracy:** 91.73%
- **Macro F1-score:** 92.12%

The confusion matrix was:

| Actual classification | Predicted Negative | Predicted Hypothyroid | Predicted Hyperthyroid |
|---|---:|---:|---:|
| Negative | 869 | 3 | 4 |
| Hypothyroid | 0 | 71 | 0 |
| Hyperthyroid | 6 | 0 | 19 |

The model correctly classified 869 of 876 negative records and all 71 hypothyroid records.

However, it correctly classified only 19 of 25 hyperthyroid records, with six hyperthyroid records incorrectly classified as negative.

This corresponds to the following class-specific recall values:

- **Negative:** 99.20%
- **Hypothyroid:** 100%
- **Hyperthyroid:** 76%

These results suggest that the model is effective at distinguishing several patterns within the historical dataset, but its comparatively lower hyperthyroid recall demonstrates an important limitation.

The small number of hyperthyroid examples also makes its performance estimate less reliable than the overall accuracy might suggest.

### Model Artifacts

After training, we saved the complete preprocessing and classification pipeline using Joblib.

The generated files include:

- `models/clinical_thyroid_three_class.joblib` — trained three-class Random Forest pipeline
- `models/three_class_evaluation_report.json` — validation and test metrics, confusion matrices, dataset information, and model limitations

These artifacts allow the trained classifier to be loaded into the ThyroAI application without retraining every time the interface runs.

## AI Integration into ThyroGuard

### ThyroAI: Three-Class Research Interface

Following model development, we updated ThyroAI's Streamlit interface to use the newly trained three-class Random Forest model instead of the earlier binary hypothyroidism classifier.

The updated interface includes sections for:

**Patient information:** Age and sex, represented using the model's expected input format.

**Medical history:** Thyroid-related medications, previous treatments, and relevant clinical indicators.

**Thyroid laboratory measurements:** TSH, T3, TT4, T4U, and FTI, with support for missing values.

**Research classification results:** Predicted dataset category and Random Forest classification scores.

**Assessment history:** A session-based history of completed research assessments, with CSV export functionality.

The application loads the saved model using Joblib and constructs an input record matching the features used during model training.

It then applies the saved preprocessing pipeline and Random Forest classifier to generate an experimental classification.

We also simplified the interface by removing the historical UCI referral-source dropdown, which would be difficult for ordinary patients to interpret. The underlying model still expects that feature and handles its missing value through the trained preprocessing pipeline.

This is an interface simplification rather than a complete removal of referral-source influence. Retraining without that feature remains a future improvement.

### Classification Scores and Interpretability

ThyroAI displays the model's three classification scores alongside the predicted historical dataset category.

These scores represent the Random Forest model's outputs and should not be interpreted as calibrated probabilities that a patient has a thyroid disorder.

The interface also displays the submitted laboratory values and communicates the limitations of the research model.

Future development will focus on adding more interpretable model explanations, including feature contributions and explainable AI methods such as SHAP.

## Supporting Application Features

**ThyroidTrend:** Organizes thyroid laboratory measurements and visualizes changes over time to help users recognize trends in their recorded health information.

**SymptomWatch:** Allows users to record and monitor symptoms, creating a structured history of changes in their condition.

**FollowUpGuard:** Tracks follow-up appointments and monitoring plans to support consistent long-term health management.

**Patient Management:** Organizes patient profiles and associated health records within a centralized interface.

**Reports:** Provides downloadable summaries and exports of recorded health information to support documentation and communication.

Together, these features establish the foundation for a comprehensive thyroid health-monitoring platform that combines structured recordkeeping, symptom tracking, laboratory visualization, and preliminary machine-learning research.

## Model Limitations and Future Validation

Although our machine-learning models demonstrated promising performance on historical test records, they are not clinically validated diagnostic systems.

Several important limitations remain.

**Historical dataset limitations:** The models were trained using historical UCI records that may not reflect modern clinical populations, laboratory practices, or disease prevalence.

**Class imbalance:** Hyperthyroid records are substantially less common than negative records, limiting the reliability of class-specific performance estimates.

**Feature compatibility:** The original dataset's laboratory measurement units, coding conventions, and feature definitions must be verified before accepting real patient laboratory results.

**Data leakage investigation:** The discrepancy between our original and revised cross-partition overlap investigations requires further verification.

**Clinical generalization:** Performance on the UCI dataset does not establish that the model will perform equally well on new patients or independent healthcare datasets.

**Classification interpretation:** The dataset's negative category should not be interpreted as confirmation of normal thyroid function.

**Prediction calibration:** Random Forest classification scores are not automatically calibrated medical risk estimates.

With additional development time, we would conduct extensive cross-validation, investigate potential data leakage, improve hyperthyroid classification performance, and evaluate the model using independent clinical datasets.

We would also retrain the model without historical metadata features that are not meaningful to patients, verify laboratory units, evaluate prediction calibration, and incorporate explainable AI techniques.

Clinical expert review and prospective validation would be necessary before considering any real-world medical application.

## What We'd Do Next

Our next development priorities include improving ThyroAI's interface, strengthening model evaluation, and expanding the integration between machine learning and longitudinal health monitoring.

We plan to:

1. Resolve the remaining feature-overlap discrepancy and independently verify our evaluation procedure.
2. Verify laboratory units and historical feature definitions before supporting real patient-entered measurements.
3. Improve hyperthyroid classification using additional training data and appropriate evaluation methods.
4. Investigate model calibration and explainability using techniques such as SHAP.
5. Retrain the model without referral-source metadata and compare performance.
6. Integrate research classification results into ThyroGuard's reporting and tracking features.
7. Test the application after deployment and strengthen data privacy and security protections.
8. Evaluate future models using independent, more diverse datasets and clinical expert feedback.

Ultimately, ThyroGuard demonstrates the technical feasibility of combining machine-learning classification with structured thyroid health monitoring.

Our goal is to continue developing a more transparent, reliable, and accessible system that helps users organize and understand their thyroid-related information while supporting, rather than replacing, professional medical evaluation.

## Sources

- UCI Machine Learning Repository — Thyroid Disease Dataset: https://archive.ics.uci.edu/dataset/102/thyroid+disease
- Scikit-learn — Random Forest Classifier: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html
- Scikit-learn — StratifiedGroupKFold: https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.StratifiedGroupKFold.html
- Streamlit — https://streamlit.io/
- Pandas — https://pandas.pydata.org/
- Plotly — https://plotly.com/python/
- GitHub — https://github.com/alpaca822/ThyroGuard

**AI development assistance:** OpenAI ChatGPT was used for coding guidance, debugging, and project documentation.
