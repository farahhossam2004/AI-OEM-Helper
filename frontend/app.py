
import os

import requests
import streamlit as st


API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")


st.set_page_config(
    page_title="AI OEM Helper",
    page_icon="🔧",
    layout="centered",
)

st.markdown(
    """
    <style>
    .stApp {
        background: #0C0D0E;
        color: #F5F4F0;
    }
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #76F28A;
        margin-bottom: 0;
    }
    .subtitle {
        color: #A5AAA5;
        margin-top: 5px;
        margin-bottom: 30px;
    }
    .result-card {
        background: #151719;
        border: 1px solid #303633;
        border-radius: 12px;
        padding: 18px;
        margin: 10px 0;
    }
    .oem-number {
        color: #76F28A;
        font-size: 1.4rem;
        font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    '<div class="main-title">AI OEM Helper</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="subtitle">Find OEM part number candidates using AI</div>',
    unsafe_allow_html=True,
)

st.markdown("### Describe your vehicle and the required part")

user_message = st.text_area(
    "Vehicle request",
    placeholder="Example: هوبات كامري 2026 أمامي\n"
                "Example: Toyota Camry 2026 front brake discs",
    height=120,
    label_visibility="collapsed",
)

st.caption(
    "You can describe the vehicle and part in Arabic or English."
)

if st.button("Find OEM Numbers", use_container_width=True):
    if not user_message.strip():
        st.warning("Please enter your vehicle and part details.")
    else:
        with st.spinner("Searching the catalog..."):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/api/v1/lookup",
                    json={"message": user_message.strip()},
                    timeout=30,
                )

                response.raise_for_status()
                result = response.json()

                st.markdown("### Result")

                status = result.get("status", "unknown")
                message = result.get("response", "")

                if status == "found":
                    st.success(message)
                elif status in ("needs_clarification", "invalid"):
                    st.warning(message)
                elif status in ("not_found",):
                    st.info(message)
                elif status == "quota_exceeded":
                    st.error(message)
                elif status == "unavailable":
                    st.error(message)
                else:
                    st.error(message or "Something went wrong.")

                catalog_result = result.get("catalog_result") or {}
                parts = catalog_result.get("parts") or []

                if parts:
                    st.markdown("### OEM Candidates")

                    for part in parts:
                        with st.container():
                            st.markdown(
                                f"""
                                <div class="result-card">
                                    <div class="oem-number">
                                        {part.get("oem_number", "N/A")}
                                    </div>
                                    <p>{part.get("description") or "No description available"}</p>
                                    <small>
                                        Status: Catalog candidate
                                    </small>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                    st.caption(
                        "These are catalog candidates, not guaranteed "
                        "fitment confirmations. Verify compatibility using "
                        "the VIN or the manufacturer's catalog."
                    )

            except requests.exceptions.Timeout:
                st.error("The request timed out. Please try again.")
            except requests.exceptions.ConnectionError:
                st.error(
                    "Cannot connect to the API. Make sure the FastAPI "
                    "server is running."
                )
            except requests.exceptions.HTTPError as error:
                st.error(f"API error: {error}")
            except requests.exceptions.RequestException as error:
                st.error(f"Request failed: {error}")
            except ValueError:
                st.error("The API returned an invalid response.")
