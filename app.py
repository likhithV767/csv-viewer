import streamlit as st
import pandas as pd
import numpy as np

# Page config
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

def toggle_theme():
    st.session_state["theme"] = "dark" if st.session_state["theme"] == "light" else "light"

def get_theme_css(theme):
    return f"""
    <style>
    html, body, .stApp {{
        height: 100%;
        overflow: hidden !important; /* Stop scrolling */
    }}

    .css-1d391kg, .css-1y4p8pa {{
        overflow: auto !important; 
    }}


    .csv-table-container {{
        max-height: 70vh;  /* Limit height */
        overflow-y: auto;  /* Allow scrolling */
        border: 1px solid #ddd;
        padding: 5px;
    }}
    </style>
    """

st.sidebar.header("Interactive CSV Viewer", divider=True)
st.markdown(get_theme_css(st.session_state["theme"]), unsafe_allow_html=True)

col1, col2, col3 = st.sidebar.columns([1, 2, 2])

with col1:
    st.button(
        f"{'🌙' if st.session_state['theme'] == 'light' else '☀️'}",
        on_click=toggle_theme
    )

with col2:
    button_bg_color = "#4CAF50" if st.session_state['theme'] == 'light' else "#2b2b2b"
    button_text_color = "white" if st.session_state['theme'] == 'light' else "#4CAF50"
    st.markdown(
        f"<a href='https://text-compare.netlify.app/' target='_blank' style='text-decoration: none;'>"
        f"<button style='background-color: {button_bg_color}; color: {button_text_color}; border: none; padding: 5px 15px; border:1px solid #505158 ;border-radius: 5px;'>"
        "Text Compare"
        "</button></a>",
        unsafe_allow_html=True
    )

with col3:
    if "expander_visible" not in st.session_state:
        st.session_state["expander_visible"] = False

    def toggle_expander():
        st.session_state["expander_visible"] = not st.session_state["expander_visible"]

    st.sidebar.button("Json View", on_click=toggle_expander)

if st.session_state["expander_visible"]:
    with st.expander("JSON View", expanded=True):
        if st.session_state["selected_file"]:
            df = st.session_state["uploaded_files"][st.session_state["selected_file"]]
            if not df.empty:
                st.json(df.to_dict(orient="records"))
            else:
                st.warning("No data available.")
        else:
            st.warning("No file selected.")



uploaded_files = st.sidebar.file_uploader("", type="csv", accept_multiple_files=True)
if uploaded_files:
    for file in uploaded_files:
        if file.name not in st.session_state["uploaded_files"]:
            df = pd.read_csv(file, encoding="ISO-8859-1")
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
        # with col3:
        #     file_size_kb = df.memory_usage(deep=True).sum() / 1024
        #     st.metric("Size", f"{file_size_kb:.2f} KB")

        st.markdown('<div class="small-metric"></div>', unsafe_allow_html=True)
        
