import anthropic

client = anthropic.Anthropic()

with client.messages.stream(
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}],
    model="claude-3-7-sonnet-20250219",
) as stream:
  for text in stream.text_stream:
      print(text, end="", flush=True)
