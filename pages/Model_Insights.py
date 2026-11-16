
import streamlit as st
import pandas as pd
import plotly.express as px

from utils.navigation import render_sidebar
from utils.ui import load_css, page_header


# ---------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------

st.set_page_config(
    page_title="Model Insights | ThyroGuard",
    page_icon="📊",
    layout="wide",
)

load_css()
render_sidebar()

page_header(
    "Model Insights",
    "Explore how ThyroAI was trained, evaluated, "
    "and integrated into ThyroGuard.",
)

st.info(
    "Research prototype: These results describe "
    "performance on historical UCI thyroid records. "
    "They do not establish clinical diagnostic accuracy."
)


# ---------------------------------------------
# MODEL OVERVIEW
# ---------------------------------------------

st.markdown("### Our machine-learning model")

st.write(
    "ThyroAI uses a Random Forest classifier trained "
    "to identify three categories in the historical "
    "UCI Thyroid Disease dataset: negative, "
    "hypothyroid, and hyperthyroid."
)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Algorithm", "Random Forest")
col2.metric("Training records", "2,800")
col3.metric("Test records", "972")
col4.metric("Input features", "28")

st.caption(
    "The negative dataset label does not necessarily "
    "mean clinically normal thyroid function."
)

st.divider()


# ---------------------------------------------
# PERFORMANCE METRICS
# ---------------------------------------------

st.markdown("### Model performance")

tab1, tab2 = st.tabs([
    "Official test results",
    "Grouped validation",
])

with tab1:
    a, b, c = st.columns(3)
    a.metric("Accuracy", "98.66%")
    b.metric("Balanced accuracy", "91.73%")
    c.metric("Macro F1-score", "92.12%")

    st.write(
        "These metrics were calculated using the "
        "official held-out test partition of 972 records."
    )

with tab2:
    a, b, c = st.columns(3)
    a.metric("Accuracy", "97.86%")
    b.metric("Balanced accuracy", "92.04%")
    c.metric("Macro F1-score", "89.78%")

    st.write(
        "Grouped stratified validation was used to "
        "reduce the chance that repeated feature "
        "patterns appeared in both training and "
        "validation partitions."
    )

with st.expander("What do these metrics mean?"):
    st.markdown(
        """
        **Accuracy:** Percentage of all predictions
        that matched their dataset labels.

        **Balanced accuracy:** Average recall across
        the three categories, giving each category
        equal weight.

        **Macro F1-score:** Average of the three
        category-specific F1-scores, giving each
        category equal weight.
        """
    )

st.divider()


# ---------------------------------------------
# CLASS DISTRIBUTION
# ---------------------------------------------

st.markdown("### Dataset composition")

distribution = pd.DataFrame({
    "Category": [
        "Negative",
        "Hypothyroid",
        "Hyperthyroid",
    ],
    "Training": [2503, 220, 77],
    "Testing": [876, 71, 25],
})

st.dataframe(
    distribution,
    hide_index=True,
    use_container_width=True,
)

fig_distribution = px.bar(
    distribution.melt(
        id_vars="Category",
        var_name="Partition",
        value_name="Records",
    ),
    x="Category",
    y="Records",
    color="Partition",
    barmode="group",
    title="Training and test class distribution",
    color_discrete_sequence=[
        "#008DB4",
        "#17344A",
    ],
)

fig_distribution.update_layout(
    template="plotly_white",
    height=380,
)

st.plotly_chart(
    fig_distribution,
    use_container_width=True,
)

st.warning(
    "The dataset is imbalanced: hyperthyroid records "
    "are much less common than negative records. "
    "This is one reason we report balanced accuracy "
    "and macro F1-score alongside overall accuracy."
)

st.divider()


# ---------------------------------------------
# CLASS-SPECIFIC RECALL
# ---------------------------------------------

st.markdown("### Performance by thyroid category")

recall_df = pd.DataFrame({
    "Category": [
        "Negative",
        "Hypothyroid",
        "Hyperthyroid",
    ],
    "Recall (%)": [
        869 / 876 * 100,
        100.0,
        19 / 25 * 100,
    ],
})

