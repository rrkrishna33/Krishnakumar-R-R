import tkinter
import azure.cognitiveservices.speech as speechsdk
import pyodbc
from openai.lib.azure import AzureOpenAI
from pyodbc import Connection
from sqlalchemy import true, false
from prettytable import PrettyTable
from tkinter.font import Font
from tkinter import scrolledtext, simpledialog
from tkinter import messagebox
from tkinter import *
from PIL import ImageTk, Image, ImageSequence

subscription_key = "SPEECH API KEY"
region = "eastus"
config = speechsdk.SpeechConfig(subscription=subscription_key, region=region)
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=config)
audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
config.speech_synthesis_voice_name = 'en-US-GuyNeural'
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=config, audio_config=audio_config)


substring1 = 'DROP'
substring2 = 'Truncate'
substring3 = 'DELETE'
file_path = "C:\\Users\\krishnakumar.ravi\\PycharmProjects\\DB_Assistant\\prompts.txt"
with open(file_path, 'r') as file:
    content = file.read()
client = AzureOpenAI(


    api_key="API_KEY",
    api_version="2024-02-01",
    azure_endpoint="Azure End point"
)
deployment_name = 'gpt-4o'


def speech_to_text():
    result = speech_recognizer.recognize_once_async().get()
    text_output.insert(INSERT, "User Input : " + result.text + '\n', "color_blue")
    text_output.update_idletasks()
    return result.text


def generate_sql_query(user_input):
    prompt = content
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": "which is the largest database in server"},
        {"role": "assistant",
         "content": "SELECT TOP 1 name AS DatabaseName, (size*8)/1024 AS SizeMB FROM sys.master_files GROUP BY name, "
                    "size ORDER BY SizeMB DESC"},
        {"role": "user", "content": user_input}
    ]
    response = client.chat.completions.create(messages=messages, model=deployment_name)
    if response:
        generated_query = response.choices[0].message.content
        generated_query: str = generated_query.replace('\\', '\\\\')
        return generated_query
    else:
        text_output.insert(INSERT, "No Response generated \n")
        text_output.update_idletasks()
        return "No Response Generated"

def db_connection(username, password, connect=None):
    global connecting
    try:
        #connection_string = f"Driver=ODBC Driver 18 for SQL Server;Server=tcp:globaldba-sqlserver.database.windows.net,1433;Database=master;Uid=GlobalDBA;Pwd=DBAGlobal_1;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
        connection_string = (
            'DRIVER=ODBC Driver 18 for SQL Server;'
            'SERVER=<IP_ADDRESS>;'
            'DATABASE=master;'
            f'UID={username};'
            f'PWD={password};'
            'TrustServerCertificate=yes'
        )
        connecting = pyodbc.connect(connection_string)
        connecting.autocommit = true
        return 'connected'
    except:
        return 'fail'



def connection_to_db(sql_query):


    if not sql_query:
        text_output.insert(INSERT, "Failed to generate sql query \n")
        text_output.update_idletasks()

    text_output.insert(INSERT, "Connected with database waiting for results \n\n")
    text_output.update_idletasks()
    text_output.insert(INSERT, "Result : \n\n", 'color_green')
    text_output.update_idletasks()
    columns, result, status = execute_query(sql_query, connecting)
    if result:
        text_output.insert(INSERT, f"{result} \n")
        text_output.update_idletasks()
    else:
        text_output.insert(INSERT, status)
        text_output.update_idletasks()


def execute_query(sql_query, connects):

    try:
        cursor = connects.cursor()
        cursor.execute(sql_query)

        if not cursor.description and not cursor.messages:
            return None, None, "Commands executed successfully, but no records to display \n"

        elif cursor.description:
            columns = [column[0] for column in cursor.description]

        else:
            return None, cursor.messages, 'Executed, but no records to display \n'

        result = cursor.fetchall()
        table = PrettyTable()
        table.field_names = columns

        for row in result:
            table.add_row(row)

        # noinspection PyTypeChecker
        text_output.insert(INSERT, table)
        text_output.update_idletasks()
        text_output.insert(INSERT, '\n')
        text_output.update_idletasks()

        if not result:
            return None, None, "Executed, but no records to display \n"

        return columns, result, "Query has been executed \n"
    except pyodbc.Error as e:
        print("sorry, syntax error", str(e))
        return None, None, ("sorry, syntax error", str(e))


def text_to_speech(result):
    text = f"{result}"
    speech_synthesizer.speak_text_async(text).get()