if st.session_state["selected_file"]:
    df = st.session_state["uploaded_files"][st.session_state["selected_file"]]

    st.subheader(f"{st.session_state['selected_file']}")

    col1, col2 = st.columns(2)  
    with col1:
        rows_per_page = st.slider("Rows per page", min_value=5, max_value=100, value=10, step=5)

    with col2:
        total_pages = int(np.ceil(df.shape[0] / rows_per_page))
        current_page = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1)

    start_idx = (current_page - 1) * rows_per_page
    end_idx = min(start_idx + rows_per_page, df.shape[0])

    st.caption(f"Showing rows {start_idx+1} to {end_idx} of {df.shape[0]}")
    
    df_slice = df.iloc[start_idx:end_idx] 
    # for idx, row in df_slice.iterrows():
    #     with st.expander(f"Details - Row {idx+1}"):
    #         st.write(row.to_dict())

    


    def df_to_interactive_html(df):
        html = f"""
        <style>
        *{{
            padding:'0';
            margin:'0';
        }}
                   .csv-table {{
            border-collapse: collapse;
            min-width: 100%;         
            font-family: Arial, sans-serif;
            table-layout: auto;
            background-color: {"#1e1e1e" if st.session_state['theme'] == 'dark' else "#ffffff"};
            color: {"#ffffff" if st.session_state['theme'] == 'dark' else "#131010"};
            box-shadow: 0px 35px 50px rgba( 0, 0, 0, 0.2 );
        }}
        .csv-table th, .csv-table td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
            vertical-align: top;
            word-wrap: break-word;
            overflow-wrap: break-word;
            position: relative;
            color: {"#ffffff" if st.session_state['theme'] == 'dark' else "#131010"};
        }}
        .csv-table th {{
            background-color: {"#333333" if st.session_state['theme'] == 'dark' else "#f2f2f2"};
            position: sticky;
            padding:'10px 0';
            top: 0;
            z-index: 10;
            font-weight: semi-bold;
            text-align: center;
        }}
      
        .csv-table tr:hover {{
            background-color: {"rgba(255, 255, 255, 0.3)" if st.session_state['theme'] == 'light' else "rgba(255, 255, 255, 0.1)"};
        }}
        .cell-content {{
            max-height: 80px;
            overflow: hidden;
            text-overflow: ellipsis;
            text-align: left;
            line-height: 1.2;
        }}
        .arrow-button {{
            position: absolute;
            bottom: 0;
            right: 0;
            cursor: pointer;
            background-color: {"#f2f2f2" if st.session_state['theme'] == 'light' else "#444444"};
            border: 1px solid #ddd;
            border-radius: 3px;
            width: 20px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            color: {"#131010" if st.session_state['theme'] == 'light' else "#ffffff"};
        }}
        .dialog-button {{
                  cursor: pointer;
            background-color: {"#4CAF50" if st.session_state['theme'] == 'light' else "#2b2b2b"};
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 12px;
        }}
        .dialog-button:hover {{
            opacity: 0.7;
        }}
        .dropdown-header {{
            display : flex;
            top:0px;
            right:5px;
        }}
        .dropdown-header button{{
            background-color: red;
            color: white;
            padding:5px 10px;
            border: none;
            border-radius:5px;
            cursor: pointer;
        }}
        .dropdown-header button:hover{{
            opacity: 0.7;
        }}
        .dropdown-content {{
            display: none;
            position: absolute;
            background-color: {"#333333" if st.session_state['theme'] == 'dark' else "#f2f2f2"};
            min-width: 500px;
            max-width: 500px;
            max-height: 300px;
            overflow-y: auto;
            box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2);
            padding: 8px;
            z-index: 100;
            border-radius: 4px;
            white-space: pre-wrap;
            word-wrap: break-word;
            line-height: 1.0;
            left: 0;
   
        }}
        .cell-action {{
            display: flex;
            position: absolute;
            bottom: 5px;
            right: 5px;
        }}
        td {{
            position: relative;
            height: 100px;
        }}
       
        </style>
        """

        html += "<table class='csv-table'>"
        html += "<thead><tr><th>Row</th>"

        for col in df.columns:
            html += f"<th>{col}</th>"
        html += "</tr></thead><tbody>"

        for i, (_, row) in enumerate(df.iterrows()):
            display_row_idx = start_idx + i + 1
            html += f"<tr><td>{display_row_idx}</td>" 

            for col_name, value in row.items():
                cell_id = f"cell_{display_row_idx}_{col_name}" 
                truncated = str(value)[:97] + "..." if len(str(value)) > 100 else str(value)

                html += f"""
                <td id='{cell_id}'>
                    <div class='cell-content'>{truncated}</div>
                    <div class='cell-action'>
                        <button class='dialog-button' onclick="showDialog('{display_row_idx}', '{col_name}', '{value}')">Details</button>
                    </div>
                </td>
                """
            html += "</tr>"
        html += "</tbody></table>"

        html += """
        <script>
        function copyToClipboard(text) {
            navigator.clipboard.writeText(text).then(function() {
            }, function(err) {
                console.error('Could not copy text: ', err);
            });
        }
function showDialog(rowIdx, colName, value) {
    setTimeout(() => {
        const dialog = document.createElement('div');
        dialog.id = "custom-dialog";
        dialog.style.position = 'fixed';
        dialog.style.top = '50%';
        dialog.style.left = '50%';
        dialog.style.transform = 'translate(-50%, -50%)';
        dialog.style.backgroundColor = '#1E201E';
        dialog.style.color = '#fff';
        dialog.style.padding = '10px 15px';
        dialog.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.5)';
        dialog.style.border = '1px solid #F5F5F5';
        dialog.style.borderRadius = '10px';
        dialog.style.zIndex = '1000';

        const content = document.createElement('p');
        content.style.whiteSpace = 'pre-wrap'; 
        content.style.wordBreak = 'break-word';
        content.textContent = `Row ${rowIdx}, Column '${colName}'\n\n${value}`; 

        const copyButton = document.createElement('button');
        copyButton.className = 'dialog-button';
        copyButton.textContent = 'Copy';
        copyButton.onclick = () => copyToClipboard(value);

        const closeButton = document.createElement('button');
        closeButton.className = 'dialog-button';
        closeButton.textContent = 'Close';
        closeButton.onclick = () => document.body.removeChild(dialog);

        dialog.appendChild(content);
        dialog.appendChild(copyButton);
        dialog.appendChild(closeButton);

        document.body.appendChild(dialog);
    }, 100);
}


       function closeDialog() {
    const dialog = document.getElementById('custom-dialog');
    if (dialog) {
        document.body.removeChild(dialog);
    }
}

        </script>
        """
        return html

    window_height = st.session_state.get("window_height",600) 
    table_height = window_height - 10

    st.components.v1.html(df_to_interactive_html(df_slice), height=table_height, scrolling=True)
    
else:
    st.info("Upload a CSV file to start viewing.")
