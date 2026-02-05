from workflows import Workflow, step
from workflows.events import (
    StartEvent,
    StopEvent,
    InputRequiredEvent,
    HumanResponseEvent,
)


class HumanInTheLoopWorkflow(Workflow):
    @step
    async def step1(self, ev: StartEvent) -> InputRequiredEvent:
        return InputRequiredEvent(prefix="Enter a number: ")

    @step
    async def step2(self, ev: HumanResponseEvent) -> StopEvent:
        return StopEvent(result=ev.response)


async def main():
    workflow = HumanInTheLoopWorkflow()

    handler = workflow.run()
    async for event in handler.stream_events():
        if isinstance(event, InputRequiredEvent):
            # here, we can handle human input however you want
            # this means using input(), websockets, accessing async state, etc.
            # here, we just use input()
            response = input(event.prefix)
            handler.ctx.send_event(HumanResponseEvent(response=response))

    final_result = await handler
    print(final_result)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
