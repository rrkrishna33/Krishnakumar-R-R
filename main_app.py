import azure.cognitiveservices.speech as speechsdk
import pyodbc
from flask import render_template
# noinspection PyProtectedMember
from openai import AzureOpenAI
from sqlalchemy import true, false
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


# Function recognize the voice and transcribed to text
def speech_to_text():
    # Initialize Speech Recognizer
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=config)
    # Record audio input from microphone
    #print("Speak into your microphone.")
    result = speech_recognizer.recognize_once_async().get()
    # Print and return transcribed text
    transcribed_text = result.text
    print("Transcribed Text:", transcribed_text)
    return transcribed_text


# Function Converts Natural Language to MS SQL Query with help of Azure ChatGPT 4o
def generate_sql_query(user_input, ):
    prompt = f"""Task: please Generate only latest MSSQL Query and return content without '`' symbol: 
            '{user_input}',and replace the values assigned to different forms of database names"""

    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": "which is the largest database in server"},
        {"role": "assistant",
         "content": "SELECT TOP 1 name AS DatabaseName, (size*8)/1024 AS SizeMB FROM sys.master_files GROUP BY name, size ORDER BY SizeMB DESC"},
        {"role": "user", "content": user_input}
    ]

    #response = api_parameter(messages)
    # API to communicate ChatGPT 4o to retrive results for user input
    response = client.chat.completions.create(messages=messages, model=deployment_name)

    print(response)

    if response:
        generated_query = response.choices[0].message.content
        generated_query: str = generated_query.replace('\\', '\\\\')
        #print(generated_query[generated_query.find(":") + 1:])
        return (generated_query)

    else:
        print("No Response genertaed")
        return ("No Response Generated")


def connection_to_db(sql_query):
    try:
        #connection_string = f"Driver=ODBC Driver 18 for SQL Server;Server=tcp:globaldba-sqlserver.database.windows.net,1433;Database=master;Uid=GlobalDBA;Pwd=DBAGlobal_1;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
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
    except:
        print(f"Oops! Master Database not available in the Server and unable to connect...")
        return
    if not sql_query:
        print("Failed to generate sql query")

    print('connecting to database')
    columns, result, status = execute_query(sql_query, connection)
    print("Columns :", columns)
    print("result :", result)
    print("Status :", status)
    """if columns and result is not None and status == 'SUCCESS':
        formatted_result = [{'ID': idx, **{columns[i]: str(value) for i, value in enumerate(row)}} for idx, row in
                            enumerate(result, start=1)]"""


def execute_query(sql_query, connection):
    try:
        cursor = connection.cursor()
        cursor.execute(sql_query)
        print("Cursor description :", cursor.description)
        print("Cursor messages :", cursor.messages)

        if not cursor.description and not cursor.messages:
            return None, None, ("Executed, but no records to display")
        elif cursor.description:
            columns = [column[0] for column in cursor.description]
        else:
            return None,cursor.messages,'Success'

        result = cursor.fetchall()

        table = PrettyTable()
        table.field_names = columns

        for row in result:
            table.add_row(row)

        print(table)
        print("Cursor fetchall", result)
        if not result:
            print("executed, but no records to display")
            return None, None, ("Executed, but no records to display")
        return columns, result, "SUCCESS"
    except pyodbc.Error as e:
        print("sorry, syntax error", str(e))
        return None, None, ("sorry, syntax error", str(e))


def text_to_speech(result):
    audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
    config.speech_synthesis_voice_name = 'en-US-JennyNeural'
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=config, audio_config=audio_config)
    text = f"{result}"
    print(result)
    speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()
    #print(speech_synthesis_result)


if __name__ == '__main__':
    #text_to_speech("Hello DBA's  ")
    substring = 'DROP'
    repeat = True
    while repeat:
        #text_to_speech("Please ask your query through the Microphone:")
        print("Listening:")
        user_query = speech_to_text()
        sql_query = generate_sql_query(user_query)

        if substring.lower() in sql_query.lower():
            text_to_speech("Are you sure want to execute below Query ? ")
            user_response = speech_to_text()
            if user_response == 'Yes.' or user_response == 'of course' or user_response == 'go ahead' or user_response == 'yeah.':
                print(user_response)
                connection_to_db(sql_query)
                text_to_speech("do you have any other queries ?")
                user_response = speech_to_text()
                if user_response == 'Yes.':
                    repeat = True
                else:
                    repeat = False
        else:
            print("Executing below Query")
            print(sql_query)
            connection_to_db(sql_query)
            text_to_speech("do you have any other queries ?")
            user_response = speech_to_text()
            if user_response == 'Yes.':
                repeat = True
            else:
                repeat = False

        #connection_to_db(generate_sql_query(speech_to_text()))