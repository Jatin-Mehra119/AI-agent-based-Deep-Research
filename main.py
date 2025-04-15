import os
import asyncio
import streamlit as st
from datetime import datetime
from modules.workflow_setup import app
from langchain_core.messages import HumanMessage

# Configure Streamlit page
st.set_page_config(page_title="Research Assistant", layout="wide")
st.title("Automated Research Workflow")
st.markdown("Generate weekly company reports with automated research")

with st.sidebar:
    st.header("Parameters")
    company = st.text_input("Company Name", "")  
    keywords = st.text_input("Keywords", "")    
    exclude = st.text_input("Exclusions", "")
    guidelines = st.text_area("Additional Instructions", "")
    run_btn = st.button("Start Research")

# Create containers for different parts of the output
status_container = st.empty()
output_container = st.container()
report_container = st.container()

async def run_workflow(company, keywords, exclude, guidelines):
    # Initialize the state dictionary with more robust defaults
    state = {
        "company": company,
        "company_keywords": keywords,
        "exclude_keywords": exclude,
        "report": "",
        "documents": {},
        "RAG_docs": {},
        "messages": [HumanMessage(content="Research initialized")],
        "iteration": 0
    }
    
    output_history = []
    
    # Stream the workflow execution
    try:
        async for step in app.astream(state):
            # Get the latest message if available
            if "messages" in step and step["messages"]:
                latest_msg = step["messages"][-1]
                if hasattr(latest_msg, "content"):
                    # Add to our history and update the UI
                    msg_content = latest_msg.content
                    output_history.append(msg_content)
                    # Update the display
                    status_container.info(f"Step: {step.get('iteration', '?')}")
                    output_container.markdown("## Progress\n" + "\n".join(output_history[-5:]))
                    
                    # If we have a report, show it in the report container
                    if "report" in step and step["report"]:
                        report_container.markdown("## Generated Report")
                        report_container.markdown(step["report"])
                        
                        # Look for PDF files in the reports directory
                        report_dir = "reports"
                        if os.path.exists(report_dir):
                            # Get PDF files that match the company name
                            safe_company = "".join([c for c in company if c.isalnum() or c.isspace()]).strip()
                            pdf_files = [f for f in os.listdir(report_dir) 
                                         if f.endswith('.pdf') and safe_company in f]
                            
                            if pdf_files:
                                # Get the most recent PDF file
                                latest_pdf = max([os.path.join(report_dir, f) for f in pdf_files], 
                                                 key=os.path.getmtime)
                                
                                # Offer as a download
                                with open(latest_pdf, "rb") as f:
                                    report_container.download_button(
                                        label="Download PDF Report",
                                        data=f.read(),
                                        file_name=os.path.basename(latest_pdf),
                                        mime="application/pdf"
                                    )
                        
    except Exception as e:
        status_container.error(f"Workflow error: {str(e)}")
        return None
        
    return step  # Return the final state

if run_btn:
    if not company.strip():
        st.error("Please enter a company name before starting research.")
    else:
        with st.spinner("Research in progress..."):
            try:
                final_state = asyncio.run(run_workflow(company, keywords, exclude, guidelines))
                
                if final_state:
                    status_container.success("Research completed successfully!")
                    
                    # Find the latest PDF file in the reports folder
                    report_dir = "reports"
                    if os.path.exists(report_dir):
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
                        else:
                            st.warning("No PDF reports found in the reports directory.")
                    else:
                        st.warning("Reports directory not found.")
                else:
                    st.error("Workflow completed but returned no final state.")
            except Exception as e:
                st.error(f"Error in workflow execution: {str(e)}")