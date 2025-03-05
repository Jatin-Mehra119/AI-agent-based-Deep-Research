import os
import asyncio
import streamlit as st
from datetime import datetime
from modules.models import ResearchState
from modules.workflow_setup import app
from langchain_core.messages import SystemMessage, HumanMessage

# Configure Streamlit page
st.set_page_config(page_title="Research Assistant", layout="wide")
st.title("Automated Research Workflow")
st.markdown("Generate weekly company reports with automated research")

with st.sidebar:
    st.header("Parameters")
    company = st.text_input("Company Name", "Google")
    keywords = st.text_input("Keywords", "business strategy")
    exclude = st.text_input("Exclusions", "financial results")
    guidelines = st.text_area("Additional Instructions")
    run_btn = st.button("Start Research")

output_area = st.empty()

async def run_workflow(company, keywords, exclude, guidelines):
    # Initialize the state dictionary
    state: ResearchState = {
        "company": company,
        "company_keywords": keywords,
        "exclude_keywords": exclude,
        "report": "",
        "documents": {},
        "RAG_docs": {},
        "messages": [SystemMessage("Research initialized")],
        "iteration": 0  # Start iteration count
    }
    
    if guidelines:
        state['messages'].append(HumanMessage(guidelines))
    
    async for step in app.astream(state):
        msg = step.get("messages", [{}])[-1].get("content", "")
        output_area.markdown(f"```\n{msg}\n```")
    
    return state

if run_btn:
    with st.spinner("Processing..."):
        try:
            final_state = asyncio.run(run_workflow(company, keywords, exclude, guidelines))
            st.success("Complete!")
            # Find the latest PDF file in the reports folder
            report_dir = "reports"
            pdf_files = [f for f in os.listdir(report_dir) if f.endswith('.pdf')]
            if pdf_files:
                latest_pdf = max([os.path.join(report_dir, f) for f in pdf_files], key=os.path.getmtime)
                with open(latest_pdf, "rb") as pdf_file:
                    st.download_button(
                        "Download Report (PDF)",
                        data=pdf_file.read(),
                        file_name=os.path.basename(latest_pdf),
                        mime="application/pdf"
                    )
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.warning("No PDF report generated yet.")