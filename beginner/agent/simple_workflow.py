from workflows import Workflow, step
from workflows.events import (
    Event,
    StartEvent,
    StopEvent,
)
from llama_index.llms.openai import OpenAI

from llama_index.core import set_global_handler

# Enable Phoenix tracing - will connect to Phoenix at localhost:6006
set_global_handler("arize_phoenix")
print("Connected to Phoenix at http://localhost:6006")


class JokeEvent(Event):
    joke: str


class JokeFlow(Workflow):
    llm = OpenAI(model="gpt-5.2", temperature=0, reasoning_effort="none")

    @step
    async def generate_joke(self, ev: StartEvent) -> JokeEvent:
        topic = ev.topic

        prompt = f"Write your best joke about {topic}."
        response = await self.llm.acomplete(prompt)
        return JokeEvent(joke=str(response))

    @step
    async def critique_joke(self, ev: JokeEvent) -> StopEvent:
        joke = ev.joke

        prompt = f"Give a thorough analysis and critique of the following joke: {joke}"
        response = await self.llm.acomplete(prompt)
        return StopEvent(result=str(response))


async def main():
    w = JokeFlow(timeout=60, verbose=False)
    result = await w.run(topic="pirates")
    print(str(result))


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
