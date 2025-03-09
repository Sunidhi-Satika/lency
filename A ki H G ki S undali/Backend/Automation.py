from AppOpener import close, open as appopen
import webbrowser
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from rich import print
from groq import Groq
import webbrowser
import subprocess
import keyboard
import asyncio
import os
import time
import re
import math

env_vars = dotenv_values(".env")
GroqAPIkey = env_vars.get("GroqAPIkey")

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebkit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36"

client = Groq(api_key=GroqAPIkey)

professional_responses = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything I can help with.",
    "I'm at your service for any additional questions or support you may need-don't hesitate to ask.",
]

messages = []

SystemChatBot = [{"role": "system", "content": f"Hello, I am {os.environ['username']}, You have to write content like letters, codes, applications, essays, notes, songs etc"}]

WebsiteBot = [{"role": "system", "content": f"Hello, I am {os.environ['username']}, You have to tell me official website links of any website asked. Tell only the link not even a single extra word is allowed"}]

file_extensions = {
    "pdf": [".pdf"],
    "word": [".doc", ".docx"],
    "excel": [".xls", ".xlsx", ".csv"],
    "ppt": [".ppt", ".pptx"],
    "text": [".txt", ".md", ".rtf"],
    "video": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv"],
    "audio": [".mp3", ".wav", ".aac", ".ogg", ".flac", ".m4a"],
    "image": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"],
    "code": [".py", ".java", ".c", ".cpp", ".html", ".css", ".js", ".php", ".json", ".xml", ".sql", ".sh", ".bat"]
}

def GoogleSearch(Topic):
    search(Topic)
    return True

def Content(Topic):
    def OpenNotepad(File):
        default_text_editor = 'notepad.exe'
        subprocess.Popen([default_text_editor, File])
    
    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": f"{prompt}"})

        completion = client.chat.completions.create(
            model = "mixtral-8x7b-32768",
            messages=SystemChatBot + messages[-5],
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True,
        )

        Answer = ""

        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.replace("</s>", "")

        messages.append({"role": "assistant", "content": Answer})
        return Answer
    
    Topic: str = Topic.replace("content ", "")
    ContentByAI = ContentWriterAI(Topic)

    with open(rf"Data/{Topic.lower().replace(' ','')}.txt", "w", encoding="utf-8") as file:
        file.write(ContentByAI)
        file.close()

    OpenNotepad(rf"Data/{Topic.lower().replace(' ','')}.txt")
    return True

def YoutubeSearch(Topic):
    Url4Search = f"https://www.youtube.com/results?search_query={Topic}"
    webbrowser.open(Url4Search)
    return True

def PlayYoutube(query):
    playonyt(query)
    return True

def OpenApp(app):

    try:
        print(f"Debug: Trying to open {app}")
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True
    except Exception as e:
        print(f"Debug: {e} - App not installed, Trying to open in web.")

    try:

        completion = client.chat.completions.create(
            model="gemma2-9b-it",
            messages= WebsiteBot + [{"role": "user", "content": f"What is the official website of {app}?"}],
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=False  # No need for streaming in this case
        )

        websitelink = completion.choices[0].message.content
        print(f"debug: {websitelink}")
        webbrowser.open(f"{websitelink}")

    except Exception as e:
        print(f"Debug: Error while querying ChatBot -> {e}")
        return None

def CloseApp(app):
    
    if "msedge" in app:
        pass
    else:
        try:
            close(app, match_closest=True, output=True, throw_error=True)
            return True
        except:
            return False