fig_recall = px.bar(
    recall_df,
    x="Category",
    y="Recall (%)",
    color="Category",
    text="Recall (%)",
    title="Recall on the official test dataset",
    color_discrete_sequence=[
        "#008DB4",
        "#17344A",
        "#6B8E9E",
    ],
)

fig_recall.update_traces(
    texttemplate="%{text:.1f}%",
    textposition="outside",
)

fig_recall.update_layout(
    template="plotly_white",
    showlegend=False,
    yaxis_range=[0, 110],
    height=400,
)

st.plotly_chart(
    fig_recall,
    use_container_width=True,
)

st.write(
    "The model correctly identified all 71 "
    "hypothyroid records in the test partition, "
    "but only 19 of 25 hyperthyroid records. "
    "Six hyperthyroid records were incorrectly "
    "classified as negative."
)

st.divider()


# ---------------------------------------------
# CONFUSION MATRIX
# ---------------------------------------------

st.markdown("### Confusion matrix")

labels = [
    "Negative",
    "Hypothyroid",
    "Hyperthyroid",
]

confusion_matrix = [
    [869, 3, 4],
    [0, 71, 0],
    [6, 0, 19],
]

matrix_df = pd.DataFrame(
    confusion_matrix,
    index=labels,
    columns=labels,
)

fig_matrix = px.imshow(
    matrix_df,
    text_auto=True,
    color_continuous_scale=[
        "#F2FAFC",
        "#008DB4",
        "#17344A",
    ],
    labels={
        "x": "Predicted category",
        "y": "Actual category",
        "color": "Records",
    },
    title="Official test confusion matrix",
    aspect="auto",
)

fig_matrix.update_layout(
    height=430,
)

st.plotly_chart(
    fig_matrix,
    use_container_width=True,
)

st.caption(
    "Rows represent actual dataset labels; "
    "columns represent model predictions. "
    "Diagonal cells are correct classifications."
)

st.divider()


# ---------------------------------------------
# TRAINING METHODOLOGY
# ---------------------------------------------

st.markdown("### How we trained ThyroAI")

with st.expander("1. Dataset preparation", expanded=True):
    st.write(
        "We combined the UCI allhypo and allhyper "
        "training and test files by matching their "
        "record identifiers. This produced 2,800 "
        "training records and 972 test records."
    )

with st.expander("2. Preprocessing"):
    st.write(
        "Numerical features were processed using "
        "median imputation. Categorical features "
        "were processed using most-frequent-value "
        "imputation and one-hot encoding. "
        "Preprocessing was incorporated into a "
        "scikit-learn pipeline."
    )

with st.expander("3. Model configuration"):
    st.code(
        """RandomForestClassifier(
    n_estimators=300,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)""",
        language="python",
    )

with st.expander("4. Model evaluation"):
    st.write(
        "We evaluated the model using grouped "
        "stratified validation and the official "
        "held-out test partition. We reported "
        "accuracy, balanced accuracy, macro "
        "F1-score, and a confusion matrix."
    )

st.divider()


# ---------------------------------------------
# LIMITATIONS
# ---------------------------------------------

st.markdown("### Limitations and future research")

st.markdown(
    """
    **Historical data:** The training records may
    not represent modern clinical populations.

    **Class imbalance:** Hyperthyroid records
    are relatively uncommon, making performance
    estimates less reliable.

    **Laboratory compatibility:** The original
    dataset's measurement conventions have not
    been fully verified for modern lab reports.

    **Data overlap:** Earlier and revised
    overlap checks produced different results,
    requiring further investigation.

    **Clinical validation:** The classifier has
    not been validated for medical diagnosis.

    **Prediction calibration:** Classification
    scores should not be interpreted as
    calibrated disease probabilities.
    """
)

st.markdown("### Future improvements")

st.write(
    "Our next research goals include investigating "
    "data overlap, improving hyperthyroid recall, "
    "verifying laboratory units, testing independent "
    "datasets, and exploring explainable AI methods "
    "such as SHAP."
)

st.divider()

st.caption(
    "ThyroGuard | Machine Learning Research "
    "Dashboard | Educational Prototype"
)
