from openai import OpenAI

client = OpenAI()

res1 = client.responses.create(
    model="gpt-5", input="What is the capital of France?", store=True
)

res2 = client.responses.create(
    model="gpt-5", input="And its population?", previous_response_id=res1.id, store=True
)

print(res2)
