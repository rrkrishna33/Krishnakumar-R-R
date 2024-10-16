import tkinter
import azure.cognitiveservices.speech as speechsdk
import pyodbc
from flask import render_template
from openai import AzureOpenAI
from sqlalchemy import true, false
from prettytable import PrettyTable
from tkinter.font import Font
from tkinter import scrolledtext
from tkinter import *
from PIL import ImageTk, Image, ImageSequence


subscription_key = "cdfbdf50ae44415ea6b152f0ccfdd1d6"
region = "eastus"
config = speechsdk.SpeechConfig(subscription=subscription_key, region=region)
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=config)
audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
config.speech_synthesis_voice_name = 'en-US-GuyNeural'
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=config, audio_config=audio_config)

client = AzureOpenAI(
    api_key="5471262c1d224ca496238d489c335028",
    api_version="2024-02-01",
    azure_endpoint="https://globaldbaopenaiservice.openai.azure.com/"
)

deployment_name = 'gpt-4o'

def speech_to_text():
    # Record audio input from microphone
    #print("Speak into your microphone.")
    result = speech_recognizer.recognize_once_async().get()
    # Print and return transcribed text
    #transcribed_text = result.text
    text_output.insert(INSERT,"User Input : "+result.text+'\n',"color_blue")
    text_output.update_idletasks()
    #print("Transcribed Text:", transcribed_text)
    return result.text

def generate_sql_query(user_input, ):
    prompt = f"""Task: Generate only pyodbc MS SQL Query based on user input and return only Content without '`' symbol: 
            '{user_input}',and replace the values assigned to different forms of database names include backup directory C:\\backup, restore directory C:\\backup don't include ` symbol, add semicolon at the end of GO statement"""

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

    #print(response)

    if response:
        generated_query = response.choices[0].message.content
        generated_query: str = generated_query.replace('\\', '\\\\')
        #print(generated_query[generated_query.find(":") + 1:])
        return (generated_query)

    else:
        text_output.insert(INSERT,"No Response genertaed \n")
        text_output.update_idletasks()
        #print("No Response genertaed")
        return ("No Response Generated")

def connection_to_db(sql_query):
    try:
        #connection_string = f"Driver=ODBC Driver 18 for SQL Server;Server=tcp:globaldba-sqlserver.database.windows.net,1433;Database=master;Uid=GlobalDBA;Pwd=DBAGlobal_1;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
        connection_string = (
            'DRIVER=ODBC Driver 18 for SQL Server;'
            'SERVER=98.71.140.253,1434;'
            'DATABASE=master;'
            'UID=sa_admin;'
            'PWD=AzureAI@123;'
            'TrustServerCertificate=yes'
        )
        connection = pyodbc.connect(connection_string)
        connection.autocommit = true
    except:
        text_output.insert(INSERT, "Oops! Master Database not available in the Server and unable to connect... \n")
        text_output.update_idletasks()
        #print(f"Oops! Master Database not available in the Server and unable to connect...")
        return
    if not sql_query:
        text_output.insert(INSERT, "Failed to generate sql query \n")
        text_output.update_idletasks()
        #print("Failed to generate sql query")
    text_output.insert(INSERT, "connecting to database \n\n")
    text_output.update_idletasks()
    text_output.insert(INSERT, "Result : \n\n",'color_green')
    text_output.update_idletasks()
    #print('connecting to database')
    columns, result, status = execute_query(sql_query, connection)
    #print("Columns :", columns)
    #print("result :", result)
    text_output.insert(INSERT,status)
    text_output.update_idletasks()
    """if columns and result is not None and status == 'SUCCESS':
        formatted_result = [{'ID': idx, **{columns[i]: str(value) for i, value in enumerate(row)}} for idx, row in
                            enumerate(result, start=1)]"""

