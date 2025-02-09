# Import libraries to make the API requests and parse JSON
import json
import requests
from langdetect import detect



def call_llm(prompt, max_tokens=100):
  postData = {
      'prompt': prompt,
      'temperature': 0.01,
      # 'model': "llama3.3:70b",
      'model': "llama3:8b",
      'max_tokens': max_tokens,
      'stream': False
  }

  ollamaUrl = 'http://localhost:11434/api/generate'
  # Make the POST request
  llmResponse = requests.post(ollamaUrl, data=json.dumps(postData))
  # Parse the JSON response and extract the summary
  result = llmResponse.json()
  return result['response']

def arabic_default_message():
    return """
    يبدو أنني لم أتمكن من العثور على إجابة لسؤالك. يُرجى المحاولة بسؤال آخر.
    """


def english_default_message():
    return "“Sorry. it seems that I can't find an answer for your question. please try another question"


def is_in_arabic(question):
    return detect(question) == 'ar'


def get_default_message(question):
    if not is_in_arabic(question):
        return english_default_message()
    else:
        return arabic_default_message()