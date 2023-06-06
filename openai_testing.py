import openai
import os

# openai.api_key = "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"
openai.api_key = "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"

goalTest="get better at english"

def generate_prompt(goal):
    prompt = "Generate objectives to complete this goal: "+goal
    return prompt

models = openai.Model.list()

response = openai.ChatCompletion.create(model="gpt-3.5-turbo", prompt=generate_prompt(goalTest),temperature=0.6)

print(response)