def execute_query(sql_query, connection):
    try:
        cursor = connection.cursor()
        cursor.execute(sql_query)
        #print("Cursor description :", cursor.description)
        #print("Cursor messages :", cursor.messages)

        if not cursor.description and not cursor.messages:
            return None, None, ("Executed, but no records to display \n")
        elif cursor.description:
            columns = [column[0] for column in cursor.description]
        else:
            return None, cursor.messages, 'Executed, but no records to display \n'

        result = cursor.fetchall()

        table = PrettyTable()
        table.field_names = columns

        for row in result:
            table.add_row(row)
        text_output.insert(INSERT,table)
        text_output.update_idletasks()
        text_output.insert(INSERT,'\n')
        text_output.update_idletasks()
        print(table)
        #text_output.insert(INSERT,result)
        #text_output.update_idletasks()
        #print("Cursor fetchall", result)
        if not result:
            #print("executed, but no records to display")
            return None, None, ("Executed, but no records to display \n")
        return columns, result, "Query has been executed \n"
    except pyodbc.Error as e:
        print("sorry, syntax error", str(e))
        return None, None, ("sorry, syntax error", str(e))

def text_to_speech(result):
    text = f"{result}"
    #speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()
    speech_synthesizer.speak_text_async(text).get()

def run_query():
    text_output.delete("1.0", "end")
    text_output.update_idletasks()
    text_output.insert(INSERT, 'Hello Techie.. \n')
    text_output.update_idletasks()
    text_to_speech("Hello Techie..")

    substring = 'DROP'
    repeat = True
    while repeat:
        text_output.insert(INSERT,"How may I assist you ?  \n",'color_red')
        text_output.update_idletasks()
        text_to_speech("How may I assist you ?")
        print("Listening:")
        text_output.insert(INSERT, "Listening \n")
        text_output.update_idletasks()
        user_query = speech_to_text()
        sql_query = generate_sql_query(user_query)

        if substring.lower() in sql_query.lower():
            text_output.insert(INSERT,"Are you sure want to execute below Query ?\n",'' )
            text_output.update_idletasks()
            text_output.insert(INSERT,'"'+sql_query+'"'+'\n','color_blue')
            text_output.update_idletasks()
            text_to_speech("Are you sure want to execute below Query ?\n")
            print("Listening:")
            text_output.insert(INSERT, "Listening \n")
            text_output.update_idletasks()
            user_response = speech_to_text()
            if user_response == 'Yes.' or user_response == 'of course' or user_response == 'go ahead' or user_response == 'yeah.':
                print(user_response)
                connection_to_db(sql_query)
                text_output.insert(INSERT,"do you have any other queries ?\n" )
                text_output.update_idletasks()
                text_to_speech("do you have any other queries ?")
                text_output.insert(INSERT,"Listening \n")
                text_output.update_idletasks()
                user_response = speech_to_text()
                if user_response == 'Yes.':
                    repeat = True
                else:
                    repeat = False
        else:
            text_output.insert(INSERT,"Executing below Query\n\n")
            text_output.update_idletasks()
            #print("Executing below Query")
            text_output.insert(INSERT,'"'+sql_query+'"'+'\n',my_font2)

            text_output.update_idletasks()
            connection_to_db(sql_query)
            text_output.insert(INSERT,"do you have any other queries ? \n")
            text_output.update_idletasks()
            text_to_speech("do you have any other queries ?")
            text_output.insert(INSERT,"Listening \n")
            text_output.update_idletasks()
            user_response = speech_to_text()
            if user_response == 'Yes.':
                repeat = True
            else:
                repeat = False

def write_query():
    text_output.delete("1.0", "end")
    text_output.update_idletasks()
    read = text_write.get(1.0, "end-1c")
    text_output.delete("1.0", "end")
    text_output.update_idletasks()
    text_output.insert(INSERT,"User Input: "+read+'\n','color_blue')
    text_output.update_idletasks()
    substring = 'DROP'
    sql_query = generate_sql_query(read)
    text_output.insert(INSERT,'"'+sql_query+'"'+'\n')
    text_output.update_idletasks()
    connection_to_db(sql_query)

class ResizableGIF(Label):
    def __init__(self, master, path, size):
        self.size = size
        self.frames = []
        self.delay = 0

        im = Image.open(path)
        for frame in ImageSequence.Iterator(im):
            frame = frame.resize(self.size)
            self.frames.append(ImageTk.PhotoImage(frame))
        self.delay = im.info['duration']

        self.idx = 0
        super().__init__(master, image=self.frames[self.idx])
        self.after(self.delay, self.next_frame)

    def next_frame(self):
        self.idx = (self.idx + 1) % len(self.frames)
        self.config(image=self.frames[self.idx])
        self.after(self.delay, self.next_frame)

