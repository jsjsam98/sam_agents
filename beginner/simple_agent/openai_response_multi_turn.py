from openai import OpenAI

client = OpenAI()

# response = client.responses.create(
#     model="gpt-4.1", input="Tell me a three sentence bedtime story about a unicorn."
# )

# print(response)


context = [{"role": "user", "content": "What is the capital of France?"}]
res1 = client.responses.create(
    model="gpt-5",
    input=context,
)

# Append the first response’s output to context
context += res1.output

# Add the next user message
context += [{"role": "user", "content": "And it's population?"}]

res2 = client.responses.create(
    model="gpt-5",
    input=context,
)
print(res2)
