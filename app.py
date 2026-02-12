# --- File: app.py (Single-File Resume Builder) ---

from flask import Flask, request
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
import warnings

# --- 1. CONFIGURATION ---
app = Flask(__name__)
warnings.filterwarnings("ignore")

# SECURITY NOTE: In a real project, never hardcode your API key.
# Use: os.getenv("GOOGLE_API_KEY")
os.environ["GOOGLE_API_KEY"] = "AIzaSyCgqM3dvPXBeDn2lTEkl8UpSof6jk3WAWQ"

# --- 2. GEMINI SETUP (Modern LCEL Syntax) ---
try:
    # UPDATED: Using a supported 2026 model name
    # gemini-1.5-flash is retired. Use gemini-2.5-flash or gemini-3-flash
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash") 

    prompt_template = PromptTemplate(
        input_variables=["user_description"],
        template="""
        Create a professional resume based on the following information:
        {user_description}
        The resume should include the following sections:
        - Personal Information
        - Summary
        - Work Experience
        - Skills
        
        DO NOT use Markdown symbols like #, * or **.
        Write section headers like "SUMMARY" and "WORK EXPERIENCE" in ALL CAPS.
        """
    )
    
    # Chain using pipe operator
    resume_chain = prompt_template | llm | StrOutputParser()
    
except Exception as e:
    print(f"FATAL SETUP ERROR: {e}")
    resume_chain = None


# --- 3. CORE LOGIC FUNCTION ---
def generate_resume_text(user_description: str) -> str:
    """Generates a resume using LangChain/Gemini."""
    if not resume_chain:
        return "ERROR: AI Chain not initialized. Check API Key."
    if not user_description:
        return "Please provide a description."
        
    try:
        # We use .invoke() instead of .run() in the new LangChain version
        resume = resume_chain.invoke({"user_description": user_description})
        return resume
    except Exception as e:
        return f"An API Error occurred: {e}"


# --- 4. FLASK ROUTES ---

@app.route('/', methods=['GET', 'POST'])
def resume_builder():
    if request.method == 'POST':
        user_description = request.form.get('user_description', '')
        resume_output = generate_resume_text(user_description)
        
        # Replace newlines with HTML breaks for display
        safe_resume_output = resume_output.replace('\n', '<br>')
        return get_results_html(user_description, safe_resume_output)
    
    return get_input_form_html()


# --- 5. INLINE HTML TEMPLATES ---
# (Keeping your existing HTML functions)

def get_input_form_html():
    return """
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Professional Resume Builder</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
        :root { --color-primary: #1a73e8; --color-text: #3c4043; --color-border: #dadce0; }
        body { font-family: 'Roboto', sans-serif; max-width: 800px; margin: 0 auto; padding: 40px 20px; color: var(--color-text); background-color: #f8f9fa; }
        form { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); border: 1px solid var(--color-border); }
        textarea { width: 100%; min-height: 200px; padding: 15px; box-sizing: border-box; border-radius: 8px; border: 1px solid var(--color-border); font-family: inherit; }
        button { background-color: var(--color-primary); color: white; padding: 15px; border: none; border-radius: 8px; width: 100%; cursor: pointer; font-size: 1.1em; margin-top: 20px; }
        h1 { color: var(--color-primary); text-align: center; }
    </style>
</head>
<body>
    <h1>Professional Resume Builder</h1>
    <form method="POST">
        <label><b>Enter your details:</b></label><br><br>
        <textarea name="user_description" required placeholder="Name, Contact, Experience, Skills..."></textarea>
        <button type="submit">✨ Generate Resume</button>
    </form>
</body>
</html>
    """

def get_results_html(description, resume):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Results</title>
        <style>
            body {{ font-family: sans-serif; max-width: 800px; margin: auto; padding: 20px; line-height: 1.6; }}
            pre {{ background: white; padding: 20px; border: 1px solid #ddd; border-radius: 8px; white-space: pre-wrap; }}
            .box {{ background: #fffde7; padding: 15px; border-left: 5px solid #fbbc05; margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <h1>🎉 Your Resume</h1>
        <div class="box"><b>Input:</b> {description}</div>
        <pre>{resume}</pre>
        <a href="/">Generate another</a>
    </body>
    </html>
    """

if __name__ == '__main__':
    app.run(debug=True)