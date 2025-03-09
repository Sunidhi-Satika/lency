from Frontend.GUI import (
GraphicalUserInterface,
SetAssistantStatus,
ShowTextToScreen,
TempDirectoryPath,
SetMicrophoneStatus,
AnswerModifier,
QueryModifier,
GetMicrophoneStatus,
GetAssistantStatus )
from Backend.Model import FirstlayerDMM
from Backend.Automation import Automation
from Backend. SpeechToText import SpeechRecognition
from Backend.RealTimeSearchEngine import RealTimeSearchEngine
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import os
import psutil

IGscript_path = r"D:\A ki H G ki S undali\Backend\ImageGeneration.py"
venv_python = r"D:\A ki H G ki S undali\.venv\Scripts\python.exe"
env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
DefaultMessage = f'''{Username} : Hello {Assistantname}, How are you?
{Assistantname} : Welcome {Username}. I am doing well. How may I help you? '''
subprocesses = []
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search", "SearchAndOpenFile"]

def ShowDefaultChatIfNoChats():
    File = open(r'Data/Chatlog.json', "r", encoding='utf-8')
    if len(File.read())<5:
        with open(f"{TempDirectoryPath}/Database.data", 'w', encoding='utf-8') as file:
            file.write("")
        
        with open(f"{TempDirectoryPath}/Responses.data",'w', encoding='utf-8') as file:
            file.write(DefaultMessage)

def ReadChatLogJson():
    with open(r'Data/Chatlog.json', "r", encoding='utf-8') as file:
        chatlog_data = json.load(file)
    return chatlog_data

def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    for entry in json_data:

        if entry["role"] == "user":
            formatted_chatlog += f"User: {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"Assistant: {entry['content']}\n"

    formatted_chatlog = formatted_chatlog.replace("User", Username + " ")
    formatted_chatlog = formatted_chatlog.replace("Assistant", Assistantname + " ")

    with open(rf"{TempDirectoryPath}/Database.data", 'w', encoding='utf-8') as file:
        file.write(AnswerModifier(formatted_chatlog))

def ShowChatsOnGUI():
    File = open(rf"{TempDirectoryPath}/Database.data","r", encoding='utf-8')
    Data = File.read()
    if len(str(Data))>0:
        lines = Data.split('\n')
        result = '\n'.join(lines)
        File.close()
        File = open(rf"{TempDirectoryPath}/Responses.data", "w", encoding='utf-8')
        File.write(result)
        File.close()

def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatsOnGUI()

InitialExecution()

def MainExecution():

    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = ""

    SetAssistantStatus("Listening...")
    Query = SpeechRecognition()

    ShowTextToScreen(f"{Username}: {Query}")
    SetAssistantStatus("Thinking...") 
    Decision = FirstlayerDMM(Query)

    G = any([i for i in Decision if i.startswith("general")]) 
    R = any([i for i in Decision if i.startswith("realtime")])

    Mearged_query = " and ".join(
        [" ".join(i.split() [1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
    )

    for queries in Decision:
        if "generate" in queries: 
            ImageGenerationQuery = str(queries)
            ImageExecution = True

    for queries in Decision:
        if TaskExecution == False: 
            if any(queries.startswith(func) for func in Functions): 
                run(Automation(list(Decision)))
                TaskExecution = True

    if ImageExecution == True:

        with open(r"Frontend/Files/ImageGeneration.data", "w") as file:
            file.write(f"{ImageGenerationQuery},True")

        try:
            p1 = subprocess.Popen(
                [venv_python, IGscript_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False,
            )
            stdout, stderr = p1.communicate()

            if stdout:
                print(f"ImageGeneration.py Output:\n{stdout.decode()}")

            if stderr:
                print(f"ImageGeneration.py Error:\n{stderr.decode()}")

        except Exception as e:
            print(f"Error starting ImageGeneration.py: {e}")
        
    if G and R or R:

        SetAssistantStatus("Searching...") 
        Answer = RealTimeSearchEngine(QueryModifier(Mearged_query)) 
        ShowTextToScreen(f"{Assistantname}: {Answer}")
        SetAssistantStatus("Answering...") 
        TextToSpeech(Answer)
        return True

    else:
        for Queries in Decision:

            if "general" in Queries:
                SetAssistantStatus("Thinking...")
                QueryFinal = Queries.replace("general","")
                Answer = ChatBot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname}: {Answer}") 
                SetAssistantStatus("Answering...")
                TextToSpeech(Answer) 
                return True

            elif "realtime" in Queries:
                SetAssistantStatus("Searching...")
                QueryFinal = Queries.replace("realtime","")
                Answer = RealTimeSearchEngine(QueryModifier(QueryFinal)) 
                ShowTextToScreen(f"{Assistantname}: {Answer}")
                SetAssistantStatus("Answering...") 
                TextToSpeech(Answer)
                return True

            elif "exit" in Queries:
                QueryFinal = "Okay, Bye!"
                Answer = ChatBot(QueryModifier(QueryFinal)) 
                ShowTextToScreen(f"{Assistantname}: {Answer}")
                SetAssistantStatus("Answering...") 
                TextToSpeech(Answer)
                SetAssistantStatus("Answering...")
                cleanup()
                os._exit(1)

def cleanup():
    print("Cleaning up background processes...")
    current_pid = os.getpid()

    processes_to_kill = ["python", "msedge", "chrome", "chromium", "pyqtwebengine", "tensorflow_model_server"]

    for proc in psutil.process_iter(attrs=['pid', 'name']):
        try:
            if proc.info['name']:
                process_name = proc.info['name'].lower()
                if any(p in process_name for p in processes_to_kill) and proc.info['pid'] != current_pid:
                    print(f"Debug: Terminating {proc.info['name']} (PID: {proc.info['pid']})")
                    proc.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    print("Cleanup complete.")


def FirstThread():
    while True:
        CurrentStatus = GetMicrophoneStatus()

        if CurrentStatus == "True":
            MainExecution()

        else:
            AIStasus = GetAssistantStatus()

            if "Available..." in AIStasus:
                sleep(0.1)
            else:
                SetAssistantStatus("Available...")

def SecondThread():

    GraphicalUserInterface()

if __name__ == "__main__":
    thread2 = threading.Thread(target=FirstThread, daemon=True)
    thread2.start()
    SecondThread()