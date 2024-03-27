import streamlit as st

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
    layout="wide"
)

st.write("# Welcome to our Question Generator Application! 👋")

st.text("Please select an application on the left <-")

st.sidebar.success("Select a demo above.")


st.markdown("""
<br>
<br>
<br>
<br>            
<div style='height: 100%; display: flex; flex-direction: column; justify-content: flex-end;'>
    <hr style='border-top: 1px solid #bbb;'>
    <p style='text-align: left;'>
        <b>Credits:</b> This app was developed by Hieu Pham and Milton Chen from the College of Business at the University of Alabama in Huntsville.</a>.
    </p>
    <p style='text-align: left;'>
        <b>Disclaimer:</b>  This is an experimental application and is provided "as-is" without any warranty, express or implied. We are sharing codes for academic purposes under the MIT license. Nothing herein is academic advice. By using this project, you hereby release and hold harmless the creators from any and all liability or responsibility for any claims, damages, losses, liabilities, costs, and expenses arising from or related to your use of the project.<br>
        <br>
        Please note that the use of the OpenAI's GPT language models can be expensive due to its token usage. By utilizing this project, you acknowledge that you are responsible for monitoring and managing your own token usage and the associated costs. It is highly recommended to check your OpenAI API usage regularly and set up any necessary limits or alerts to prevent unexpected charges.
    </p>
</div>
""", unsafe_allow_html=True)