def run_query():
    text_output.insert(INSERT, 'Hello Techie.. \n')
    text_output.update_idletasks()
    text_to_speech("Hello Techie..")
    text_output.insert(INSERT, "How may I assist you ?  \n", 'color_red')
    text_output.update_idletasks()
    text_to_speech("How may I assist you ?")
    text_output.see(tkinter.END)

    repeat = True
    while repeat:
        text_output.insert(INSERT, "Listening \n")
        text_output.update_idletasks()
        user_query = speech_to_text()
        sql_query = generate_sql_query(user_query)

        if substring1.lower() in sql_query.lower() or substring2.lower() in sql_query.lower() or substring3.lower() in sql_query.lower():

            text_output.insert(INSERT, "Are you sure want to execute below Query ?\n", '')
            text_output.update_idletasks()
            text_to_speech("Are you sure want to execute below Query ?\n")
            text_output.insert(INSERT, '"' + sql_query + '"' + '\n', 'color_blue')
            text_output.update_idletasks()
            text_output.insert(INSERT, "Listening \n")
            text_output.update_idletasks()
            user_response = speech_to_text()
            if user_response == 'Yes' or user_response == 'of course' or user_response == 'go ahead' or user_response == 'yeah':
                connection_to_db(sql_query)
                text_output.insert(INSERT, "do you have any other queries ?\n")
                text_output.update_idletasks()
                text_to_speech("do you have any other queries ?")
                text_output.insert(INSERT, "Listening \n")
                text_output.see(tkinter.END)
                text_output.update_idletasks()
                user_response = speech_to_text()
                if user_response == 'Yes.':
                    repeat = True
                else:
                    repeat = False
        else:
            text_output.insert(INSERT, "Executing below Query\n\n")
            text_output.update_idletasks()
            # noinspection PyTypeChecker
            text_output.insert(INSERT, '"' + sql_query + '"' + '\n', my_font2)

            text_output.update_idletasks()
            connection_to_db(sql_query)
            text_output.insert(INSERT, "do you have any other queries ? \n")
            text_output.update_idletasks()
            text_to_speech("do you have any other queries ?")
            text_output.insert(INSERT, "Listening \n")
            text_output.update_idletasks()
            user_response = speech_to_text()
            if user_response == 'Yes.':
                repeat = True
            else:
                repeat = False


def write_query():
    read = text_write.get(1.0, "end-1c")
    text_output.delete("1.0", "end")
    text_output.update_idletasks()
    text_output.insert(INSERT, "User Input: " + read + '\n', 'color_blue')
    text_output.update_idletasks()
    sql_query = generate_sql_query(read)

    if substring1.lower() in sql_query.lower() or substring2.lower() in sql_query.lower() or substring3.lower() in sql_query.lower():
        text_output.insert(INSERT, "Are you sure want to execute below Query ?\n", '')
        text_output.update_idletasks()
        text_output.insert(INSERT, '"' + sql_query + '"' + '\n')
        text_output.update_idletasks()
        result = messagebox.askquestion(title="Confirmation", message=""'Are you sure want to execute below Query')

        if result == 'yes':
            connection_to_db(sql_query)
        else:
            text_output.insert(INSERT, 'User Cancelled the transaction. \n')
            text_output.update_idletasks()
    else:
        text_output.insert(INSERT, "Executing Below Query \n")
        text_output.update_idletasks()
        text_output.insert(INSERT, '"' + sql_query + '"' + '\n')
        text_output.update_idletasks()
        connection_to_db(sql_query)


class ResizableGIF(Label):
    def __init__(self, master, path, sizes):
        self.size = sizes
        self.frames = []
        self.delay = 0

        im = Image.open(path)
        for frame in ImageSequence.Iterator(im):
            frame = frame.resize(self.size)
            self.frames.append(ImageTk.PhotoImage(frame))
        self.delay = im.info['duration']

        self.idx = 0
        # noinspection PyTypeChecker
        super().__init__(master, image=self.frames[self.idx])
        self.after(self.delay, self.next_frame)

    def next_frame(self):
        self.idx = (self.idx + 1) % len(self.frames)
        # noinspection PyTypeChecker
        self.config(image=self.frames[self.idx])
        self.after(self.delay, self.next_frame)


