import asyncio
from llama_index.core import set_global_handler
from llama_index.core.workflow import (
    Workflow,
    StartEvent,
    StopEvent,
    step,
    Event,
)
from llama_index.llms.openai import OpenAI

# Enable Phoenix tracing - will connect to Phoenix at localhost:6006
set_global_handler("arize_phoenix")
print("Connected to Phoenix at http://localhost:6006")


# Simulated functions to test
def calculate_discount(price: float, discount_percent: float) -> float:
    """Calculate the final price after applying a discount"""
    print(f"  [Function] calculate_discount({price}, {discount_percent}%)")
    discount_amount = price * (discount_percent / 100)
    final_price = price - discount_amount
    return final_price


def calculate_tax(amount: float, tax_rate: float) -> float:
    """Calculate the total amount including tax"""
    print(f"  [Function] calculate_tax({amount}, {tax_rate}%)")
    tax_amount = amount * (tax_rate / 100)
    total = amount + tax_amount
    return total


# Define custom events for our workflow
class ParseEvent(Event):
    """Event triggered when we need to parse the user input"""
    query: str


class CalculateEvent(Event):
    """Event triggered when we need to perform calculation"""
    num1: float
    num2: float
    function_name: str  # Which function to call: 'discount' or 'tax'


class FormatEvent(Event):
    """Event triggered when we need to format the response"""
    result: float
    original_query: str


# Custom workflow
class CalculatorWorkflow(Workflow):
    """A custom workflow that parses, calculates, and formats responses"""

    def __init__(self, llm: OpenAI):
        super().__init__()
        self.llm = llm

    @step
    async def parse_input(self, ev: StartEvent) -> ParseEvent:
        """Step 1: Receive user input and emit parse event"""
        print(f"\n[Step 1] Parsing input: {ev.query}")
        return ParseEvent(query=ev.query)

    @step
    async def extract_numbers(self, ev: ParseEvent) -> CalculateEvent:
        """Step 2: Use LLM to extract numbers and determine which function to call"""
        print(f"[Step 2] Extracting numbers from: {ev.query}")

        prompt = f"""Extract the two numbers and determine which function to call from this query.
Query: {ev.query}

Available functions:
- discount: Calculate price after discount (price, discount_percent)
- tax: Calculate total with tax (amount, tax_rate)

Respond in this exact format:
NUMBER1: <first number>
NUMBER2: <second number>
FUNCTION: <discount or tax>
"""
        response = await self.llm.acomplete(prompt)
        result = str(response)

        # Parse the LLM response
        lines = result.strip().split('\n')
        num1 = float(lines[0].split(':')[1].strip())
        num2 = float(lines[1].split(':')[1].strip())
        function_name = lines[2].split(':')[1].strip().lower()

        print(f"  → Extracted: {num1}, {num2} → function: {function_name}")

        return CalculateEvent(num1=num1, num2=num2, function_name=function_name)

    @step
    async def perform_calculation(self, ev: CalculateEvent) -> FormatEvent:
        """Step 3: Call the appropriate function"""
        print(f"[Step 3] Calling function: {ev.function_name} with ({ev.num1}, {ev.num2})")

        if ev.function_name == "discount":
            result = calculate_discount(ev.num1, ev.num2)
            original_query = f"${ev.num1} with {ev.num2}% discount"
        elif ev.function_name == "tax":
            result = calculate_tax(ev.num1, ev.num2)
            original_query = f"${ev.num1} with {ev.num2}% tax"
        else:
            result = 0
            original_query = f"unknown function: {ev.function_name}"

        print(f"  → Result: ${result:.2f}")

        return FormatEvent(
            result=result,
            original_query=original_query
        )

    @step
    async def format_response(self, ev: FormatEvent) -> StopEvent:
        """Step 4: Use LLM to format a friendly response"""
        print(f"[Step 4] Formatting response")

        prompt = f"""Create a friendly response for this calculation:
Question: {ev.original_query}
Answer: {ev.result}

Make it conversational and natural."""

        response = await self.llm.acomplete(prompt)
        final_response = str(response)

        print(f"  → Final response ready")

        return StopEvent(result=final_response)


async def main():
    # Create our custom workflow
    llm = OpenAI(model="gpt-4o-mini")
    workflow = CalculatorWorkflow(llm=llm)

    # Test cases for both functions
    test_queries = [
        "What is the price of a $100 item with a 20% discount?",
        "If I buy something for $85.50 and the tax is 8.5%, what's the total?",
    ]

    for i, query in enumerate(test_queries, 1):
        print("\n" + "="*60)
        print(f"TEST {i}: {query}")
        print("="*60)

        # Run the workflow
        result = await workflow.run(query=query)

        print("\n" + "-"*60)
        print("FINAL ANSWER:")
        print("-"*60)
        print(result)
        print()


# Run the workflow
if __name__ == "__main__":
    asyncio.run(main())