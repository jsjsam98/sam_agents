import asyncio
import time
from llama_index.llms.openai import OpenAI as LlamaIndexOpenAI
from openai import OpenAI


async def main():
    models = ["gpt-5.2", "gpt-5-mini", "gpt-5-nano"]
    prompt = "hi"

    print("LlamaIndex OpenAI:")
    for model in models:
        llm = LlamaIndexOpenAI(model=model)
        start = time.time()
        await llm.acomplete(prompt)
        elapsed = time.time() - start
        print(f"  {model}: {elapsed:.3f}s")

    print("\nOpenAI API directly:")
    client = OpenAI()
    for model in models:
        start = time.time()
        client.responses.create(
            model=model,
            input=prompt,
            service_tier="priority",
        )
        elapsed = time.time() - start
        print(f"  {model}: {elapsed:.3f}s")


if __name__ == "__main__":
    asyncio.run(main())
