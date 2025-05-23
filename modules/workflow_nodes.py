"""
Workflow Nodes Module
=====================

This module defines the core nodes in the AI research workflow pipeline. Each node
represents a distinct step in the research process, from information gathering to
report generation and publishing.

The workflow follows these main steps:
1. Tool execution (search, extraction)
2. Research using AI models
3. Document curation and selection
4. Report generation
5. PDF publishing

Each function is designed to work with a ResearchState object that maintains the
state throughout the workflow execution process.
"""

import os
from datetime import datetime
import streamlit as st

from langchain_core.messages import AIMessage, ToolMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from modules.models import ResearchState, TavilyExtractInput, QuotedAnswer
from modules.pdf_utils import generate_pdf_from_md
from modules.tools import tools_by_name, tavily_client

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()
# Set up the Google API key for the Gemini model
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")


# Node: Tool Node – execute tools (e.g. search)
async def tool_node(state: ResearchState):
    """
    Execute AI-requested tools (like search operations) and process their results.
    
    This node processes tool calls made by the AI model, invokes the appropriate tools,
    collects new documents/information, and updates the state with the results.
    It also handles deduplication of documents based on URLs.
    
    Args:
        state (ResearchState): The current state of the research workflow
        
    Returns:
        dict: Updated state with new messages, documents, and iteration count
    """
    docs = state.get('documents', {})
    docs_str = ""
    msgs = []
    
    # Process each tool call in the latest message
    for tool_call in state["messages"][-1].tool_calls:
        tool = tools_by_name[tool_call["name"]]
        # Execute the tool with the provided arguments
        new_docs = await tool.ainvoke(tool_call["args"])
        
        # Process new documents and avoid duplicates
        for doc in new_docs:
            # Make sure that this document was not retrieved before
            if not docs or doc['url'] not in docs:
                docs[doc['url']] = doc
                docs_str += f"{doc['title']}: {doc['url']}\n"
        
        # Add a ToolMessage with more detailed information
        msgs.append(ToolMessage(
            content=f"Found the following new documents/information: {docs_str}",
            tool_call_id=tool_call["id"]
        ))
    
    # Return updated messages and documents
    return {
        "messages": msgs, 
        "documents": docs,
        "iteration": state.get('iteration', 0) + 1
    }

# Node: Research Model – perform research using Gemini
async def research_model(state: ResearchState):
    """
    Perform research using the Google Generative AI (Gemini) model.
    
    This node constructs a research prompt based on the current state,
    initializes a Gemini model with appropriate tool bindings, and invokes
    the model to gather information about the specified company.
    
    Args:
        state (ResearchState): The current state of the research workflow
        
    Returns:
        dict: Updated state with model's response messages
        
    Note:
        Includes error handling with Streamlit feedback for debugging purposes
    """
    # Build a prompt with current date, company, and keywords
    prompt = f"""Today's date is {datetime.now().strftime('%d/%m/%Y')}.\n
You are an expert researcher tasked with gathering information for a weekly report on recent developments in portfolio companies.\n
Your current objective is to gather documents about any significant events that occurred in the past week for the following company: {state['company']}.\n
The user has provided the following company keywords: {state['company_keywords']} to help you find documents relevant to the correct company.\n     
**Instructions:**\n
- Use the 'tavily_search' tool to search for relevant documents
- Focus on gathering documents by making appropriate tool calls
- If you believe you have gathered enough information, state 'I have gathered enough information and am ready to proceed.'
"""
    
    # Initialize Gemini model with tool bindings
    model = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",  
        temperature=0.2,
        max_output_tokens=4500
    ).bind_tools(list(tools_by_name.values()))
    
    # Convert system message to human message for Gemini
    # This is a workaround for Gemini's handling of system messages
    messages = state['messages']
    if len(messages) == 0 or isinstance(messages[0], SystemMessage):
        # Add the prompt as a HumanMessage instead of SystemMessage
        human_msg = HumanMessage(content=prompt)
        messages = [human_msg]
    else:
        # Append the prompt as a HumanMessage
        messages = messages + [HumanMessage(content=prompt)]
    
    # Invoke the model with the properly formatted messages
    try:
        response = await model.ainvoke(messages)
        return {"messages": [response]}
    except Exception as e:
        error_msg = f"Error in research_model: {str(e)}"
        st.error(error_msg)
        st.error(f"Message count: {len(messages)}")
        st.error(f"API Key present: {'Yes' if os.getenv('GOOGLE_API_KEY') else 'No'}")
        return {"messages": [AIMessage(content=error_msg)]}

