import streamlit as st
from PIL import Image
from datetime import datetime
import pandas as pd
import json
from module.data_cleaner_module.data_cleaning_utils.rows_definer_utils import parse_text_to_json, custom_sort, classify_income, drop_duplicates_from_dataframe

class Keypress_Decoder:
    def __init__(self):
        pass

    def run3(self):
        st.title('Keypresses Decoder🔑')
        st.markdown("### Upload Script OR JSON Files (.txt, .json format)")
        uploaded_file = st.file_uploader("Choose a txt with formatting or json with flow-mapping file", type=['txt', 'json'], key='keypress_file_uploader')

        flow_no_mappings = {}

        if uploaded_file is not None:
            file_content = uploaded_file.getvalue().decode("utf-8")

            try:
                # Try loading as JSON first
                flow_no_mappings = json.loads(file_content)
            except json.JSONDecodeError:
                # If JSON decoding fails, attempt parsing as plain text
                flow_no_mappings = parse_text_to_json(file_content)

            # Debug information in a dropdown box
            with st.expander("Show FlowNo Mappings"):
                st.write("FlowNo Mappings:", flow_no_mappings)

            if flow_no_mappings:
                st.success("Questions and answers parsed successfully. ✨")
            else:
                st.error("Parsed data is empty. Check file content and parsing logic.")
        else:
            st.info("Please upload a file to parse questions and their answers.")

        simple_mappings = {k: v for question in flow_no_mappings.values() for k, v in question["answers"].items()}
        for q_key, q_data in flow_no_mappings.items():
            for answer_key, answer_value in q_data["answers"].items():
                simple_mappings[answer_key] = answer_value

        if 'renamed_data' not in st.session_state:
            st.session_state['renamed_data'] = pd.DataFrame()

        if 'renamed_data' in st.session_state and not st.session_state['renamed_data'].empty:
            renamed_data = st.session_state['renamed_data']

            sorted_columns = sorted(renamed_data.columns, key=custom_sort)
            renamed_data = renamed_data[sorted_columns]
            st.session_state['renamed_data'] = renamed_data
            st.write("Preview of Renamed Column Data:")
            st.dataframe(renamed_data.head())

            keypress_mappings = {}
            drop_cols = []
            excluded_flow_nos = {}

            question_columns = renamed_data.columns[1:-1]
            for i, col in enumerate(question_columns, start=1):
                st.subheader(f"Q{i}: {col}")
                unique_values = [val for val in renamed_data[col].unique() if pd.notna(val)]
                sorted_unique_values = sorted(unique_values, key=lambda x: int(x.split('=')[1]) if '=' in x and x.split('=')[1] else float('inf'))

                if st.checkbox(f"Drop entire Question {i}", key=f"exclude_{col}"):
                    drop_cols.append(col)
                    continue

                ### Decoder ###
                all_mappings = {}
                excluded_flow_nos[col] = []

                for idx, val in enumerate(sorted_unique_values):
                    if pd.notna(val):
                        autofill_value = simple_mappings.get(val, "")
                        unique_key = f"{col}_{val}_{idx}"
                        if st.checkbox(f"Drop '{val}'", key=f"exclude_{unique_key}"):
                            excluded_flow_nos[col].append(val)
                            continue

                        readable_val = st.text_input(f"Rename '{val}' to:", value=autofill_value, key=unique_key)
                        if readable_val:
                            all_mappings[val] = readable_val

                if all_mappings:
                    keypress_mappings[col] = all_mappings

            if st.button("Decode Keypresses"):
                if drop_cols:
                    renamed_data.drop(columns=drop_cols, inplace=True)
                for col, col_mappings in keypress_mappings.items():
                    if col in renamed_data.columns:
                        renamed_data[col] = renamed_data[col].map(col_mappings).fillna(renamed_data[col])
                        for val_to_exclude in excluded_flow_nos.get(col, []):
                            renamed_data = renamed_data[renamed_data[col] != val_to_exclude]

                if 'IncomeRange' in renamed_data.columns:
                    income_group = renamed_data['IncomeRange'].apply(classify_income)
                    income_range_index = renamed_data.columns.get_loc('IncomeRange')
                    renamed_data.insert(income_range_index + 1, 'IncomeGroup', income_group)

                renamed_data = drop_duplicates_from_dataframe(renamed_data)
                st.session_state['renamed_data'] = renamed_data
                st.markdown("### Decoded Data")
                st.write("Preview of Decoded Data:")
                st.dataframe(renamed_data)

                today = datetime.now()
                st.write(f'IVR count by Set as of {today.strftime("%d-%m-%Y").replace("-0", "-")}')
                st.write(renamed_data['Set'].value_counts())

                renamed_data.dropna(inplace=True)
                st.session_state['renamed_data'] = renamed_data
                st.write(f'No. of rows after dropping nulls: {len(renamed_data)} rows')

                st.session_state['total_CRs'] = renamed_data.shape[0]
                st.session_state['pick_up_rate_percentage'] = (st.session_state['total_pickups'] / st.session_state['total_calls_made']) * 100 if st.session_state['total_calls_made'] > 0 else 0
                st.session_state['cr_rate_percentage'] = (st.session_state['total_CRs'] / st.session_state['total_pickups']) * 100 if st.session_state['total_pickups'] > 0 else 0
  
                st.success("Files have been processed successfully.✨")
            
                st.markdown("### Final IVR Campaign Basic Statistics:")
                data = {
                    "Metric": ["Total calls made", "Total of pick-ups", "Pick-up Rate","Total Cleaned CRs", "CR Rate"],
                    "Value": [
                        f"{st.session_state['total_calls_made']:,}",
                        f"{st.session_state['total_pickups']:,}",
                        f"{st.session_state['pick_up_rate_percentage']:.2f}%",
                        f"{st.session_state['total_CRs']:,}",
                        f"{st.session_state['cr_rate_percentage']:.2f}%"
                    ]
                }
                df_stats = pd.DataFrame(data)
                df_stats.index = df_stats.index + 1
                st.table(df_stats)

                st.write(f'Preview of Total of Null Values per Column:')
                st.write(renamed_data.isnull().sum())

                st.markdown("### Sanity check for values in each column")
                
                if 'column_checks' not in st.session_state:
                    st.session_state['column_checks'] = {}

                def run_sanity_check(index, col, data):
                    st.write(f"{index}: {col}")
                    value_counts = data[col].value_counts(normalize=True, dropna=False)
                    st.write(value_counts)

                for index, col in enumerate(renamed_data.columns, start=0):
                    if col != 'phonenum':
                        run_sanity_check(index, col, renamed_data)
                        st.session_state['column_checks'][col] = True

                formatted_date = datetime.now().strftime("%Y%m%d")
                st.session_state['output_filename'] = f'IVR_Decoded_Data_v{formatted_date}.csv'

                def update_output_filename():
                    st.session_state['output_filename'] = st.session_state['output_filename_input'] + '.csv' if not st.session_state['output_filename_input'].lower().endswith('.csv') else st.session_state['output_filename_input']

                st.text_input("Edit the filename for download", value=st.session_state['output_filename'], key='output_filename_input', on_change=update_output_filename)
                data_as_csv = renamed_data.to_csv(index=False).encode('utf-8')
                st.download_button("Download Decoded Data as CSV", data=data_as_csv, file_name=st.session_state['output_filename'], mime='text/csv')
        else:
            st.error("No renamed data found. Please go back to the previous step and rename your data first.")