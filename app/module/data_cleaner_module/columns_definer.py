import streamlit as st
from PIL import Image
import json
from module.data_cleaner_module.data_cleaning_utils.columns_definer_utils import parse_questions_and_answers, parse_text_to_json, rename_columns

class Questionnaire_Definer:
    def __init__(self):
        pass

    def run2(self):
        st.title('Columns Definer 🍃')
        st.markdown("### Upload Script Files (.txt, .json format)")

        uploaded_file = st.file_uploader("Choose a txt with formatting or json with flow-mapping file", type=['txt','json'], key='questionnaire_file_uploader')
        file_parsed = False  # Track if a file has been parsed

        if uploaded_file is not None:
            file_contents = uploaded_file.getvalue().decode("utf-8")

            if uploaded_file.type == "application/json":
                try:
                    json_data = json.loads(file_contents)
                    parsed_data = parse_questions_and_answers(json_data)
                    st.session_state['qa_dict'] = parsed_data
                    st.success("JSON questions and answers parsed successfully.✨")
                    file_parsed = True
                except json.JSONDecodeError:
                    st.error("Error decoding JSON. Please ensure the file is a valid JSON format.")
            else:  # For text format
                parsed_data = parse_text_to_json(file_contents)
                st.session_state['qa_dict'] = parsed_data
                st.success("Text questions and answers parsed successfully.✨")
                file_parsed = True

        st.markdown("## Rename Columns")
        if 'cleaned_data' not in st.session_state:
            st.warning("No cleaned data available for renaming.")
        else:
            cleaned_data = st.session_state['cleaned_data']
            column_names_to_display = [col for col in cleaned_data.columns]  # Placeholder for actual column names

            new_column_names = []
            for idx, default_name in enumerate(column_names_to_display):
                if idx == 0:
                    default_value = "phonenum"
                elif idx == len(column_names_to_display) - 1:
                    default_value = "Set"
                elif file_parsed:
                    question_key = f"Q{idx}"
                    default_value = st.session_state['qa_dict'].get(question_key, {}).get('question', default_name)
                else:
                    default_value = default_name

                new_name = st.text_input(f"Column {idx+1}: {default_name}", value=default_value, key=f"new_name_{idx}")
                new_column_names.append(new_name)

            if st.button("Apply New Column Names"):
                updated_df = rename_columns(cleaned_data, new_column_names)
                st.session_state['renamed_data'] = updated_df
                st.write("DataFrame with Renamed Columns:")
                st.dataframe(updated_df.head())