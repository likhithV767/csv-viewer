import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="CSV Viewer",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "uploaded_files" not in st.session_state:
    st.session_state["uploaded_files"] = {}
if "selected_file" not in st.session_state:
    st.session_state["selected_file"] = None
if "theme" not in st.session_state:
    st.session_state["theme"] = "dark"
if "view_mode" not in st.session_state:
    st.session_state["view_mode"] = "Table"  
if "show_text_compare" not in st.session_state:
    st.session_state["show_text_compare"] = False 
if "text_compare_diff" not in st.session_state:
    st.session_state["text_compare_diff"] = ""
if "clear_counter" not in st.session_state:
    st.session_state["clear_counter"] = 0  

def toggle_theme():
    st.session_state["theme"] = "dark" if st.session_state["theme"] == "light" else "light"

def toggle_text_compare():
    st.session_state["show_text_compare"] = not st.session_state["show_text_compare"]

def clear_text_compare():
    st.session_state["clear_counter"] += 1
    st.session_state["text_compare_diff"] = ""

def get_theme_css(theme):
    return f"""
    <style>
    html, body, .stApp {{
        height: 100%;
        overflow: hidden !important;
    }}
    .css-1d391kg, .css-1y4p8pa {{
        overflow: auto !important;
    }}
    </style>
    """

# Custom CSS to force text areas to expand to full width in their containers
st.markdown("""
    <style>
    div[data-testid="stTextArea"] > div > textarea {
        width: 100% !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.sidebar.header("Interactive CSV Viewer")
st.markdown(get_theme_css(st.session_state["theme"]), unsafe_allow_html=True)

with st.sidebar:
    uploaded_files = st.file_uploader("", type="csv", accept_multiple_files=True)
    if uploaded_files:
        for file in uploaded_files:
            if file.name not in st.session_state["uploaded_files"]:
                try:
                    df = pd.read_csv(file, encoding="ISO-8859-1")
                except Exception as e:
                    st.error(f"Error reading {file.name}: {e}")
                    continue
                st.session_state["uploaded_files"][file.name] = df
                if not st.session_state["selected_file"]:
                    st.session_state["selected_file"] = file.name

if st.session_state["uploaded_files"]:
    selected_file = st.sidebar.radio(
        "Select a file to view",
        list(st.session_state["uploaded_files"].keys()),
        index=list(st.session_state["uploaded_files"].keys()).index(st.session_state["selected_file"]),
    )
    st.session_state["selected_file"] = selected_file

if st.session_state["selected_file"]:
    df = st.session_state["uploaded_files"][st.session_state["selected_file"]]
    with st.sidebar:
        st.divider()
        st.caption("File Information")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Rows", df.shape[0])
        with col2:
            st.metric("Columns", df.shape[1])
        st.divider()
        st.session_state["view_mode"] = st.radio(
            "View Mode",
            options=["Table", "JSON"],
            index=["Table", "JSON"].index(st.session_state["view_mode"])
        )

if st.session_state["selected_file"]:
    df = st.session_state["uploaded_files"][st.session_state["selected_file"]]

    if st.session_state["view_mode"] == "JSON":
        st.subheader(f"{st.session_state['selected_file']} - JSON View")
        st.json(df.to_dict(orient="records"))
    elif st.session_state["view_mode"] == "Table":
        st.subheader(f"{st.session_state['selected_file']} - Table View")
        try:
            edited_df = st.data_editor(df, num_rows="dynamic")
        except Exception as e:
            st.warning("Data editor is not supported in your version of Streamlit.")
            edited_df = df
        st.session_state["uploaded_files"][st.session_state["selected_file"]] = edited_df
        st.caption("Changes saved automatically.")

    st.markdown("---")
    if st.button("Toggle Text Compare"):
        toggle_text_compare()

    if st.session_state["show_text_compare"]:
        key1 = f"text_compare_input1_{st.session_state['clear_counter']}"
        key2 = f"text_compare_input2_{st.session_state['clear_counter']}"
        
        col_texts = st.columns(2)
        with col_texts[0]:
            text1 = st.text_area("Text 1", key=key1, value="", height=200)
        with col_texts[1]:
            text2 = st.text_area("Text 2", key=key2, value="", height=200)

        col_actions = st.columns(2)
        with col_actions[0]:
            compare_clicked = st.button("Compare")
        with col_actions[1]:
            clear_clicked = st.button("Clear", on_click=clear_text_compare)
        
        if compare_clicked:
            import difflib
            words1 = text1.split()
            words2 = text2.split()
            matcher = difflib.SequenceMatcher(None, words1, words2)
            result = []
            for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                if tag == 'equal':
                    result.append(" ".join(words1[i1:i2]))
                elif tag == 'replace':
                    deleted = " ".join(words1[i1:i2])
                    inserted = " ".join(words2[j1:j2])
                    result.append(f"<span style='background-color: red; color: white;'>{deleted}</span>")
                    result.append(f"<span style='background-color: green; color: white;'>{inserted}</span>")
                elif tag == 'delete':
                    deleted = " ".join(words1[i1:i2])
                    result.append(f"<span style='background-color: red; color: white;'>{deleted}</span>")
                elif tag == 'insert':
                    inserted = " ".join(words2[j1:j2])
                    result.append(f"<span style='background-color: green; color: white;'>{inserted}</span>")
            st.session_state["text_compare_diff"] = " ".join(result)
        
        if st.session_state["text_compare_diff"]:
            st.markdown(st.session_state["text_compare_diff"], unsafe_allow_html=True)
else:
    st.info("Upload a CSV file to start viewing.")
