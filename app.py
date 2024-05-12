import streamlit as st
import os
import time
import telebot
from groq import Groq
from pypdf import PdfReader

# Set up Telegram Bot
recipient_user_id = os.environ['RECIPIENT_USER_ID']
bot_token = os.environ['BOT_TOKEN']
bot = telebot.TeleBot(bot_token)

# Retrieve the API keys from the environment variables
MISTRAL_API_KEY = os.environ["GROQ_API_KEY"]
mistral = Groq(api_key=MISTRAL_API_KEY)

st.set_page_config(page_title="TurboChapeau", page_icon=":sunglasses:",)
st.subheader("**TurboChapeau** : pdf to para in a flash")

original_prompt = "You will be summarizing a given text. Here is the text to summarize:\n\n<text>{{TEXT}}</text>\n\nPlease follow these steps to generate a high-quality summary:\n\n1. Read the text carefully and thoroughly to ensure you fully understand its content.\n\n2. Identify the main ideas and key details presented in the text. Consider the overall purpose and message the author is trying to convey.\n\n3. Generate a concise and coherent summary that captures the essence of the text. Focus on the most important information and avoid including unnecessary details or repetition.\n\n4. Present your summary in a clear and organized way, ensuring that it flows logically from one point to the next.\n\nPlease present your output as a single paragraph."
system_prompt = st.text_area("", original_prompt)
         
uploaded_file = st.file_uploader("", type = "pdf")
raw_text = ""
if uploaded_file is not None:
  doc_reader = PdfReader(uploaded_file)
  for page in enumerate(doc_reader.pages):
    text = page.extract_text()
    if text:
      raw_text = raw_text + text + "\n"
  
  if raw_text != "":
    try:
      with st.spinner("Running AI Model..."):
        start = time.time()
        input_text = "<text>\n" + raw_text + "\n</text>"
        response = mistral.chat.completions.create(
          model="mixtral-8x7b-32768", messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": input_text},
          ],
          temperature = 0,
        )
        output_text = response.choices[0].message.content
        end = time.time()

        container = st.container(border=True)
        container.subheader(output_text)
        container.subheader("Time to generate: " + str(round(end-start,2)) + " seconds")
        bot.send_message(chat_id=recipient_user_id, text="TurboChapeau")
        st.download_button(':floppy_disk:', output_text)
    except:
      st.error(" Error occurred when running model", icon="🚨")
