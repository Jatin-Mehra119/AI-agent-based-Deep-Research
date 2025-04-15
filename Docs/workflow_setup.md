# Workflow Setup Module Documentation

The  workflow_setup.py module defines and configures the research workflow as a directed graph using LangGraph's StateGraph framework. This module connects the various workflow nodes into a cohesive execution pipeline.

## Graph Structure

The module creates a directed graph that represents the research workflow:

-   **Graph Type**: StateGraph with  `ResearchState`  as the state type
-   **Entry Point**: "research" node
-   **Terminal Point**: END (built-in LangGraph termination node)

## Nodes

The workflow consists of five primary nodes, each handling a different phase of the research process:

1.  **"research"**: Implements  `research_model`  to gather information
2.  **"tools"**: Implements  `tool_node`  to execute tool calls (e.g., web searches)
3.  **"curate"**: Implements  `select_and_process`  to filter and refine documents
4.  **"write"**: Implements  `write_report`  to generate the markdown report
5.  **"publish"**: Implements  `generate_pdf`  to create the final PDF document

## Edges and Flow Control

The module defines the following transitions between nodes:

-   **Conditional Edge**: From "research" to either "tools" or "curate" based on the  `should_continue`  function:
    -   If tool calls are present → "tools"
    -   If iteration limit reached → "curate"
-   **Standard Edges**:
    -   "tools" → "research" (creates a research-tools loop for information gathering)
    -   "curate" → "write" (after document curation, proceed to report generation)
    -   "write" → "publish" (after report creation, proceed to PDF generation)
    -   "publish" → END (workflow completion)

## Compiled Application

The module compiles the workflow into an executable application:

-   **app**: The compiled workflow that can be invoked to execute the research process

## Dependencies

-   **langgraph.graph**: For StateGraph and END constructs
-   **modules.models**: For the ResearchState data structure
-   **modules.workflow_nodes**: For all workflow node implementations

## Workflow Diagram
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