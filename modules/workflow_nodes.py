import os
import re
import asyncio
import time
from datetime import datetime
import streamlit as st

from langchain_core.messages import AIMessage, SystemMessage, ToolMessage
from langchain_groq import ChatGroq
from modules.models import ResearchState, TavilyExtractInput, QuotedAnswer
from modules.rate_limiter import rate_limited_execute
from modules.pdf_utils import generate_pdf_from_md
from modules.tools import tools_by_name, tavily_client

# Node: Tool Node – execute tools (e.g. search)
async def tool_node(state: ResearchState):
    docs = state.get('documents', {})
    msgs = []
    
    # Process each tool call in the latest message
    for tool_call in state["messages"][-1].tool_calls:
        if tool_call["name"] == "tavily_search":
            tool = tools_by_name["tavily_search"]
            results = await tool.ainvoke(tool_call["args"])
            
            new_docs = 0
            for doc in results:
                if doc['url'] not in docs:
                    docs[doc['url']] = {
                        'content': doc.get('content', ''),
                        'title': doc.get('title', 'Untitled'),
                        'score': doc.get('score', 0.0)
                    }
                    new_docs += 1
                    
            msgs.append(ToolMessage(
                content=f"Added {new_docs} new documents",
                tool_call_id=tool_call["id"]
            ))
    
    return {
        "messages": msgs, 
        "documents": docs,
        "iteration": state.get('iteration', 0) + 1  # Increment iteration count
    }

# Node: Research Model – perform research using ChatGroq
async def research_model(state: ResearchState):
    prompt = f"""Today: {datetime.now().strftime('%d/%m/%Y')}
Research target: {state['company']}
Keywords: {state['company_keywords']}"""
    
    messages = state['messages'] + [SystemMessage(content=prompt)]
    
    model = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0,
        max_tokens=4500,
        timeout=30
    ).bind_tools(list(tools_by_name.values()))
    
    response = await rate_limited_execute(model.ainvoke, messages)
    return {"messages": [response]}

# Conditional edge decision function
def should_continue(state: ResearchState) -> str:
    last_msg = state['messages'][-1]
    if state.get('iteration', 0) >= 3:  # Stop after 3 iterations
        return "curate"
    return "tools" if last_msg.tool_calls else "curate"

# Node: Curate – analyze and select relevant documents
async def select_and_process(state: ResearchState):
    prompt = f"""Analyze documents for: {state['company']}
Keywords: {state['company_keywords']}
Exclusions: {state['exclude_keywords']}"""
    
    model = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0,
        max_tokens=3500
    ).with_structured_output(TavilyExtractInput)
    
    structured_output = await rate_limited_execute(model.ainvoke, [SystemMessage(content=prompt)])
    relevant_urls = structured_output.urls
    RAG_docs = {url: state['documents'][url] for url in relevant_urls if url in state['documents']}
    
    try:
        extracted = await tavily_client.extract(urls=relevant_urls)
        for item in extracted['results']:
            if item['url'] in RAG_docs:
                RAG_docs[item['url']]['raw_content'] = item['raw_content']
    except Exception as e:
        st.error(f"Extraction error: {e}")
    
    return {"messages": [AIMessage(content="Documents curated successfully")], "RAG_docs": RAG_docs}

# Node: Write Report – generate the markdown report
async def write_report(state: ResearchState):
    try:
        prompt = f"""Create markdown report for {state['company']}
Sources: {state['RAG_docs']}
## Report Format:
### 1. Executive Summary
- Brief overview of the company
- Key findings from the research

### 2. Company Background
- Founding year, headquarters, and key executives
- Industry and market position

### 3. Financial Overview
- Revenue, profit, and other financial highlights (if available)
- Recent financial trends

### 4. Market & Competitive Landscape
- Key competitors and market positioning
- SWOT Analysis (Strengths, Weaknesses, Opportunities, Threats)

### 5. Recent News & Developments
- Major events, partnerships, acquisitions, or controversies

### 6. Future Outlook & Recommendations
- Predictions based on available data
- Strategic recommendations for growth or risk mitigation

### 7. References
- List of sources used

Generate the report in a structured and professional markdown format.
"""
        model = ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0,
            max_tokens=5000
        ).with_structured_output(QuotedAnswer)  # Specify the schema here
    
        response = await rate_limited_execute(model.ainvoke, [SystemMessage(content=prompt)])
        full_report = response.answer
        
        if not full_report.strip():
            full_report = f"## {state['company']} Weekly Report\nNo significant updates found this week."
            
        if response.citations:
            full_report += "\n\n### Sources\n"
            seen_urls = set()
            for citation in response.citations:
                url = citation.source_id
                if url in state['RAG_docs'] and url not in seen_urls:
                    title = state['RAG_docs'][url].get('title', url)
                    full_report += f"- [{title}]({url})\n"
                    seen_urls.add(url)
        
        return {"messages": [AIMessage(content="Report generated")], "report": full_report}
    
    except Exception as e:
        return {"messages": [AIMessage(content=f"Report error: {str(e)}")],
                "report": f"# Report Generation Failed\nError: {str(e)}"}

# Node: Publish – generate PDF from the report
def generate_pdf(state: ResearchState):
    directory = "reports" 
    filename = f"{directory}/{state['company']} Report {datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pdf"
    os.makedirs(directory, exist_ok=True)
    result = generate_pdf_from_md(state['report'], filename)
    return {"messages": [AIMessage(result)]}
