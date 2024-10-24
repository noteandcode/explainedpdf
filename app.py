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
                    "content": "You are a helpful assistant that provides detailed answers in Hungarian language. Always respond in Hungarian, regardless of the input language."
                },
                {
                    "role": "user",
                    "content": f"Provide a detailed answer in Hungarian to the following question: {question_type} about '{highlighted_text}'. Include explanations and examples if relevant."
                }
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Hiba: Nem sikerült választ kapni az OpenAI API-tól. Hiba: {str(e)}"

st.title("Orvosi PDF Szövegkiemelő és Részletes Válaszgenerátor")
st.header("A válaszokért semmilyen feleősséget nem vállalunk. A válaszok tájékoztató jellegűek", divider=True)
# Add input for OpenAI API key
api_key = st.text_input("Írd be az OpenAI API kulcsodat:", type="password")

# Initialize OpenAI client
if api_key:
    client = OpenAI(api_key=api_key)
else:
    client = None

uploaded_file = st.file_uploader("Válassz egy PDF fájlt", type="pdf")

if uploaded_file is not None:
    text = extract_text_from_pdf(uploaded_file)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f'<div style="height: 400px; overflow-y: scroll;">{text}</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div id="highlight-area"></div>', unsafe_allow_html=True)
        
        highlighted_text = st.text_input("Kiemelt szöveg:")
        question_type = st.selectbox("Válaszd ki a kérdés típusát:", ["Hogyan", "Miért", "Részletek"])
        
        if st.button("Válasz Generálása") or st.session_state.get('generate_answer', False):
            if highlighted_text and client:
                with st.spinner("Válasz generálása folyamatban..."):
                    detailed_answer = get_detailed_answer_from_openai(client, question_type, highlighted_text)
                st.markdown("### Részletes Válasz")
                st.write(detailed_answer)
                st.session_state['generate_answer'] = False
            elif not client:
                st.warning("Kérlek, add meg az OpenAI API kulcsodat.")
            else:
                st.warning("Kérlek, előbb jelölj ki szöveget.")

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
            highlightArea.textContent = 'Kijelölt szöveg: ' + highlightedText;
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
