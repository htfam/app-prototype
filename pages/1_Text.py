import streamlit as st
import requests
import pandas as pd
from canvasapi import Canvas
import json
from openai import OpenAI
from datetime import datetime
import subprocess
import tempfile
import os
import shutil
import ast

# Set page configuration to use wide mode, making better use of screen space
st.set_page_config(page_title="Text Only", layout="wide")

def format_quiz_display(questions):
    quiz_content = ""
    alpha = 'abcdefghijklmnopqrstuvwxyz'  # For indexing multiple choice options

    for i, question in enumerate(questions, start=1):
        # Add the question text
        quiz_content += f"{i}. {question['question_text']}\n"

        if question['question_type'] == 'multiple_choice_question':
            for idx, ans in enumerate(question['answers']):
                prefix = "*" if ans['weight'] == 100 else ""
                quiz_content += f"{prefix}{alpha[idx]}) {ans['answer_text']}\n"
                
        elif question['question_type'] == 'true_false_question':
            correct_answer = "True" if question['answers'][0]['weight'] == 100 else "False"
            quiz_content += f"*a) {correct_answer}\nb) {'False' if correct_answer == 'True' else 'True'}\n"
            
        elif question['question_type'] == 'essay_question':
            quiz_content += "___\n"
        
        quiz_content += "\n"

    return quiz_content

def format_quiz(questions):
    quiz_content = "\nQuiz title: Quiz\n"
    alpha = 'abcdefghijklmnopqrstuvwxyz'  # For indexing multiple choice options

    for i, question in enumerate(questions, start=1):
        # Add the question text
        quiz_content += f"{i}. {question['question_text']}\n"

        if question['question_type'] == 'multiple_choice_question':
            for idx, ans in enumerate(question['answers']):
                prefix = "*" if ans['weight'] == 100 else ""
                quiz_content += f"{prefix}{alpha[idx]}) {ans['answer_text']}\n"
                
        elif question['question_type'] == 'true_false_question':
            correct_answer = "True" if question['answers'][0]['weight'] == 100 else "False"
            quiz_content += f"*a) {correct_answer}\nb) {'False' if correct_answer == 'True' else 'True'}\n"
            
        elif question['question_type'] == 'essay_question':
            quiz_content += "___\n"
        
        quiz_content += "\n"

    return quiz_content

def add_question_to_quiz(quiz, question_data):
    for question in question_data:
        quiz.create_question(question=question)

# Function to create quiz
def create_quiz(canvas_domain, canvas_token, course_id, quiz_data):
    canvas = Canvas(canvas_domain, canvas_token)
    course = canvas.get_course(course_id)
    quiz = course.create_quiz(quiz=quiz_data)
    return quiz

def chat_prompting(question):
    global conversation_history
    # Append the user's question to the conversation history
    conversation_history.append({"role": "user", "content": f"{question}, I want {st.session_state['question_number']} total."})

    # Make the API call
    response = client.chat.completions.create(
        model=openai_model,  # Make sure to use the correct model here
        messages=conversation_history
    )

    # Extract the text from the response
    answer = response.choices[0].message.content

    # Append the assistant's response to the conversation history
    conversation_history.append({"role": "assistant", "content": answer})

    #Return the assistant's response
    return answer


def convert_to_json(input_data):
    try:
        # Try parsing the input data as JSON directly
        parsed_data = json.loads(input_data)
    except json.JSONDecodeError:
        # If parsing as JSON fails, it might be a Python literal string
        try:
            # Convert string that looks like a Python dict/list to actual Python object
            python_object = ast.literal_eval(input_data)
            # Convert the Python object back to a JSON string
            parsed_data = json.dumps(python_object)
        except (ValueError, SyntaxError):
            # Handle cases where input_data is neither valid JSON nor a valid Python literal
            raise ValueError("Input data is neither valid JSON nor a valid Python literal.")
    return parsed_data

st.title("Question Creator from Text")


        