def ai_expert_window():
    def generate_user_query():
        prompt_filepath = "C:\\Users\\krishnakumar.ravi\\PycharmProjects\\DB_Assistant\\prompt_newwindow.txt"
        with open(prompt_filepath, 'r') as files:
            contents = files.read()
        message = text_input.get(1.0, "end-1c")
        prompt = contents

        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": "how to tune the SQL Query"},
            {"role": "user", "content": message}
        ]
        if message:
            messages.append(
                {"role": "user", "content": message},
            )
        text_input.delete("1.0", "end")

        response1 = client.chat.completions.create(messages=messages, model=deployment_name)
        reply = response1.choices[0].message.content
        print(f"ChatGPT: {reply}")
        text_user_output.insert(INSERT, f"User : {message}\n")
        text_user_output.insert(INSERT, f"Assistant : {reply}\n")
        text_user_output.update_idletasks()
        messages.append({"role": "assistant", "content": reply})

    expert_window = Toplevel(app)
    expert_window.title("Query Optimization and General Knowledge")
    expert_window.geometry("1920x1080")
    text_label = Label(expert_window, text='AI Expert', font=my_font1)
    text_input = scrolledtext.ScrolledText(expert_window, height=8, width=120, bd=10)
    text_user_output = scrolledtext.ScrolledText(expert_window, bd=10, height=20, width=120)

    button_send = Button(expert_window, text='Send', height=2, width=4, command=generate_user_query)

    text_label.place(relx=0.1, rely=0.085)
    text_input.place(relx=0.1, rely=0.65)
    button_send.place(relx=0.87, rely=0.65)
    text_user_output.place(relx=0.1, rely=0.12)


def clear_text():
    text_write.delete("1.0", "end")


class LoginDialog(simpledialog.Dialog):
    def body(self, master):
        self.title("Login")

        tkinter.Label(master, text="Username:").grid(row=0, column=0)
        self.username_entry = tkinter.Entry(master)
        self.username_entry.grid(row=0, column=1)

        tkinter.Label(master, text="Password:").grid(row=1, column=0)
        self.password_entry = tkinter.Entry(master, show="*")
        self.password_entry.grid(row=1, column=1)

        return self.username_entry

    def apply(self):
        self.username = self.username_entry.get()
        self.password = self.password_entry.get()


def show_login_dialog():

    login_window.transient(app)
    login_window.grab_set()

    dialog = LoginDialog(login_window)
    return dialog.username, dialog.password

def check_credentials(username, password):
    # Replace with actual credential checking logic
    return username == "sa_admin" and password == "AzureAI@123"

def open_main_window():
    app.withdraw()  # Hide the root window initially

    username, password = show_login_dialog()
    print(username,password)
    status = db_connection(username,password)
    print(status)
    if status == 'connected':
        main_window()
        login_window.destroy()

    #if check_credentials(username, password):
     #   main_window()
      #  login_window.destroy()

    else:
        tkinter.messagebox.showerror("Login failed", "Incorrect username or password")
        app.destroy()

def main_window():
    app.deiconify()
    app.title('Voice Tech Assistant')
    app.geometry('1920x1080')

app = Tk()
login_window = tkinter.Toplevel(app)
app.withdraw()
open_main_window()

my_font = Font(size=20, slant="italic")
my_font1 = Font(size=13, slant="italic")
my_font2 = Font(slant="italic", size=15)
title_label = Label(text='Voice Tech assistant', background='#eed484', font=my_font)
title_label.place(relx=0.5, rely=0.1, height=50, width=3000, anchor=tkinter.CENTER)
load = Image.open('C:\\Users\\krishnakumar.ravi\\Downloads\\mic.png')
loaded = load.resize((40, 40))
render = ImageTk.PhotoImage(loaded)
size = (100, 100)  # Resize to 300x300 pixels
gif_path = 'C:\\Users\\krishnakumar.ravi\\Downloads\\man-talking.gif'
btn_voice_label = Label(text='Voice input', font=my_font1)
# noinspection PyTypeChecker
btn_voice = Button(image=render, command=run_query)
btn_write_label = Label(text='Query input', font=my_font1)
text_write = scrolledtext.ScrolledText(height=3, width=60)
btn_write_submit = Button(text='Submit', font=my_font1, command=write_query)
output_label = Label(text='Result Output', font=my_font1)
text_output = Text(height=20, width=150, wrap="none")
text_output.tag_configure('color_green', foreground="Green")
text_output.tag_configure('color_red', foreground="RED")
text_output.tag_configure('color_blue', foreground="blue")
btn_clear = Button(text='clear', command=clear_text, font=my_font1)
scrollhorizontal = Scrollbar(app, orient="horizontal", command=text_output.xview, width=20)
text_output.configure(xscrollcommand=scrollhorizontal.set)
btn_new = Button(text="Seek Assistant", command=ai_expert_window, font=my_font1)
btn_voice_label.place(relx=0.01, rely=0.16)
btn_voice.place(relx=0.15, rely=0.16)
btn_write_label.place(relx=0.5, rely=0.14)
text_write.place(relx=0.5, rely=0.18)
btn_write_submit.place(relx=0.915, rely=0.18)
btn_clear.place(relx=0.915, rely=0.24)
btn_new.place(relx=0.20, rely=0.30)
output_label.place(relx=0.01, rely=0.34)
text_output.place(relx=0.01, rely=0.38)
scrollhorizontal.place(relx=0.01, rely=0.88)
gif_label = ResizableGIF(app, gif_path, size)
gif_label.place(relx=0.2, rely=0.15)



app.mainloop()