# Conditional edge decision function
def should_continue(state: ResearchState) -> str:
    """
    Decide the next workflow step based on the current state.
    
    This function examines the current state to determine whether to:
    - Continue gathering information (tools)
    - Proceed to document curation (curate)
    
    Args:
        state (ResearchState): The current state of the research workflow
        
    Returns:
        str: Next workflow step, either "tools" or "curate"
        
    Decision logic:
    - If max iterations reached (5) -> curate
    - If model wants to use more tools -> tools
    - If model indicates completion -> curate
    - Default -> tools
    """
    last_msg = state['messages'][-1]
    
    # Check if we've reached max iterations (as a safety measure)
    if state.get('iteration', 0) >= 5:
        return "curate"
    
    # Check if the model has indicated it's done or if it's making more tool calls
    if last_msg.tool_calls:
        return "tools"
    elif "gathered enough information" in last_msg.content.lower():
        return "curate"
    else:
        # If no clear signal, default to continuing research
        return "tools"

# Node: Curate – analyze and select relevant documents
async def select_and_process(state: ResearchState):
    """
    Analyze and select the most relevant documents for report generation.
    
    This node filters the collected documents to identify those most relevant to the
    company of interest, considering keywords and exclusion criteria. It then
    extracts raw content from the selected URLs using the Tavily API.
    
    Args:
        state (ResearchState): The current state of the research workflow
        
    Returns:
        dict: Updated state with selected documents and their content
        
    Note:
        Includes error handling with Streamlit feedback for debugging purposes
    """
    # Build more detailed prompt
    prompt = f"""You are an expert researcher specializing in analyzing portfolio companies.\n
Your current task is to review a list of documents and select the most relevant URLs related to recent developments for the following company: {state['company']}.\n
Be aware that some documents may refer to other companies with similar or identical names, potentially leading to conflicting information.\n
Your objective is to choose the documents that pertain to the correct company and provide the most consistent and synchronized information, using the following keywords provided by the user to help identify the correct company: {state['company_keywords']}."""

    # Add exclusion words if provided
    if state['exclude_keywords']:
        prompt += f"""\nAdditionally, filter out documents containing any form of these exclusion words: {state['exclude_keywords']}."""
    
    # Add document list
    prompt += f"""\nHere is the list of documents gathered for your review:\n{state['documents']}\n"""
    
    # Initialize model with structured output - with correct message handling
    model = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash", 
        temperature=0.2,
        max_output_tokens=3500
    ).with_structured_output(TavilyExtractInput)
    
    # Use HumanMessage instead of SystemMessage
    message = HumanMessage(content=prompt)
    
    try:
        structured_output = await model.ainvoke([message])
        relevant_urls = structured_output.urls
        
        # Filter documents
        RAG_docs = {url: state['documents'][url] for url in relevant_urls if url in state['documents']}
        
        # Add debug message
        msg = f"Curating Documents ...\nSelected {len(RAG_docs)} relevant documents.\n"
        
        try:
            # Extract content from URLs - Improve URL validation handling
            if relevant_urls:
                valid_urls = [url for url in relevant_urls if url.startswith('http')]
                if valid_urls:
                    response = await tavily_client.extract(urls=valid_urls)
                    msg += "Extracted raw content for:\n"
                    
                    # Process extraction results
                    for item in response['results']:
                        url = item['url']
                        msg += f"{url}\n" 
                        if url in RAG_docs:
                            RAG_docs[url]['raw_content'] = item['raw_content']
                else:
                    msg += "No valid URLs found for extraction.\n"
            else:
                msg += "No URLs selected for extraction.\n"
        
            # Return updated state
            return {
                "messages": [AIMessage(content=msg)],
                "RAG_docs": RAG_docs
            }
        except Exception as e:
            st.error(f"Error in extraction: {str(e)}")
            return {"messages": [AIMessage(content=f"Error curating documents: {str(e)}")]}
    except Exception as e:
        st.error(f"Error in select_and_process: {str(e)}")
        return {"messages": [AIMessage(content=f"Error curating documents: {str(e)}")]}

