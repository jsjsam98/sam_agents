"""
Draw the CalculatorWorkflow diagram using LlamaIndex's built-in visualization.
"""

from pathlib import Path
from llama_index.utils.workflow import draw_all_possible_flows
from agent import CalculatorWorkflow


def main():
    """Generate workflow diagram without running it"""

    # Create output directory
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / "workflow_diagram.html"

    print("=" * 60)
    print("Drawing Workflow Structure")
    print("=" * 60)

    # Draw all possible flows (static diagram showing workflow structure)
    print("\nGenerating workflow diagram...")
    draw_all_possible_flows(CalculatorWorkflow, filename=str(output_file))

    print(f"[OK] Saved to: {output_file}")
    print("     This shows all possible paths through the workflow")

    print("\n" + "=" * 60)
    print("Diagram generated successfully!")
    print("=" * 60)
    print(f"\nOpen this file in your browser:")
    print(f"  {output_file.absolute()}")
    print("=" * 60)


if __name__ == "__main__":
    main()
