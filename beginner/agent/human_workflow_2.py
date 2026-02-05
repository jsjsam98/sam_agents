from workflows import Workflow, step
from workflows.events import (
    StartEvent,
    StopEvent,
    InputRequiredEvent,
    HumanResponseEvent,
)
from workflows import Context


class HumanInTheLoopWorkflow(Workflow):
    @step
    async def step1(self, ev: StartEvent) -> InputRequiredEvent:
        return InputRequiredEvent(question="What is your name? ")

    @step
    async def step2(self, ev: HumanResponseEvent) -> StopEvent:
        msg = "Hello, " + ev.response
        return StopEvent(result=msg)


async def main():
    workflow = HumanInTheLoopWorkflow()

    handler = workflow.run()
    async for event in handler.stream_events():
        if isinstance(event, InputRequiredEvent):
            # Serialize the context, store it anywhere as a JSON blob
            ctx_dict = handler.ctx.to_dict()
            await handler.cancel_run()
            break

    # now we handle the human response once it comes in
    response = input(event.question)

    restored_ctx = Context.from_dict(workflow, ctx_dict)
    handler = workflow.run(ctx=restored_ctx)

    # Send the event to resume the workflow
    handler.ctx.send_event(HumanResponseEvent(response=response))

    # now we resume the workflow streaming with our restored context
    async for event in handler.stream_events():
        continue

    final_result = await handler
    print(final_result)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
