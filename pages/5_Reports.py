
from utils.navigation import render_sidebar

import streamlit as st
from utils.navigation import render_sidebar
import pandas as pd

from io import BytesIO
from datetime import datetime
from xml.sax.saxutils import escape

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch

from database.db import (
    initialize_database,
    get_lab_entries,
    get_symptom_entries,
    get_followups,
)

from utils.ui import load_css, page_header
from utils.navigation import render_sidebar
from utils.patient_context import selected_patient_id


# --------------------------------------------------
# PAGE SETUP
# --------------------------------------------------

st.set_page_config(
    page_title="Reports | ThyroGuard",
    page_icon="🩺",
    layout="wide",
)

load_css()
initialize_database()
render_sidebar()

active_patient_id = selected_patient_id()

page_header(
    "Health reports",
    "Generate and export structured summaries of your "
    "thyroid health records for medical appointments.",
)

st.info(
    "Demonstration environment: Reports contain recorded "
    "information and are not medical diagnoses or advice."
)


# --------------------------------------------------
# DATA HELPERS
# --------------------------------------------------

def records_to_dataframe(records):
    """Convert SQLite rows, dictionaries, or tuples to a DataFrame."""

    if records is None:
        return pd.DataFrame()

    records = list(records)

    if not records:
        return pd.DataFrame()

    first = records[0]

    if hasattr(first, "keys"):
        return pd.DataFrame([
            {key: row[key] for key in row.keys()}
            for row in records
        ])

    return pd.DataFrame(records)


def prepare_export(df):
    """Remove internal identifiers from downloadable reports."""

    if df.empty:
        return df.copy()

    result = df.copy()

    internal_columns = {
        "id",
        "patient_id",
        "created_by",
        "updated_by",
    }

    result = result.drop(
        columns=[
            col for col in result.columns
            if str(col).lower() in internal_columns
        ],
        errors="ignore",
    )

    result.columns = [
        str(col).replace("_", " ").title()
        for col in result.columns
    ]

    return result.fillna("Not recorded")


def csv_bytes(df):
    return df.to_csv(index=False).encode("utf-8-sig")


# --------------------------------------------------
# PDF GENERATOR
# --------------------------------------------------

def generate_pdf(lab_df, symptom_df, followup_df, patient_id):

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=(8.5 * inch, 11 * inch),
        rightMargin=42,
        leftMargin=42,
        topMargin=48,
        bottomMargin=48,
    )

    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="ReportTitleCustom",
            parent=styles["Title"],
            fontSize=22,
            leading=27,
            textColor=colors.HexColor("#17344A"),
            spaceAfter=10,
        )
    )

    styles.add(
        ParagraphStyle(
            name="SectionCustom",
            parent=styles["Heading2"],
            fontSize=12,
            leading=16,
            textColor=colors.HexColor("#008DB4"),
            spaceBefore=15,
            spaceAfter=8,
        )
    )

    styles.add(
        ParagraphStyle(
            name="CellCustom",
            parent=styles["Normal"],
            fontSize=7,
            leading=10,
            wordWrap="CJK",
        )
    )

    story = []

    story.append(
        Paragraph(
            "THYROGUARD",
            styles["ReportTitleCustom"],
        )
    )

    story.append(
        Paragraph(
            "Thyroid Health Appointment Report",
            styles["Heading2"],
        )
    )

    story.append(
        Paragraph(
            f"Generated: {datetime.now():%B %d, %Y at %I:%M %p}",
            styles["Normal"],
        )
    )

    story.append(
        Paragraph(
            f"Selected demonstration patient ID: {patient_id}",
            styles["Normal"],
        )
    )

    story.append(Spacer(1, 16))

    story.append(
        Paragraph(
            "<b>Educational prototype.</b> "
            "This report summarizes recorded data only. "
            "It is not a medical diagnosis, treatment plan, "
            "or substitute for professional evaluation.",
            styles["Normal"],
        )
    )

    story.append(Spacer(1, 18))

    # ----------------------------------------------
    # SUMMARY
    # ----------------------------------------------

    story.append(
        Paragraph(
            "Report Overview",
            styles["SectionCustom"],
        )
    )

    summary_data = [
        ["Category", "Records"],
        ["Laboratory measurements", str(len(lab_df))],
        ["Symptom check-ins", str(len(symptom_df))],
        ["Follow-up records", str(len(followup_df))],
    ]

    summary_table = Table(
        summary_data,
        colWidths=[310, 160],
    )

    summary_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0),
             colors.HexColor("#E7F7FA")),
            ("TEXTCOLOR", (0, 0), (-1, 0),
             colors.HexColor("#17344A")),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
            ("TOPPADDING", (0, 0), (-1, -1), 9),
            ("LINEBELOW", (0, 0), (-1, -1),
             0.3, colors.HexColor("#DCE5EA")),
        ])
    )

    story.append(summary_table)

    # ----------------------------------------------
    # DATA SECTIONS
    # ----------------------------------------------

    def add_section(title, dataframe):

        story.append(
            Paragraph(title, styles["SectionCustom"])
        )

        if dataframe.empty:
            story.append(
                Paragraph(
                    "No records available.",
                    styles["Normal"],
                )
            )
            return

        # One record per block keeps wide datasets readable.
        for index, (_, record) in enumerate(
            dataframe.iterrows(), start=1
        ):
            block = [
                Paragraph(
                    f"<b>Entry {index}</b>",
                    styles["Normal"],
                ),
                Spacer(1, 5),
            ]

            rows = []

            for column, value in record.items():
                rows.append([
                    Paragraph(
                        escape(str(column)),
                        styles["CellCustom"],
                    ),
                    Paragraph(
                        escape(str(value)),
                        styles["CellCustom"],
                    ),
                ])

            table = Table(
                rows,
                colWidths=[170, 300],
                hAlign="LEFT",
            )

            table.setStyle(
                TableStyle([
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ROWBACKGROUNDS", (0, 0), (-1, -1),
                     [
                         colors.white,
                         colors.HexColor("#F3F7FA"),
                     ]),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("LINEBELOW", (0, 0), (-1, -1),
                     0.25, colors.HexColor("#DCE5EA")),
                ])
            )

            block.append(table)
            block.append(Spacer(1, 12))

            story.append(KeepTogether(block))

    add_section("Thyroid Laboratory History", lab_df)
    add_section("Symptom History", symptom_df)
    add_section("Follow-Up Records", followup_df)

    story.append(Spacer(1, 20))

    story.append(
        Paragraph(
            "Prepared with ThyroGuard | Educational research prototype",
            styles["Normal"],
        )
    )

    document.build(story)

    buffer.seek(0)

    return buffer.getvalue()


