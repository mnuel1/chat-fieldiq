from openai import OpenAI
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(
  api_key=os.getenv("OPENAI_API_KEY"),
  organization=os.getenv("OPENAI_ORG_ID")
)

def normalize_date(sentence: str) -> str:  
  today = datetime.today().strftime("%Y/%m/%d")
  
  response = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[
      {
        "role": "system",
        "content": (
          f"Today’s date is {today}. "
          "Extract the descriptive date from the user's text and "
          "convert it into the format YYYY/MM/DD. "
          "If there is no date, reply with 'None'. "
          "Reply with the date only, no explanations."
        ),
      },
      {"role": "user", "content": sentence},
    ],
  )

  return response.choices[0].message.content.strip()

print(normalize_date("I have sales today"))
print(normalize_date("I will be visiting this farm on last Monday"))
print(normalize_date("I’ll be harvesting crops tomorrow"))