def openNewWindow():

    def generate_user_query():
        messages = [ {"role": "system", "content":
            "You are a intelligent assistant."} ]

        message = text_input.get(1.0, "end-1c")

        if message:
            messages.append(
                {"role": "user", "content": message},

            )
        text_input.delete("1.0", "end")

        response1 = client.chat.completions.create(messages=messages, model=deployment_name)
        reply = response1.choices[0].message.content
        print(f"ChatGPT: {reply}")
        text_user_output.insert(INSERT,f"User : {message}\n")
        text_user_output.insert(INSERT,f"Assistant : {reply}\n")
        text_user_output.update_idletasks()
        messages.append({"role": "assistant", "content": reply})

    loadimage = Image.open('C:\\Users\\krishnakumar.ravi\\Downloads\\send.png')
    loadedimage = loadimage.resize((100, 100))
    rendered_image = ImageTk.PhotoImage(loadedimage)
    newWindow = Toplevel(app)
    newWindow.title("Query Optimization and General Knowledge")
    newWindow.geometry("1920x1080")
    text_label = Label(newWindow, text='AI Expert',font=my_font1)
    text_input = scrolledtext.ScrolledText(newWindow, height=8, width=120, bd=10)
    text_user_output = scrolledtext.ScrolledText(newWindow, bd=10, height=20, width=120)


    button_send = Button(newWindow, text='Send', height=2, width=4,command=generate_user_query)

    text_label.place(relx=0.1, rely=0.1)
    text_input.place(relx=0.1, rely=0.65)
    button_send.place(relx=0.87,rely=0.65)
    text_user_output.place(relx=0.1, rely=0.15)

def clear_text():
    text_write.delete("1.0", "end")


app = Tk()
app.title('Voice Tech Assistant')
app.geometry('1920x1080')

my_font = Font(size=20,slant="italic")
my_font1 = Font(size=13,slant="italic")
my_font2 = Font(slant="italic",size=15)

title_label = Label(text='Voice Tech assistant', background='#eed484', font=my_font)
title_label.place(relx=0.5, rely=0.1, height=50, width=3000, anchor=tkinter.CENTER)

load = Image.open('C:\\Users\\krishnakumar.ravi\\Downloads\\mic.png')
loaded = load.resize((40, 40))
render = ImageTk.PhotoImage(loaded)

size = (100, 100)  # Resize to 300x300 pixels
gif_path = 'C:\\Users\\krishnakumar.ravi\\Downloads\\man-talking.gif'

btn_voice_label = Label(text='Voice input', font=my_font1)
btn_voice = Button(image=render, command=run_query)
btn_write_label = Label(text='Query input', font=my_font1)
text_write = scrolledtext.ScrolledText(height=3, width=60)
btn_write_submit = Button(text='Submit', font=my_font1,command=write_query)
output_label = Label(text='Result Output', font=my_font1)
text_output = Text(height=20, width=150,wrap="none")
text_output.tag_configure('color_green',foreground="Green")
text_output.tag_configure('color_red',foreground="RED")
text_output.tag_configure('color_blue',foreground="blue")
btn_clear = Button(text='clear',command=clear_text,font=my_font1)
scrollhorizontal = Scrollbar(app, orient="horizontal", command=text_output.xview,width=20)
text_output.configure(xscrollcommand=scrollhorizontal.set)
btn_new = Button(text="Query Generate",command=openNewWindow,font=my_font1)

btn_voice_label.place(relx=0.01, rely=0.16)
btn_voice.place(relx=0.15, rely=0.16)
btn_write_label.place(relx=0.5, rely=0.14)
text_write.place(relx=0.5, rely=0.18)
btn_write_submit.place(relx=0.915, rely=0.18)
btn_clear.place(relx=0.915, rely=0.24)
btn_new.place(relx=0.85,rely=0.30)
output_label.place(relx=0.01, rely=0.34)
text_output.place(relx=0.01, rely=0.38)
scrollhorizontal.place(relx=0.01,rely=0.88)
gif_label = ResizableGIF(app, gif_path, size)
gif_label.place(relx=0.2, rely=0.15)

app.mainloop()