# Moving configuration options to the sidebar
with st.sidebar:

    # st.session_state['openai_api_key'] = st.text_input("Enter your OpenAI API Key:",
    #                         type="password")
    
    openai_model = st.selectbox('OpenAI Model', ['gpt-3.5-turbo-0125',
                                               'gpt-3.5-turbo-1106', 'gpt-4-0125-preview',
                                               'gpt-4-1106-preview', 'gpt-4-vision-preview',
                                               'gpt-4-1106-vision-preview'])
    
    upload_to_canvas = st.radio("Are you interested in uploading to Canvas?", ('Yes', 'No'), index = 1)

    if upload_to_canvas == 'Yes':   
        canvas_token = st.text_input("Enter your Canvas API Token:",
                                    type="password")

        canvas_domain = st.text_input("Enter your Canvas Domain (e.g. 'https://AAA.instructure.com'):")  # Or use st.text_input to allow dynamic input
        course_id = st.text_input("Enter your Course ID:")
        
        # Option to choose action
        action = st.radio("Do you want to create a new quiz or add questions to an existing quiz?", 
                        ('Create New Quiz', 'Add to Existing Quiz'))
        
        if action == 'Create New Quiz':
            quiz_title = st.text_input('Quiz Title', value='Quiz ' + datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
            quiz_description = st.text_area('Quiz Description', value='This is a test quiz.', height=100)
            quiz_type = st.selectbox('Quiz Type', ['assignment', 'graded_survey', 'survey', 'practice_quiz'])
        else:
            existing_quiz_id = st.text_input("Enter Existing Quiz ID:")
            
        if st.button('Submit'):
            # #print(st.session_state['response_text'])
            # cleaned_response_text = st.session_state['response_text'].replace("```json", "").replace("```", "").strip()
            # #print(cleaned_response_text)
            # question_data = json.loads(cleaned_response_text)
            # #print(question_data)

            # if not isinstance(question_data, list):
            #     question_data = [question_data]
            
            if action == 'Create New Quiz':
                # Input fields for quiz details
                quiz_data = {
                    'title': quiz_title,
                    'description': quiz_description,
                    'quiz_type': quiz_type
                }
                # Create the quiz
                quiz = create_quiz(canvas_domain, canvas_token, course_id, quiz_data)
                st.success(f'Quiz created successfully with ID: {quiz.id}')
            else:
                # Use an existing quiz
                quiz = Canvas(canvas_domain, canvas_token).get_course(course_id).get_quiz(existing_quiz_id)
                st.success(f'Adding questions to existing quiz with ID: {existing_quiz_id}')
            
            # Add questions to the quiz
            add_question_to_quiz(quiz, st.session_state['all_selected_questions'])
            st.success('Questions added to the quiz.')
    
    if st.button('Refresh App'):
        st.session_state.clear() 
        st.rerun()


quiz_example = [

    {
        'question_name': 'First Question',
        'question_text': 'What is 2 + 2?',
        'question_type': 'numerical_question',
        'points_possible': 1,
        'answers': [{'answer_text': '4', 'numerical_answer_type': 'exact_answer'}]
    },
    {
        'question_name': 'Second Question',
        'question_text': 'What is the capital of France?',
        'question_type': 'short_answer_question',
        'points_possible': 1,
        'answers': [{'answer_text': 'Paris', 'answer_weight': 100}]
    },
    {
        "question_name": "Third Question",
        "question_text": "At what temperature does water boil at sea level?",
        "question_type": "multiple_choice_question",
        "points_possible": 1,
        "answers": [
            {"answer_text": "100°C", "weight": 100},
            {"answer_text": "90°C", "weight": 0},
            {"answer_text": "0°C", "weight": 0},
            {"answer_text": "50°C", "weight": 0}
        ]
    },
    {
        "question_name": "Fourth Question",
        "question_text": "The Earth is flat.",
        "question_type": "true_false_question",
        "points_possible": 1,
        "answers": [
            {"answer_text": "True", "weight": 0},
            {"answer_text": "False", "weight": 100}
        ]
    },
    {
        "question_name": "Essay: Importance of Education",
        "question_text": "Discuss the importance of education in society.",
        "question_type": "essay_question",
        "points_possible": 10,
        "answers": []
        },
        {
        "question_name": "File Upload: Project Submission",
        "question_text": "Upload your project file here.",
        "question_type": "file_upload_question",
        "points_possible": 10,
        "answers": [] 
        }
]

conversation_history = [
    {"role": "system", "content": f"You are a professor who is a great educator."},
    {"role": "user", "content": f"If I ask you to create a question, please format your output for the canvasapi, i.e. as a python dictionary. Following the example formatting exactly. \nHere is an example of how to format the output:\n{quiz_example}"},
    {"role": "user", "content": "If the question involves a table of values, please embed the table directly in the question in HTML format. Only output the python dictionary and nothing else not even comments."},
    {"role": "user", "content": "If I do not ask for a question, simply respond normally."}
]
# Define client for OpenAI API
client = OpenAI(
    api_key=st.session_state['openai_api_key']
)




# Initialize 'response_text' in Streamlit's session state if it's not already set
if 'response_text' not in st.session_state:
    st.session_state['response_text'] = ""
if 'question_data' not in st.session_state:
    st.session_state['question_data'] = []
if 'all_selected_questions' not in st.session_state:
    st.session_state['all_selected_questions'] = []  # This will store all selected questions across generations.

# Use st.columns to create two columns
col1, col2 = st.columns([1, 1.75], gap="medium")

with col1:
    # Input field for the number of questions
    st.session_state['question_number'] = st.selectbox("How many questions would you like?",
                                                    options = ('1', '2', '3', '4', '5', '6', '7', '8', '9', '10'),
                                                    index = 0)

    # Input field for the question creation and the number of questions
    question = st.text_area("Enter your question prompt:", value = "Create a multiple choice supply chain question")
    if st.button("Generate"):
        st.session_state['response_text'] = chat_prompting(question)
        cleaned_response_text = st.session_state['response_text'].replace("```json", "").replace("```", "").strip()

        #question_data = json.loads(cleaned_response_text)
        question_data = ast.literal_eval(cleaned_response_text)
        # if not isinstance(question_data, list):
        #     print("IFSTATEMENT")
        #     question_data = [question_data]

        st.session_state['question_data'] = question_data
        st.text_area("Generated Question:", value=format_quiz_display(st.session_state['question_data']), height=350, key="response")
        #st.session_state['generate_clicked'] = True

    if 'form_question_selections' not in st.session_state:
        st.session_state['form_question_selections'] = list()

    #st.session_state['form_question_selections']

    with st.form("question_selection_form"):
        new_selections = []  # Temporarily store the current form's selections
        st.write("Which question(s) would you like to keep?")
        for i, question in enumerate(st.session_state['question_data']):
            # Render checkbox and store its state
            selected = st.checkbox(f"Question {i+1}", key=f"select_question_{i}")
            new_selections.append(selected)
        
        # On form submission, update the selections in session state
        submitted = st.form_submit_button("Submit Selections")
        if submitted:
            # Append newly selected questions to the persistent list of all selected questions.
            for i, selected in enumerate(new_selections):
                if selected and st.session_state['question_data'][i] not in st.session_state['all_selected_questions']:
                    st.session_state['all_selected_questions'].append(st.session_state['question_data'][i])

with col2:
    # Display all selected questions
    st.write("Selected Questions:")
    #for question in st.session_state['all_selected_questions']:
    st.text(format_quiz_display(st.session_state['all_selected_questions']))


    # Button to generate quiz and QTI file
    if st.button('Generate QTI File'):
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.txt') as tmp_quiz_file:
            tmp_quiz_file.write(format_quiz(st.session_state['all_selected_questions']))
            tmp_quiz_file.flush()  # Make sure content is written

            # Assuming text2qti is accessible and installed in the environment
            subprocess.run(['text2qti', tmp_quiz_file.name], shell=False)
            qti_output_filename = os.path.splitext(tmp_quiz_file.name)[0] + ".zip"

        # Offer the QTI file for download
        if os.path.exists(qti_output_filename):
            with open(qti_output_filename, "rb") as fp:
                btn = st.download_button(
                    label="Download QTI File",
                    data=fp,
                    file_name="quiz.qti.zip",
                    mime="application/zip"
                )
            os.remove(qti_output_filename)  # Clean up the QTI file after offering it for download
        else:
            st.error("Failed to generate the QTI file.")

        os.remove(tmp_quiz_file.name)  # Clean up the temporary quiz file
