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
    conversation_history.append({"role": "user", "content": question})

    # Make the API call
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Make sure to use the correct model here
        messages=conversation_history
    )

    # Extract the text from the response
    answer = response.choices[0].message.content

    # Append the assistant's response to the conversation history
    conversation_history.append({"role": "assistant", "content": answer})

    #Return the assistant's response
    return answer

st.title("Question Creator")


# Moving configuration options to the sidebar
with st.sidebar:

    openai_api_key = st.text_input("Enter your OpenAI API Key:",
                            type="password")
    
    # # Add a subject selection dropdown
    # subject_options = ['Management', 'Marketing', 'Finance',
    #                     'Economics', 'Accounting', 'Operations',
    #                     'Analytics', 'Information Systems']
    # # Create a select box that directly modifies session state
    # st.session_state['selected_subject'] = st.selectbox("What subject are you interested in?",
    #                                                   subject_options)
    
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
            #print(st.session_state['response_text'])
            cleaned_response_text = st.session_state['response_text'].replace("```json", "").replace("```", "").strip()
            print(cleaned_response_text)
            question_data = json.loads(cleaned_response_text)
            print(question_data)

            if not isinstance(question_data, list):
                question_data = [question_data]
            
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
            add_question_to_quiz(quiz, question_data)
            st.success('Questions added to the quiz.')
    
    if st.button('Refresh App'):
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
    {"role": "user", "content": f"If I ask you to create a question, please format your output for the canvasapi, i.e. in a JSON dictionary format. Following the example formatting exactly. \nHere is an example of how to format the output:\n{quiz_example}"},
    {"role": "user", "content": "If the question involves a table of values, please embed the table directly in the question in HTML format."},
    {"role": "user", "content": "If I do not ask for a question, simply respond normally."}
]
# Define client for OpenAI API
client = OpenAI(
    api_key=openai_api_key
)


# Initialize 'response_text' in Streamlit's session state if it's not already set
if 'response_text' not in st.session_state:
    st.session_state['response_text'] = ""

# Input field for the question creation and the number of questions
question = st.text_area("Enter your question prompt:")

# Function to convert the structured data into a human-friendly format
# def format_question_data(data):
#     data = data.replace("```json", "").replace("```", "").strip()
#     formatted_data = json.loads(data.strip('"'))
#     formatted_text = ""
#     for question in formatted_data:
#         name = question.get("question_name", "Unnamed Question")
#         text = question.get("question_text", "")
#         question_type = question.get("question_type", "Unknown Type").replace("_", " ").title()
#         points = question.get("points_possible", 0)
        
#         formatted_text += f"Question: {name}\nType: {question_type}\nPoints: {points}\n{text}\n\n"
#     return formatted_text.strip()



if st.button("Generate"):
    st.session_state['response_text'] = chat_prompting(question)
    st.text_area("Generated Question:", value=st.session_state['response_text'], height=150, key="response")
else:
    st.warning("Please enter a question and click generate.")


# Button to generate quiz and QTI file
if st.button('Generate QTI File'):
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.txt') as tmp_quiz_file:
        cleaned_response_text = st.session_state['response_text'].replace("```json", "").replace("```", "").strip()
        print(st.session_state['response_text'])
        question_data = json.loads(cleaned_response_text)
        print(question_data)
        if not isinstance(question_data, list):
            question_data = [question_data]
        print(format_quiz(question_data))
        tmp_quiz_file.write(format_quiz(question_data))
        tmp_quiz_file.flush()  # Make sure content is written

        # Assuming text2qti is accessible and installed in the environment
        subprocess.run(['text2qti', tmp_quiz_file.name], shell=True)
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