# --------------------------------------------------
# PATIENT DATA
# --------------------------------------------------

if active_patient_id is None:
    st.warning(
        "Please select a patient from the sidebar "
        "before generating a report."
    )
    st.stop()

labs = get_lab_entries(active_patient_id)
symptoms = get_symptom_entries(active_patient_id)
followups = get_followups(active_patient_id)

lab_df = prepare_export(records_to_dataframe(labs))
symptom_df = prepare_export(records_to_dataframe(symptoms))
followup_df = prepare_export(records_to_dataframe(followups))


# --------------------------------------------------
# REPORT OVERVIEW
# --------------------------------------------------

st.markdown("### Report overview")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Laboratory entries",
        len(lab_df),
    )

with col2:
    st.metric(
        "Symptom check-ins",
        len(symptom_df),
    )

with col3:
    st.metric(
        "Follow-up records",
        len(followup_df),
    )

st.caption(
    f"Selected demonstration patient ID: {active_patient_id}"
)

st.divider()


# --------------------------------------------------
# REPORT PREVIEW
# --------------------------------------------------

st.markdown("### Preview your report")

st.write(
    "Review the recorded information that will be "
    "included in your exported report."
)

tab1, tab2, tab3 = st.tabs([
    "Laboratory History",
    "Symptom History",
    "Follow-Up Records",
])

with tab1:
    if lab_df.empty:
        st.info("No laboratory entries recorded.")
    else:
        st.dataframe(
            lab_df,
            use_container_width=True,
            hide_index=True,
        )

with tab2:
    if symptom_df.empty:
        st.info("No symptom check-ins recorded.")
    else:
        st.dataframe(
            symptom_df,
            use_container_width=True,
            hide_index=True,
        )

with tab3:
    if followup_df.empty:
        st.info("No follow-up records available.")
    else:
        st.dataframe(
            followup_df,
            use_container_width=True,
            hide_index=True,
        )

st.divider()


# --------------------------------------------------
# REPORT EXPORT
# --------------------------------------------------

st.markdown("### Export your health report")

st.write(
    "Download a structured PDF report for appointments "
    "or export the underlying records as CSV files."
)

pdf_data = generate_pdf(
    lab_df,
    symptom_df,
    followup_df,
    active_patient_id,
)

st.download_button(
    label="📄 Download PDF Report",
    data=pdf_data,
    file_name=f"ThyroGuard_Report_{active_patient_id}.pdf",
    mime="application/pdf",
    type="primary",
    use_container_width=True,
)

st.markdown("#### Download individual datasets")

col1, col2, col3 = st.columns(3)

with col1:
    st.download_button(
        "Download Lab Data",
        data=csv_bytes(lab_df),
        file_name="thyroid_labs.csv",
        mime="text/csv",
        use_container_width=True,
    )

with col2:
    st.download_button(
        "Download Symptoms",
        data=csv_bytes(symptom_df),
        file_name="thyroid_symptoms.csv",
        mime="text/csv",
        use_container_width=True,
    )

with col3:
    st.download_button(
        "Download Follow-Ups",
        data=csv_bytes(followup_df),
        file_name="thyroid_followups.csv",
        mime="text/csv",
        use_container_width=True,
    )

st.caption(
    "Downloads contain the selected patient's records. "
    "Store exported files securely. "
    "This prototype is not intended for real patient data."
)
