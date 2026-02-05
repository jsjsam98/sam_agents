# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based repository for experimenting with LlamaIndex workflows and AI agents. The project focuses on building event-driven agentic workflows using LlamaIndex's workflow system.

## Core Architecture

### Simple Agents (Direct OpenAI Responses API)

The `beginner/simple_agent/` directory contains examples using OpenAI's Responses API directly without LlamaIndex workflows. This API is designed for conversational interactions with built-in context management.

**Key Features:**
- Uses `client.responses.create()` instead of `client.chat.completions.create()`
- Input accepts array of message items: `[{"role": "user", "content": "..."}]`
- Output is an array containing `ResponseReasoningItem` and `ResponseOutputMessage` objects
- Supports reasoning steps (visible via `ResponseReasoningItem` when enabled)

**Multi-turn Conversation Patterns:**

1. **Manual Context Management** (openai_response_multi_turn.py):
   ```python
   context = [{"role": "user", "content": "What is the capital of France?"}]
   res1 = client.responses.create(model="gpt-5", input=context)

   # Append entire output (includes reasoning + messages)
   context += res1.output

   # Add next user message
   context += [{"role": "user", "content": "And its population?"}]
   res2 = client.responses.create(model="gpt-5", input=context)
   ```
   - Context is a mixed array: user messages (dicts) + response objects
   - Preserves full conversation history including model reasoning

2. **Stateful Conversation** (openai_response_conv.py):
   ```python
   res1 = client.responses.create(
       model="gpt-5",
       input="What is the capital of France?",
       store=True
   )

   res2 = client.responses.create(
       model="gpt-5",
       input="And its population?",
       previous_response_id=res1.id,
       store=True
   )
   ```
   - Uses `store=True` to persist responses server-side
   - Links conversations via `previous_response_id`
   - Server handles context management automatically

**Response Structure:**
```python
response.output = [
    ResponseReasoningItem(type='reasoning', content=None, encrypted_content=None),
    ResponseOutputMessage(role='assistant', content=[...])
]
```

**Best Practices:**
- **Simple input**: Can pass a string directly: `input="Hello!"`
- **Structured input**: Use `instructions` + `input` to separate system prompt from user input
- **Accessing output**: Use helper `response.output_text` for quick access to text
- **Stateless with reasoning**: Set `store=False` and include `["reasoning.encrypted_content"]` for ZDR compliance
- **Native tools**: Use built-in tools like `tools=[{"type": "web_search"}]` instead of custom implementations
- **Structured outputs**: Use `text.format` with JSON schema for typed responses
- **Function strictness**: Functions are strict by default in Responses API (vs non-strict in Chat Completions)

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

## OpenAI API Guidelines

**Important:** Always use the **Responses API** for new projects. Chat Completions API remains supported but Responses is recommended. See [docs/openai_rule.md](docs/openai_rule.md) for complete migration guide.

### Available OpenAI Models

When using OpenAI APIs (either directly or through LlamaIndex), the following models are available:

- **gpt-5.2** - Latest GPT-5 model with enhanced capabilities
- **gpt-5** - Standard GPT-5 model
- **gpt-5-mini** - Smaller, faster GPT-5 variant
- **gpt-5-nano** - Most efficient GPT-5 model for simple tasks

### Responses API vs Chat Completions API

**Why use Responses API:**
- 3% better performance on benchmarks (e.g., SWE-bench)
- Built-in tools: web search, file search, code interpreter, computer use, MCP servers
- 40-80% better cache utilization = lower costs
- Agentic loop by default (multi-tool calls in single request)
- Stateful context with `store: true` and `previous_response_id`
- Encrypted reasoning support for Zero Data Retention (ZDR) requirements

**Key API Differences:**

| Feature | Chat Completions | Responses |
|---------|-----------------|-----------|
| Parameter | `messages` | `input` |
| System prompt | In messages array | Separate `instructions` field |
| Output | `choices[0].message.content` | `output_text` |
| Context | Messages only | Messages + reasoning items |
| Tools | Manual implementation | Native tools built-in |
| Structured output | `response_format` | `text.format` |
| Functions | `function.strict: false` default | `strict: true` default |

## Development Commands

### Running Simple Agents (Direct OpenAI API)

```bash
# Multi-turn conversation with context management
python beginner/simple_agent/openai_response_multi_turn.py

# Conversation using previous_response_id (stateful)
python beginner/simple_agent/openai_response_conv.py
```

### Running Workflows (LlamaIndex)

```bash
# Run a basic workflow
python beginner/agent/simple_workflow.py

# Run human-in-the-loop workflow
python beginner/agent/human_workflow_1.py

# Router workflow with query engine selection
python beginner/agent/router_workflow.py

# ReAct agent with tool calling
python beginner/agent/react_workflow.py

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
│   ├── simple_agent/   # Direct OpenAI Responses API examples
│   │   ├── openai_response_multi_turn.py  # Manual context management
│   │   └── openai_response_conv.py        # Stateful with previous_response_id
│   ├── agent/          # LlamaIndex workflow examples
│   │   ├── simple_workflow.py             # Basic workflow
│   │   ├── router_workflow.py             # Query engine router
│   │   ├── react_workflow.py              # ReAct agent with tools
│   │   ├── human_workflow_1.py            # Human-in-the-loop
│   │   ├── output/                        # Generated visualizations
│   │   └── data/                          # Sample data for RAG
│   └── speed_test/     # Performance benchmarking
├── docs/               # Project documentation
│   └── openai_rule.md  # OpenAI Responses API migration guide
├── lib/                # JavaScript libraries for visualization
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

**LlamaIndex Workflows:**
```python
class MyWorkflow(Workflow):
    llm = OpenAI(model="gpt-5", temperature=0)
```

**Direct OpenAI API:**
```python
from openai import OpenAI
client = OpenAI()
response = client.responses.create(model="gpt-5", input=[...])
```

**Model Selection:**
- Use `gpt-5.2` for most advanced capabilities
- Use `gpt-5` for standard tasks
- Use `gpt-5-mini` for faster, cost-effective processing
- Use `gpt-5-nano` for simple, high-throughput tasks

For reasoning models, the Responses API automatically includes `ResponseReasoningItem` in output when the model uses internal reasoning.

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
