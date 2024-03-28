import streamlit as st

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
    layout="wide"
)

st.write("# Welcome to our Question Generator Application! 👋")


st.markdown("""
Please select an application on the left 👈

Explore our three interactive options: **Text**, **Images**, and **PDFs**. Each option leverages the power of ChatGPT models to provide a tailored experience:

| Application | Interaction Mode                                                    | Description |
|-------------|---------------------------------------------------------------------|-------------|
| **Text**    | Direct Text Input                                                   | Engage directly with ChatGPT models through text. Ideal for queries, conversations, and text analysis. |
| **Images**  | Image Upload                                                        | Interact with ChatGPT models by uploading images. Perfect for image-based inquiries and analyses. |
| **PDFs**    | PDF Upload                                                          | Upload PDF documents to extract text and interact with ChatGPT models. Suitable for document analysis and information extraction. |

**Note:** This application is still in its experimental phase. We are actively fixing bugs and refining features. As Brian Fantana from *Anchorman: The Legend of Ron Burgundy* famously remarked:

> "60% of the time, it works every time."

We appreciate your patience and feedback as we continue to improve this application!
""")


st.sidebar.success("Select a demo above.")


st.markdown("""
<br>
<br>
<br>
<br>            
<div style='height: 100%; display: flex; flex-direction: column; justify-content: flex-end;'>
    <hr style='border-top: 1px solid #bbb;'>
    <p style='text-align: left;'>
        <b>Credits:</b> This app was developed by Hieu Pham from the College of Business at the University of Alabama in Huntsville</a>.
    </p>
    <p style='text-align: left;'>
        <b>Disclaimer:</b>  This is an experimental application and is provided "as-is" without any warranty, express or implied. We are sharing codes for academic purposes under the MIT license. Nothing herein is academic advice. By using this project, you hereby release and hold harmless the creators from any and all liability or responsibility for any claims, damages, losses, liabilities, costs, and expenses arising from or related to your use of the project.<br>
        <br>
        Please note that the use of the OpenAI's GPT language models can be expensive due to its token usage. By utilizing this project, you acknowledge that you are responsible for monitoring and managing your own token usage and the associated costs. It is highly recommended to check your OpenAI API usage regularly and set up any necessary limits or alerts to prevent unexpected charges.
    </p>
</div>
""", unsafe_allow_html=True)