def SearchAndOpenFile(file_type, file_name, search_dirs=["D:\\", "C:\\"]):
    """Search and open a file based on type and filename keywords."""

    if file_type not in file_extensions:
        print(f"Debug: Unknown file type '{file_type}'.")
        return False

    found_files = []

    for drive in search_dirs:
        if not os.path.exists(drive):
            continue
        
        for root, _, files in os.walk(drive, topdown=True):
            for file in files:
                if any(file.lower().endswith(ext) for ext in file_extensions[file_type]):
                    # Convert underscores, dashes, and special characters into spaces
                    cleaned_name = re.sub(r"[_\-@.]", " ", file).lower()
                    if all(word in cleaned_name for word in file_name.lower().split()):
                        found_files.append(os.path.join(root, file))

    if not found_files:
        print(f"Debug: No {file_type} file found matching '{file_name}'.")
        return False

    file_path = found_files[0]
    print(f"Debug: Opening {file_path}")
    subprocess.Popen(["start", "", file_path], shell=True)
    return True

def System(command):
    """Handles system commands like volume control with step adjustments."""
    try:
        match = re.search(r"(increase|decrease|volume up|volume down|mute|unmute)\s*(\d+)?", command, re.IGNORECASE)

        if not match:
            print(f"Debug: Unknown system command: '{command}'")
            return False

        action = match.group(1).lower()
        amount = int(match.group(2)) if match.group(2) else 5
        amount = math.ceil(amount/2)
        if action in ["mute", "unmute"]:
            keyboard.press_and_release("volume mute")
            print(f"Debug: Executed '{action}'")
        elif action in ["increase", "volume up"]:
            for _ in range(amount):
                keyboard.press_and_release("volume up")
                time.sleep(0.05)  # Small delay to make the increase gradual
            print(f"Debug: Increased volume by {amount} steps")
        elif action in ["decrease", "volume down"]:
            for _ in range(amount):
                keyboard.press_and_release("volume down")
                time.sleep(0.05)  # Small delay to make the decrease gradual
            print(f"Debug: Decreased volume by {amount} steps")
        else:
            print(f"Debug: Unrecognized volume command: '{command}'")
            return False

        return True
    except Exception as e:
        print(f"Debug: Error executing '{command}': {e}")
        return False

async def TranslateAndExecute(commands: list[str]):

    funcs = []

    for command in commands:
        try:
            if command.startswith("open "):
                if "open it " in command:
                    pass
                if "open file " in command:
                    pass
                else:
                    fun = asyncio.to_thread(OpenApp, command.removeprefix("open "))
                    funcs.append(fun)
            elif command.startswith("general "):
                pass
            elif command.startswith("realtime "):
                pass
            elif command.startswith("close "):
                fun = asyncio.to_thread(CloseApp, command.removeprefix("close "))
                funcs.append(fun)
            elif command.startswith("play "):
                fun = asyncio.to_thread(PlayYoutube, command.removeprefix("play "))
                funcs.append(fun)
            elif command.startswith("content "):
                fun = asyncio.to_thread(Content, command.removeprefix("content "))
                funcs.append(fun)
            elif command.startswith("google search "):
                fun = asyncio.to_thread(GoogleSearch, command.removeprefix("google search "))
                funcs.append(fun)
            elif command.startswith("youtube search "):
                fun = asyncio.to_thread(YoutubeSearch, command.removeprefix("youtube search "))
                funcs.append(fun)
            elif command.startswith("system "):
                fun = asyncio.to_thread(System, command.removeprefix("system "))
                funcs.append(fun)
            elif command.startswith("SearchAndOpenFile "):
                parts = command.replace("SearchAndOpenFile ", "").split(" ", 1)
                if len(parts) == 2:
                    file_name, file_type = parts
                    print(f"Debug: Searching for {file_type} file named '{file_name}'...")
                    fun = asyncio.to_thread(SearchAndOpenFile, file_type, file_name)
                    funcs.append(fun)
                else:
                    print(f"Debug: Invalid SearchAndOpenFile format -> {command}")
            else:
                print(f"No Function Found. For {command}")

        except Exception as e:
            print(f"Debug: Error processing command '{command}': {e}")

    results = await asyncio.gather(*funcs, return_exceptions=True)

    for result in results:
        if isinstance(result, Exception):
            print(f"Debug: Command execution error -> {result}")
        else:
            yield result

async def Automation(commands: list[str]):

    async for result in TranslateAndExecute(commands):
        pass

    return True
