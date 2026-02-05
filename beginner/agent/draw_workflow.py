"""
Draw the CalculatorWorkflow diagram using LlamaIndex's built-in visualization.
"""

from pathlib import Path
from llama_index.utils.workflow import draw_all_possible_flows
from simple_workflow import JokeFlow
from concurrent_workflow import ConcurrentFlow
from react_workflow import ReActAgent

def main():
    """Generate workflow diagram without running it"""

    # Create output directory
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / "workflow_diagram.html"

    # Draw all possible flows (static diagram showing workflow structure)
    draw_all_possible_flows(ReActAgent, filename=str(output_file))


if __name__ == "__main__":
    main()
