import streamlit as st
import pandas as pd
from datetime import datetime
from module.data_cleaner_module.data_cleaning_utils.data_cleaner import process_file 

class IVR_Data_Cleaner:
    def __init__(self):
        pass

    @staticmethod
    def set_dark_mode_css():
        dark_mode_css = """
        <style>
            html, body, [class*="View"] {
                color: #ffffff !important;  /* Text Color */
                background-color: #111111 !important;  /* Background Color */
            }
            .streamlit-container {
                background-color: #111111 !important;
            }
            .stTextInput > div > div > input {
                color: #ffffff !important;
            }
            /* You can add additional CSS rules here */
        </style>
        """
        st.markdown(dark_mode_css, unsafe_allow_html=True)

    def run(self):
        self.set_dark_mode_css()  # Apply the dark mode CSS
        st.title('IVR Data Cleaner💎')
        if 'processed' not in st.session_state:
            st.session_state['processed'] = False
            st.session_state['total_calls_made'] = 0
            st.session_state['total_pickups'] = 0
            st.session_state['total_CRs'] = 0

        if 'df_merge' not in st.session_state:
            st.session_state['df_merge'] = pd.DataFrame()
        
        if 'phonenum_combined' not in st.session_state:
            st.session_state['phonenum_combined'] = pd.DataFrame()
        
        if 'processed' not in st.session_state:
            st.session_state['processed'] = False
            st.session_state['all_data'] = []
            st.session_state['all_phonenum'] = []
            st.session_state['total_calls_made'] = 0
            st.session_state['total_pickups'] = 0
            st.session_state['file_count'] = 0

        st.markdown("### Upload IVR Files (.csv format)")

        uploaded_files = st.file_uploader("Choose CSV files", accept_multiple_files=True)

        if uploaded_files:
            st.write(f"Number of files uploaded: {len(uploaded_files)}")

        if st.button('Process'):
            with st.spinner("Processing the files..."):
                st.session_state['all_data'] = []
                st.session_state['all_phonenum'] = []
                st.session_state['total_calls_made'] = 0
                st.session_state['total_pickups'] = 0
                st.session_state['file_count'] = 0
                st.session_state['processed'] = True

                for uploaded_file in uploaded_files:
                    df_complete, phonenum_list, total_calls_made, total_of_pickups, df_merge ,df_list = process_file(uploaded_file)

                    st.session_state['all_data'].append(df_complete)
                    st.session_state['all_phonenum'].append(phonenum_list)
                    st.session_state['total_calls_made'] += total_calls_made
                    st.session_state['total_pickups'] += total_of_pickups
                    st.session_state['file_count'] += 1
                    st.session_state['total_CRs'] += len(df_complete)
                    st.session_state['df_merge'] = pd.concat([st.session_state['df_merge'], df_complete], ignore_index=True)
                    st.session_state['phonenum_combined'] = pd.concat([st.session_state['phonenum_combined']], ignore_index=True).drop_duplicates()
                
                if st.session_state['all_data']:
                    st.session_state['df_merge'] = pd.concat(st.session_state['all_data'], ignore_index=True)
                else:
                    st.session_state['df_merge'] = pd.DataFrame()

                if st.session_state['all_phonenum']:
                    st.session_state['phonenum_combined'] = pd.concat(st.session_state['all_phonenum'], ignore_index=True).drop_duplicates()
                else:
                    st.session_state['phonenum_combined'] = pd.DataFrame()

                st.session_state['processed'] = True

        if st.session_state['processed']:
            combined_data = pd.concat(st.session_state['all_data'], axis='index', ignore_index=True)
            combined_phonenum = pd.concat(st.session_state['all_phonenum'], axis=0).drop_duplicates()
            combined_phonenum.rename(columns={'PhoneNo': 'phonenum'}, inplace=True)

            st.session_state['total_CRs'] = combined_data.shape[0]
            st.session_state['pick_up_rate_percentage'] = (st.session_state['total_pickups'] / st.session_state['total_calls_made']) * 100 if st.session_state['total_calls_made'] > 0 else 0
            # st.session_state['cr_rate_percentage'] = (st.session_state['total_CRs'] / st.session_state['total_pickups']) * 100 if st.session_state['total_pickups'] > 0 else 0
                
            st.success("Files have been processed successfully.✨")
        
            st.markdown("### IVR Campaign Basic Statistics:")
            data = {
                "Metric": ["Total calls made", "Total of pick-ups", "Pick-up Rate"],
                "Value": [
                    f"{st.session_state['total_calls_made']:,}",
                    f"{st.session_state['total_pickups']:,}",
                    f"{st.session_state['pick_up_rate_percentage']:.2f}%",
                    # f"{st.session_state['cr_rate_percentage']:.2f}%"
                ]
            }
            df_stats = pd.DataFrame(data)
            df_stats.index = df_stats.index + 1
            st.table(df_stats)

            st.markdown("### Cleaned Data Preview:")
            st.dataframe(combined_data.head())

            formatted_date = datetime.now().strftime("%Y%m%d")
            default_filename = f'IVR_Cleaned_Data_v{formatted_date}.csv'
            output_filename = st.text_input("Edit the filename for download", value=default_filename)

            if not output_filename.lower().endswith('.csv'):
                output_filename += '.csv'
            
            st.session_state['cleaned_data'] = combined_data
            data_as_csv = combined_data.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Cleaned Data as CSV",
                data=data_as_csv,
                file_name=output_filename,
                mime='text/csv'
            )
    
            phonenum_combined = combined_data
            st.write(phonenum_combined)
            dup = phonenum_combined.duplicated().sum()
            phonenum_combined_cleaned = phonenum_combined.drop_duplicates()
        
            st.markdown("### Preview of Phone Numbers to be Excluded in the Next Sampling:")
            st.dataframe(phonenum_combined_cleaned.head())

            phone_data = {
                "Metric": [
                    "Total count of phone numbers that need to be excluded in the next sampling", 
                    "Total duplicated numbers", 
                    "Total numbers after dropping duplicate numbers"
                ],
                "Count": [
                    f"{phonenum_combined.shape[0]}",
                    f"{dup}",
                    f"{phonenum_combined_cleaned.shape[0]}"
                ]
            }
            df_phone_stats = pd.DataFrame(phone_data)
            df_phone_stats.index = df_phone_stats.index + 1
            st.table(df_phone_stats)

            formatted_date = datetime.now().strftime("%Y%m%d")
            default_filename_phonenum = f'IVR_Dialed_Phonenum_v{formatted_date}.csv'
            output_filename_phonenum = st.text_input("Edit the filename for download", value=default_filename_phonenum)

            if not output_filename_phonenum.lower().endswith('.csv'):
                output_filename_phonenum += '.csv'

            phonenum_data_as_csv = phonenum_combined.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Dialed Phone Numbers as CSV",
                data=phonenum_data_as_csv,
                file_name=output_filename_phonenum,
                mime='text/csv'
            )

            st.write("To continue to the Questionnaire Definition, please navigate to the 'Questionairre-Definer & Keypresses-Decoder🎉' app.")