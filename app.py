import streamlit as st
import pypdf
from openai import OpenAI

def extract_text_from_pdf(file):
    pdf = pypdf.PdfReader(file)
    text = ""
    for page in pdf.pages:
        text += page.extract_text() + "\n"
    return text

def get_detailed_answer_from_openai(client, question_type, highlighted_text):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that provides detailed answers to questions based on highlighted text from a document."
                },
                {
                    "role": "user",
                    "content": f"Provide a detailed answer to the following question: {question_type} about '{highlighted_text}'. Include explanations and examples if relevant."
                }
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: Unable to get response from OpenAI API. Error: {str(e)}"

st.title("PDF Highlighter and Detailed Answer Generator")

# Add input for OpenAI API key
api_key = st.text_input("Enter your OpenAI API key:", type="password")

# Initialize OpenAI client
if api_key:
    client = OpenAI(api_key=api_key)
else:
    client = None

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    text = extract_text_from_pdf(uploaded_file)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f'<div style="height: 400px; overflow-y: scroll;">{text}</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div id="highlight-area"></div>', unsafe_allow_html=True)
        
        highlighted_text = st.text_input("Highlighted text:")
        question_type = st.selectbox("Select question type:", ["How", "Why", "Details"])
        
        if st.button("Generate Detailed Answer") or st.session_state.get('generate_answer', False):
            if highlighted_text and client:
                with st.spinner("Generating detailed answer..."):
                    detailed_answer = get_detailed_answer_from_openai(client, question_type, highlighted_text)
                st.markdown("### Detailed Answer")
                st.write(detailed_answer)
                st.session_state['generate_answer'] = False
            elif not client:
                st.warning("Please enter your OpenAI API key.")
            else:
                st.warning("Please highlight some text first.")

    # Add JavaScript for text selection and keyboard shortcut
    js = """
    <script>
    const textElement = document.querySelector('.stMarkdown');
    const highlightArea = document.getElementById('highlight-area');
    
    textElement.addEventListener('mouseup', function() {
        const selection = window.getSelection();
        const highlightedText = selection.toString().trim();
        if (highlightedText) {
            document.querySelector('.stTextInput input').value = highlightedText;
            highlightArea.textContent = 'Selected: ' + highlightedText;
        }
    });
    
    document.addEventListener('keydown', function(e) {
        if (e.key === 'r' || e.key === 'R') {
            // Use Streamlit's event system to trigger the button click
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: true,
                key: 'generate_answer'
            }, '*');
        }
    });
    </script>
    """
    st.markdown(js, unsafe_allow_html=True)