# Node: Write Report – generate the markdown report
async def write_report(state: ResearchState):
    """
    Generate a comprehensive markdown report based on curated documents.
    
    This node uses the Gemini model to generate a detailed, well-formatted report
    about the company of interest, based on the curated documents. The report includes
    citations and references to the source documents.
    
    Args:
        state (ResearchState): The current state of the research workflow, including
                              curated documents (RAG_docs)
        
    Returns:
        dict: Updated state with the generated report and confirmation message
        
    Note:
        Uses structured output format (QuotedAnswer) to ensure proper citations
        Includes error handling with Streamlit feedback for debugging purposes
    """
    # Log state information for debugging
    st.info(f"Starting report generation for {state['company']}")
    st.info(f"Number of RAG docs: {len(state.get('RAG_docs', {}))}")
    
    # Create a prompt
    prompt = f"""Today's date is {datetime.now().strftime('%d/%m/%Y')}.\n
You are an expert researcher, writing a weekly report about recent events in portfolio companies.\n
Your task is to write an in-depth, well-written, and detailed report on the following company: {state['company']} in markdown syntax.\n
Here are all the documents you should base your answer on:\n{state['RAG_docs']}\n"""

    # Initialize model with structured output
    model = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0,
        max_output_tokens=5000
    ).with_structured_output(QuotedAnswer)
    
    # Use HumanMessage instead of SystemMessage
    messages = [HumanMessage(content=prompt)]
    
    try:
        response = await model.ainvoke(messages)
        # Format the full report with citations
        full_report = response.answer
        
        # Add Citations Section
        full_report += "\n\n### Citations\n"
        for citation in response.citations:
            doc = state['RAG_docs'].get(citation.source_id, {})
            full_report += f"- [{doc.get('title', citation.source_id)}]({citation.source_id}): \"{citation.quote}\"\n"
        
        # Log report length for debugging
        st.success(f"Report generated - {len(full_report)} characters")
        
        # Return the report
        return {
            "messages": [AIMessage(content=f"Generated Report:\n{full_report}")], 
            "report": full_report
        }
    except Exception as e:
        st.error(f"Error in write_report: {str(e)}")
        return {"messages": [AIMessage(content=f"Error generating report: {str(e)}")]}

# Node: Publish – generate PDF from the report
def generate_pdf(state: ResearchState):
    """
    Convert the markdown report to PDF and save it to the file system.
    
    This node takes the generated markdown report and converts it to a
    PDF document, saving it in the 'reports' directory with a filename
    based on the company name and current timestamp.
    
    Args:
        state (ResearchState): The current state of the research workflow,
                              including the generated report
        
    Returns:
        dict: Updated state with PDF generation status message
        
    Note:
        Creates the reports directory if it doesn't exist
        Sanitizes company name to ensure valid filename
        Includes error handling with Streamlit feedback for debugging purposes
    """
    # Create directory if it doesn't exist
    directory = "reports"
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    # Generate filename with timestamp - Fix invalid characters in filename
    safe_company_name = "".join([c for c in state['company'] if c.isalnum() or c.isspace()]).strip()
    file_name = f"{safe_company_name} Weekly Report {datetime.now().strftime('%Y-%m-%d %H-%M-%S')}"
    
    # Use a more detailed path for debugging
    full_path = os.path.join(directory, f"{file_name}.pdf")
    st.info(f"Generating PDF at: {full_path}")
    
    # Check if report exists in state
    if not state.get('report'):
        st.error("No report content found in state")
        return {"messages": [AIMessage(content="Error: No report content to generate PDF")]}
    
    # Generate PDF with better error handling
    try:
        report_length = len(state['report'])
        st.info(f"Converting markdown content ({report_length} chars) to PDF...")
        
        msg = generate_pdf_from_md(state['report'], filename=full_path)
        
        if os.path.exists(full_path):
            file_size = os.path.getsize(full_path)
            st.success(f"PDF generated successfully: {full_path} ({file_size} bytes)")
            return {"messages": [AIMessage(content=msg)]}
        else:
            st.error(f"PDF file was not created at {full_path}")
            return {"messages": [AIMessage(content="PDF generation failed: output file not found")]}
            
    except Exception as e:
        error_msg = f"Error generating PDF: {str(e)}"
        st.error(error_msg)
        return {"messages": [AIMessage(content=error_msg)]}