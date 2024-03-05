import os
from openai import OpenAI

os.environ['OPENAI_API_KEY'] = "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"

client = OpenAI()

response = client.chat.completions.create(
  model="gpt-4-vision-preview",
  messages=[
    {
      "role": "user",
      "content": [
        {"type": "text", "text": """Give a 0-10 value for this outfit based on the situation, if it's perfect for the situation, it's a 10, if it doesn't fit the situation at all, it's a 0.

Situation: going to the beach:
"""},
        {
          "type": "image_url",
          "image_url": {
            "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
          },
        },
      ],
    }
  ],
  max_tokens=300,
)

print(response.choices)
print()
print(response.choices[0])
