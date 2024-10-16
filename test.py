import azure.cognitiveservices.speech as speechsdk
import pyodbc
from tkinter import *
from tkinter import scrolledtext
from openai import AzureOpenAI
from sqlalchemy import true
from prettytable import PrettyTable

# Set up Azure Cognitive Services Speech SDK
subscription_key = "cdfbdf50ae44415ea6b152f0ccfdd1d6"
region = "eastus"
config = speechsdk.SpeechConfig(subscription=subscription_key, region=region)

# Set up Azure OpenAI Services ChatGPT
client = AzureOpenAI(
    api_key="5471262c1d224ca496238d489c335028",
    api_version="2024-02-01",
    azure_endpoint="https://globaldbaopenaiservice.openai.azure.com/"
)

# Chat GPT model
deployment_name = 'gpt-4o'

# Function to recognize the voice and transcribe to text
def speech_to_text():
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=config)
    result = speech_recognizer.recognize_once_async().get()
    transcribed_text = result.text
    text_area.insert(INSERT, f"Transcribed Text: {transcribed_text}\n")
    return transcribed_text

# Function to generate SQL query from user input
def generate_sql_query(user_input):
    prompt = f"""Task: please Generate only latest MSSQL Query and return content without '`' symbol: 
            '{user_input}',and replace the values assigned to different forms of database names"""

    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": "which is the largest database in server"},
        {"role": "assistant",
         "content": "SELECT TOP 1 name AS DatabaseName, (size*8)/1024 AS SizeMB FROM sys.master_files GROUP BY name, size ORDER BY SizeMB DESC"},
        {"role": "user", "content": user_input}
    ]

    response = client.chat.completions.create(messages=messages, model=deployment_name)
    generated_query = response.choices[0].message.content if response else "No Response Generated"
    generated_query = generated_query.replace('\\', '\\\\')
    text_area.insert(INSERT, f"Generated Query: {generated_query}\n")
    return generated_query

def connection_to_db(sql_query):
    try:
        connection_string = (
            'DRIVER=ODBC Driver 18 for SQL Server;'
            'SERVER=98.71.140.253,1433;'
            'DATABASE=master;'
            'UID=sa_admin;'
            'PWD=AzureAI@123;'
            'TrustServerCertificate=yes'
        )
        connection = pyodbc.connect(connection_string)
        connection.autocommit = true
    except Exception as e:
        text_area.insert(INSERT, f"Oops! Master Database not available in the Server and unable to connect... {str(e)}\n")
        return

    if not sql_query:
        text_area.insert(INSERT, "Failed to generate SQL query\n")
        return

    columns, result, status = execute_query(sql_query, connection)
    text_area.insert(INSERT, f"Columns: {columns}\nResult: {result}\nStatus: {status}\n")

def execute_query(sql_query, connection):
    try:
        cursor = connection.cursor()
        cursor.execute(sql_query)
        columns = [column[0] for column in cursor.description] if cursor.description else []
        result = cursor.fetchall()
        table = PrettyTable()
        table.field_names = columns
        for row in result:
            table.add_row(row)
        text_area.insert(INSERT, f"{table}\n")
        return columns, result, "SUCCESS"
    except pyodbc.Error as e:
        text_area.insert(INSERT, f"Sorry, syntax error: {str(e)}\n")
        return None, None, f"Sorry, syntax error: {str(e)}"

def text_to_speech(result):
    audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
    config.speech_synthesis_voice_name = 'en-US-JennyNeural'
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=config, audio_config=audio_config)
    speech_synthesizer.speak_text_async(result).get()

def run_query():
    user_query = speech_to_text()
    sql_query = generate_sql_query(user_query)
    if "DROP" in sql_query.upper():
        text_to_speech("Are you sure you want to execute this query?")
        user_response = speech_to_text()
        if user_response.lower() in ['yes', 'of course', 'go ahead', 'yeah']:
            connection_to_db(sql_query)
            text_to_speech("Query executed. Do you have any other queries?")
    else:
        connection_to_db(sql_query)
        text_to_speech("Query executed. Do you have any other queries?")

# Tkinter GUI setup
app = Tk()
app.title("Database Monitoring with ChatGPT")
app.geometry("800x600")

btn_run = Button(app, text="Run Query", command=run_query)
btn_run.pack()

text_area = scrolledtext.ScrolledText(app, wrap=WORD, width=80, height=30)
text_area.pack()

app.mainloop()
