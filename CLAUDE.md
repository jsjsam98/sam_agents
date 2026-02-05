# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based repository for experimenting with LlamaIndex workflows and AI agents. The project focuses on building event-driven agentic workflows using LlamaIndex's workflow system.

## Core Architecture

### Workflow System

The codebase uses LlamaIndex's workflow engine with an event-driven architecture:

- **Workflow Base**: Custom workflows extend `Workflow` class from `llama_index.core.workflow`
- **Events**: Custom event types inherit from `Event`, with `StartEvent` and `StopEvent` marking workflow boundaries
- **Steps**: Functions decorated with `@step` that process events and emit new events
- **Async Pattern**: All workflows use Python's async/await pattern

### Event Flow Pattern

Workflows follow this general pattern:
1. Receive `StartEvent` with initial parameters
2. Emit custom events between processing steps
3. Each step processes an event and returns the next event
4. End with `StopEvent` containing final result

Example event chain: `StartEvent → ParseEvent → CalculateEvent → FormatEvent → StopEvent`

### Human-in-the-Loop

The project includes patterns for human interaction using:
- `InputRequiredEvent`: Signals when human input is needed
- `HumanResponseEvent`: Carries the human response back to workflow
- `ctx.write_event_to_stream()`: Emits events to external stream
- `ctx.wait_for_event()`: Pauses workflow until specific event received

## Development Commands

### Running Workflows

```bash
# Run a workflow directly
python beginner/agent/simple_workflow.py

# Run human-in-the-loop workflow
python beginner/agent/human_workflow.py

# Generate workflow visualization
python beginner/agent/draw_workflow.py
```

### Performance Testing

```bash
# Test model performance (LlamaIndex vs direct OpenAI API)
python beginner/speed_test/test.py
```

## Project Structure

```
sam_agents/
├── beginner/
│   ├── agent/          # Workflow examples and templates
│   │   ├── output/     # Generated visualization files
│   │   └── lib/        # Symlinked visualization libraries
│   ├── speed_test/     # Performance benchmarking scripts
│   ├── backend/        # (Empty - future development)
│   └── frontend/       # (Empty - future development)
├── lib/                # JavaScript libraries for visualization
│   ├── vis-9.1.2/      # vis-network for workflow diagrams
│   ├── tom-select/     # Select UI component
│   └── bindings/       # Utility functions for vis.js integration
└── .mcp.json          # MCP server configuration
```

## Dependencies

Required Python packages:
- `llama-index-core` - Core LlamaIndex framework
- `llama-index-llms-openai` - OpenAI LLM integration
- `llama-index-utils-workflow` - Workflow visualization utilities
- `openai` - Direct OpenAI API access
- `python-dotenv` - Environment variable management
- `arize-phoenix` - Observability and tracing

## Phoenix Tracing

Workflows are configured to use Arize Phoenix for observability:

```python
from llama_index.core import set_global_handler
set_global_handler("arize_phoenix")
```

Phoenix runs on `http://localhost:6006` and must be started separately before running workflows with tracing enabled.

## Environment Setup

Create a `.env` file in the project root with:
```
OPENAI_API_KEY=your_api_key_here
```

## Workflow Visualization

The project uses LlamaIndex's built-in visualization to generate HTML diagrams:

```python
from llama_index.utils.workflow import draw_all_possible_flows

draw_all_possible_flows(YourWorkflow, filename="output/diagram.html")
```

Diagrams are saved to the `output/` directory and use the vis-network library from `lib/`.

## Key Concepts

### LLM Configuration

Workflows instantiate LLMs at the class level:
```python
class MyWorkflow(Workflow):
    llm = OpenAI(model="gpt-4o-mini", temperature=0)
```

For OpenAI o1 models, use `reasoning_effort="none"` to disable thinking tokens.

### Context Access

Steps can access workflow context for advanced features:
```python
async def my_step(self, ev: MyEvent, ctx: Context) -> NextEvent:
    ctx.write_event_to_stream(event)  # Emit to external handlers
    response = await ctx.wait_for_event(EventType)  # Wait for specific event
```

### Workflow Execution

```python
# Create instance
workflow = MyWorkflow(timeout=60, verbose=False)

# Run and get final result
result = await workflow.run(param1="value")

# Stream events during execution
handler = workflow.run(param1="value")
async for event in handler.stream_events():
    # Process events as they occur
    pass
result = await handler
```

## MCP Servers

The project has MCP servers configured in `.mcp.json`:
- `svelte` - Svelte documentation and development
- `llama-index-docs` - LlamaIndex documentation access
