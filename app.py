
import streamlit as st

from language_detector import detect_language
from claim_extractor import extract_claims
from evidence_retriever import retrieve_evidence
from fact_checker import check_claim
from reliability_score import calculate_reliability


# -----------------------------------
# Page configuration
# -----------------------------------

st.set_page_config(
    page_title="AI Answer Reliability Checker",
    page_icon="🔍",
    layout="wide"
)


# -----------------------------------
# Application heading
# -----------------------------------

st.title("🔍 AI Answer Reliability Checker")

st.write(
    "Analyze AI-generated answers, detect possible factual errors, "
    "and verify claims using retrieved evidence."
)

st.divider()


# -----------------------------------
# User input
# -----------------------------------

st.subheader("Enter an AI-generated answer")

answer = st.text_area(
    "Paste your answer here:",
    placeholder=(
        "Example: India became independent in 1947. "
        "Bengaluru is the capital of Karnataka."
    ),
    height=180
)

analyze_button = st.button(
    "Analyze Answer",
    type="primary",
    use_container_width=True
)


# -----------------------------------
# Analyze answer
# -----------------------------------

if analyze_button:

    if not answer.strip():

        st.warning("Please enter an answer before analyzing.")

    else:

        # Step 1: Detect language
        with st.spinner("Detecting language..."):

            language_info = detect_language(answer)

        st.subheader("1. Language Detection")

        col1, col2 = st.columns(2)

        col1.metric(
            "Detected Language",
            language_info["language"]
        )

        col2.metric(
            "Detection Confidence",
            f"{language_info['confidence'] * 100:.1f}%"
        )

        if not language_info["supported"]:

            st.warning(
                "This language is not in the currently supported "
                "language list (English, Hindi and Kannada). "
                "Results may be unreliable."
            )

        # Step 2: Extract claims
        claims = extract_claims(answer)

        st.subheader("2. Extracted Claims")

        if not claims:

            st.warning("No claims could be extracted.")

            st.stop()

        st.write(f"Total claims identified: **{len(claims)}**")

        for index, claim in enumerate(claims, start=1):

            st.write(f"{index}. {claim}")

        # Step 3: Retrieve evidence and fact-check
        st.subheader("3. Fact Checking")

        verification_results = []

        progress_bar = st.progress(0)

        status_text = st.empty()

        for index, claim in enumerate(claims):

            status_text.write(
                f"Checking claim {index + 1} of {len(claims)}..."
            )

            try:

                # Retrieve supporting information
                evidence_list = retrieve_evidence(claim)

                # Verify the claim
                result = check_claim(claim, evidence_list)

                # Store claim and its result
                result["claim"] = claim

                verification_results.append(result)

            except Exception as error:

                st.error(
                    f"Error while checking claim: {claim}\n\n{error}"
                )

                verification_results.append({
                    "claim": claim,
                    "result": "Insufficient Evidence",
                    "confidence": 0.0,
                    "evidence": None,
                    "source": None,
                    "title": None
                })

            progress_bar.progress(
                (index + 1) / len(claims)
            )

        status_text.success("Fact-checking completed!")

        # Step 4: Calculate reliability score
        st.subheader("4. Overall Reliability Score")

        score_data = calculate_reliability(
            verification_results
        )

        score = score_data["reliability_score"]

        st.metric(
            "Reliability Score",
            f"{score:.2f}%"
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Total Claims",
            score_data["total_claims"]
        )

        col2.metric(
            "Supported",
            score_data["supported"]
        )

        col3.metric(
            "Contradicted",
            score_data["contradicted"]
        )

        col4.metric(
            "Insufficient Evidence",
            score_data["insufficient"]
        )

        st.caption(
            "The score is calculated using supported and contradicted "
            "claims only. Claims with insufficient evidence are excluded."
        )

        # Step 5: Display individual results
        st.subheader("5. Detailed Verification Results")

        for index, item in enumerate(
            verification_results,
            start=1
        ):

            result = item["result"]

            if result == "Supported":
                icon = "✅"

            elif result == "Contradicted":
                icon = "❌"

            else:
                icon = "⚠️"

            with st.expander(
                f"{icon} Claim {index}: {item['claim']}",
                expanded=True
            ):

                st.write(
                    f"**Verification Result:** {result}"
                )

                st.write(
                    f"**Model Confidence:** "
                    f"{item['confidence']}%"
                )

                if item.get("title"):

                    st.write(
                        f"**Evidence Article:** {item['title']}"
                    )

                if item.get("evidence"):

                    st.write("**Retrieved Evidence:**")

                    st.write(item["evidence"])

                else:

                    st.info(
                        "No relevant evidence was retrieved."
                    )

                if item.get("source"):

                    st.markdown(
                        f"[Open Source Article]({item['source']})"
                    )

        st.divider()

        st.success(
            "Analysis completed successfully!"
        )

        st.caption(
            "This is an educational prototype. Its results depend on "
            "retrieval quality and model predictions and should not "
            "be treated as definitive proof of truth or falsehood."
        )
