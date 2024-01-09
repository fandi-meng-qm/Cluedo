import openai

openai.api_key = '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'


def get_completion(prompt, model="gpt-3.5"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0,  # Control randomness
    )
    return response.choices[0].message["content"]