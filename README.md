# AI-Agent-Based Deep Research 
[Live Demo](https://ai-agent-based-deep-research.streamlit.app/)

A sophisticated AI-powered research automation system that performs comprehensive company research, generates structured reports, and delivers polished PDF documents with minimal human input.

## Overview

This project leverages Large Language Models and specialized AI agents to automate the process of gathering, analyzing, and synthesizing business intelligence. The system follows a structured workflow to transform a simple company name and keywords into a comprehensive, professionally formatted research report.

## Key Features

-   **Automated Research Gathering**: Conducts parallel web searches across multiple queries to gather comprehensive company information
-   **Intelligent Document Curation**: Filters and prioritizes the most relevant documents for report generation
-   **Structured Report Generation**: Creates well-organized reports with standardized sections
-   **Citation Management**: Automatically includes citations with quoted text and source URLs
-   **PDF Export**: Converts markdown reports to properly formatted PDF documents
-   **Rate Limiting**: Implements token bucket algorithm to manage API usage efficiently
## Architecture

The system is built using a modular architecture based on LangGraph's StateGraph framework:
```
            ┌─────────┐
            │         │
            ▼         │
┌─────────┐     ┌─────┴───┐
│ research ├─────► tools  │
└────┬────┘     └─────────┘
     │
     ▼
┌─────────┐     ┌─────────┐     ┌─────────┐
│ curate  ├─────► write   ├─────► publish ├─────► END
└─────────┘     └─────────┘     └─────────┘
```
### Core Components

1.  **Research Node**: Coordinates the research process using the Groq LLM API
2.  **Tools Node**: Executes web searches using the Tavily API
3.  **Curate Node**: Filters and processes collected documents
4.  **Write Node**: Generates structured markdown reports with citations
5.  **Publish Node**: Converts markdown to PDF format

## Report Structure

Each generated report follows a standardized format:

1.  Executive Summary
2.  Company Background
3.  Financial Overview
4.  Market & Competitive Landscape
5.  Recent News & Developments
6.  Future Outlook & Recommendations
7.  References
## Installation

1.  Clone the repository
```
git clone https://github.com/Jatin-Mehra119/AI-agent-based-Deep-Research.git
cd AI-agent-based-Deep-Research
```
2.  Install dependencies
```
pip install -r requirements.txt
```
3.  Set up environment variables
```
export TAVILY_API_KEY=your_tavily_api_key
export GROQ_API_KEY=your_groq_api_key
```
## Project Structure
```
AI-agent-based-Deep-Research/
├── modules/                # Implementation files
│   ├── models.py           # Data structures and type definitions
│   ├── pdf_utils.py        # PDF generation utilities
│   ├── rate_limiter.py     # API rate limiting
│   ├── tools.py            # External service integrations
│   ├── workflow_nodes.py   # Individual workflow components
│   └── workflow_setup.py   # Workflow graph definition
│
├── Docs/                   # Module documentation
│   ├── models.md
│   ├── pdf_utils.md
│   ├── rate_limiter.md
│   ├── tools.md
│   ├── workflow_nodes.md
│   └── workflow_setup.md
│
├── reports/                # Generated PDF reports
└── README.md
```

## Dependencies

-   **LangChain/LangGraph**: For workflow orchestration
-   **Google Gemini 1.5 Pro API**: For AI model interactions
-   **Tavily API**: For web search capabilities
-   **FPDF**: For PDF generation from markdown
-   **Streamlit**: For error display and potential UI
-   **Asyncio**: For concurrent operations


## License
MIT


# Report
## Deep Research AI Agentic System for Online Information Gathering

### 1. Executive Summary

This project presents a Deep Research AI Agentic System designed to crawl websites for online information using the Tavily API. The system implements a dual-agent architecture where one agent focuses on data collection and research, while the second agent synthesizes the gathered data into a professional report. The workflow is orchestrated using the LangGraph framework, and communication is managed through LangChain, ensuring an efficient and scalable research process.

### 2. Introduction

In today's fast-paced digital landscape, automated research systems are invaluable for gathering and processing information from a multitude of online sources. This project meets an assignment challenge by designing an agentic system that not only collects data via web crawling (leveraging Tavily) but also drafts comprehensive reports using language models. The dual-agent system divides responsibilities between:

-   **Data Collection & Curation:** Responsible for searching, crawling, and curating relevant online content.
-   **Answer Drafting:** Focused on synthesizing curated data into a structured, readable report.

### 3. System Architecture

The system is structured into a set of modular components that are organized into clearly defined folders and files. Key components include:

-   **Modules:**
    
    -   **Models:** Defines data structures (state, citations, structured outputs) using Pydantic and TypedDict.
    -   **Rate Limiter:** Implements a token bucket mechanism to control API usage and ensure compliance with rate limits.
    -   **Tools:** Contains tool definitions (such as the Tavily search tool) to interact with online APIs.
    -   **Workflow Nodes:** Implements individual nodes (research, tool execution, data curation, answer drafting, and PDF publication) for the research workflow.
    -   **PDF Utilities:** Provides helper functions for converting markdown reports into PDF format.
-   **Workflow Orchestration:**  
    The LangGraph framework is used to define a state-driven workflow. Nodes are linked with conditional transitions (for example, looping through research iterations until enough data is gathered), and the workflow is compiled into an executable Streamlit app.
    
-   **User Interface:**  
    The app is built with Streamlit, offering an intuitive web interface for users to enter research parameters and download generated PDF reports.
    

### 4. Detailed Workflow

#### Step 1: Research Initiation

-   The user inputs the company name, keywords, and any additional guidelines via the Streamlit UI.
-   The system creates an initial state and a research prompt that is passed to the research agent.
-   The research agent uses a language model to identify potential search queries and may trigger tool calls.

#### Step 2: Data Collection

-   The tool node intercepts search requests and invokes the Tavily search tool.
-   Multiple search queries are executed in parallel, and results are aggregated to remove duplicates.
-   Newly discovered documents are appended to the research state.

#### Step 3: Iterative Refinement

-   The system iterates between research and tool nodes (up to three iterations) to refine and enhance data collection.
-   A decision function determines whether to continue gathering data or move to the curation phase.

#### Step 4: Data Curation

-   Once data collection is complete, the curated agent analyzes the collected documents.
-   The agent filters relevant URLs and calls an extraction function to obtain raw content.
-   The curated documents (RAG_docs) now form a robust knowledge base for drafting.

#### Step 5: Answer Drafting

-   A detailed prompt is sent to a drafting agent that compiles the curated data into a markdown report.
-   The report includes sections such as the executive summary, company background, financial overview, competitive landscape, and recommendations.
-   Citations are dynamically appended based on the sources of curated documents.

#### Step 6: Report Publication

-   The final markdown report is transformed into a PDF using a PDF generation module.
-   The PDF is saved and made available for download through the Streamlit interface.

### 5. Implementation Details

-   **Frameworks & Libraries:**
    
    -   **LangChain & LangGraph:** Manage model interactions and state-based workflow execution.
    -   **Google Gemini 1.5 Pro API:** Provides advanced language modeling capabilities for research and report generation.
    -   **Tavily API:** Provides robust search and extraction capabilities for online information.
    -   **Streamlit:** Offers a user-friendly interface for running and interacting with the research system.
    -   **FPDF:** Used for converting markdown content into downloadable PDF reports.
    -   **Python & Pydantic:** Ensure strong type definitions and modular code organization.
-   **Rate Limiting:**  
    A token bucket mechanism ensures that API calls to the language model are properly rate-limited, thereby avoiding overuse and maintaining responsiveness.
    
-   **Modular Design:**  
    The codebase is organized into separate modules for models, tools, workflow nodes, and utilities. This modularity promotes ease of maintenance, scalability, and the potential for future enhancements.
    

### 6. Conclusion

The Deep Research AI Agentic System successfully demonstrates a dual-agent approach to automated research and report generation. By combining online crawling capabilities with advanced language model synthesis, the system efficiently gathers, curates, and presents data in a structured report format. The integration of LangGraph and LangChain frameworks underlines the system’s modular design and scalability, making it a robust solution for deep research tasks.

### 7. Future Enhancements

-   **Expand Data Sources:** Incorporate additional web APIs and data sources to broaden the scope of research.
-   **Advanced Curation:** Improve the curation phase with more sophisticated natural language processing techniques.
-   **User Customization:** Enhance the UI to allow for more customizable report formats and analysis options.
-   **Error Handling:** Refine error management and logging to better handle exceptions during long-running research sessions.
