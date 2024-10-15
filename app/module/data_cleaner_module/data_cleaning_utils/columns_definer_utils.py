import re
import json
import streamlit as st
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple

def parse_questions_and_answers(json_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Parses questions and their respective answers from a JSON data structure.

    Parameters:
    - json_data (dict): A dictionary containing questions as keys and their details (question text and answers) as values.

    Returns:
    - dict: A dictionary with question numbers as keys and a sub-dictionary containing the question text and a list of answers.
    """
    questions_and_answers = {}
    for q_key, q_value in json_data.items():
        question_text = q_value['question']
        answers = [answer for _, answer in q_value['answers'].items()]
        questions_and_answers[q_key] = {'question': question_text, 'answers': answers}
    return questions_and_answers

def parse_text_to_json(text_content: str) -> Dict[str, Dict[str, Any]]:
    """
    Converts structured text content into a JSON-like dictionary, parsing questions and their answers.

    Parameters:
    - text_content (str): Text content containing questions and answers in a structured format.

    Returns:
    - dict: A dictionary representing the parsed content with questions as keys and their details (question text and answers) as values.
    """
    data = {}
    question_re = re.compile(r'^(\d+)\.\s*(.*)')  # Adjusted to allow optional spaces after the period
    answer_re = re.compile(r'^\s*-\s*(.*)')  # Adjusted to allow optional spaces around the dash

    current_question = ""

    for line in text_content.splitlines():
        question_match = question_re.match(line)
        answer_match = answer_re.match(line)

        if question_match:
            q_number, q_text = question_match.groups()
            current_question = f"Q{q_number}"
            data[current_question] = {"question": q_text, "answers": {}}
        elif answer_match and current_question:
            answer_text = answer_match.groups()[0]
            flow_no = len(data[current_question]["answers"]) + 1
            flow_no_key = f"FlowNo_{int(q_number)+1}={flow_no}"
            data[current_question]["answers"][flow_no_key] = answer_text

    return data

def rename_columns(df: pd.DataFrame, new_column_names: List[str]) -> pd.DataFrame:
    """
    Renames dataframe columns based on a list of new column names.

    Parameters:
    - df (pd.DataFrame): The original DataFrame.
    - new_column_names (list): A list of new column names corresponding to the DataFrame's columns.

    Returns:
    - pd.DataFrame: A DataFrame with updated column names.
    """
    mapping = {old: new for old, new in zip(df.columns, new_column_names) if new}
    return df.rename(columns=mapping, inplace=False)

def process_file_content(uploaded_file: Optional[st.runtime.uploaded_file_manager.UploadedFile]) -> Tuple[Optional[Dict[str, Any]], Optional[str], Optional[str]]:
    """
    Process the content of the uploaded file.

    Parameters:
    - uploaded_file (Optional[st.runtime.uploaded_file_manager.UploadedFile]): The uploaded file.

    Returns:
    - Tuple[Optional[Dict[str, Any]], Optional[str], Optional[str]]: The parsed content, success message, and error message.
    """
    try:
        if uploaded_file and uploaded_file.type == "application/json":
            # Handle JSON file
            flow_no_mappings = json.loads(uploaded_file.getvalue().decode("utf-8"))
        else:
            # Handle plain text file
            flow_no_mappings = parse_text_to_json(uploaded_file.getvalue().decode("utf-8"))
        return flow_no_mappings, "Questions and answers parsed successfully.✨", None
    except Exception as e:
        return None, None, f"Error processing file: {e}"

def flatten_json_structure(flow_no_mappings: Dict[str, Any]) -> Dict[str, str]:
    """
    Flatten the JSON structure to simplify the mapping access.

    Parameters:
    - flow_no_mappings (Dict[str, Any]): The original JSON-like dictionary.

    Returns:
    - Dict[str, str]: The flattened dictionary.
    """
    if not flow_no_mappings:
        return {}
    return {k: v for question in flow_no_mappings.values() for k, v in question["answers"].items()}

def drop_duplicates_from_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Drops duplicate rows from the DataFrame.

    Parameters:
    - df (pd.DataFrame): The DataFrame from which duplicates will be removed.

    Returns:
    - pd.DataFrame: A DataFrame with duplicates removed.
    """
    return df.drop_duplicates()