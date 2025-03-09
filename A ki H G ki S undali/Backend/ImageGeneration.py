import asyncio
import requests
from random import randint
from PIL import Image
from dotenv import load_dotenv
from time import sleep
import os

load_dotenv()
HuggingFaceAPI = os.getenv("HuggingFaceAPI")

def open_images(prompt):
    folder_path = r"Data"
    prompt = prompt.replace(" ", "_")

    files = [f"{prompt}{i}.jpg" for i in range(1, 4)]

    for jpg_file in files:
        image_path = os.path.join(folder_path, jpg_file)

        try:
            img = Image.open(image_path)
            print(f"Opening image: {image_path}")
            img.show()
            sleep(1)
        except IOError:
            print(f"Unable to open: {image_path}")

API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {HuggingFaceAPI}"}

async def query(prompt):
    payload = {
            "inputs": f"{prompt}, quality=4K, sharpness=maximum, Ultra High details, high resolution, seed={randint(0, 1000000)}"
        }
    response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}, {response.text}")
        return None
    
    return response.content

async def generate_images(prompt: str):

    tasks = [query(prompt) for _ in range(3)] 
    image_data_list = await asyncio.gather(*tasks)

    if not any(image_data_list):  # Check if all requests failed
        print("No images were generated.")
        return

    for i, image_data in enumerate(image_data_list):
        if image_data:
            file_path = fr"Data/{prompt.replace(' ', '_')}{i+1}.jpg"
            with open(file_path, "wb") as f:
                f.write(image_data)
            print(f"Image saved: {file_path}")

        # Add a delay to avoid rate limits
        sleep(5)

def GenerateImages(prompt: str):
    asyncio.run(generate_images(prompt))
    open_images(prompt)

def main():
    while True:
        try:
            with open(r"Frontend/Files/ImageGeneration.data", "r") as f:
                data = f.read().strip()

            if not data:
                sleep(1)
                continue

            prompt, status = data.split(",")

            if status == "True":
                print("Generating Images...")
                GenerateImages(prompt=prompt)

                with open(r"Frontend/Files/ImageGeneration.data", "w") as f:
                    f.write("False,False")

                break
            else:
                sleep(1)

        except Exception as e:
            print(f"Error: {e}")
            sleep(1)

if __name__ == "__main__":
    main()