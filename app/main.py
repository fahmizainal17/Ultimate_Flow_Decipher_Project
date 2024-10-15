import streamlit as st
import numpy as np
from utils.component import page_style
from utils.security import check_password
from module.data_cleaner_module.data_cleaner import IVR_Data_Cleaner
from module.data_cleaner_module.columns_definer import Questionnaire_Definer
from module.data_cleaner_module.rows_definer import Keypress_Decoder
from module.data_cleaner_module.dataframe_decoder import Questionnaire_Keypress_Decoder

if check_password():
    page_style()
    # Ensure to initialize the class
    ivr_cleaner = IVR_Data_Cleaner()

    # Ensure to initialize the class
    questionnaire_definer = Questionnaire_Definer()

    keypress_decoder = Keypress_Decoder()

    questionnaire_keypress_decoder = Questionnaire_Keypress_Decoder()

    # Set dark mode CSS
    ivr_cleaner.set_dark_mode_css()

    tab1, tab2, tab3, tab4 = st.tabs(["IVR_Data_Cleaner", "Questionnaire_Definer", "Keypress_Decoder", "Questionnaire_Keypress_Decoder"])

    with tab1:
        ivr_cleaner.run()

    with tab2:
        questionnaire_definer.run2()

    with tab3:
        keypress_decoder.run3()

    with tab4:
        questionnaire_keypress_decoder.run4()