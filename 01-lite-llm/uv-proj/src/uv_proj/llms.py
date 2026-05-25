from litellm import completion

GEMINI_KEY="AIzaSyC9e0oReu9G7H1ZBT-pRS6Sd31W493Bf6w"

def gemini2():
    response = completion(
        model="gemini/gemini-2.0-flash-exp",
        api_key=GEMINI_KEY,
        messages=[{ "content": "Hello, how are you?","role": "user"}]
    )

    print(response.choices[0].message.content)