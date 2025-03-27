import requests
import tkinter as tk
import mss
import pytesseract
from PIL import Image, ImageTk, ImageOps
import os
import time
import threading

kill = False
class ShinyCounterApp():
    def __init__(self, root):
        self.root = root
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.geometry("300x250")
        self.root.title("Shiny Encounter Tool")
        self.main_menu()
    
    def on_closing(self):
        global kill
        kill = True
        print("Closing app")
        root.destroy()

    def main_menu(self):
        for widget in self.root.winfo_children():  # Clear the current screen
            widget.destroy()
        self.label = tk.Label(root, text="Shiny Encounter Tool", font=("Arial", 14))
        self.label.pack(pady=10)

        self.label2 = tk.Label(root, text="Name for the current hunt", font=("Arial", 14))
        self.label2.pack(pady=10)
        self.pokemon_field = tk.Entry(root, width=10)
        self.pokemon_field.pack(pady=5)
        self.buttonStart = tk.Button(root,text="Start Hunt",command=self.start_hunt)
        self.buttonStart.pack(pady = 10)

    def start_hunt(self):
        self.pokemon_name = self.pokemon_field.get()
        pokemonList = open("list.txt","r").readlines()
        if self.pokemon_name+"\n" in pokemonList:
            if not self.pokemon_name+".png" in os.listdir("image/"):
                url = f"https://pokeapi.co/api/v2/pokemon/{self.pokemon_name.lower()}"
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    shiny_url = data["sprites"]["other"]["home"]["front_shiny"]
                    img_data = requests.get(shiny_url).content
                    save = open("image/"+self.pokemon_name+".png","wb")
                    save.write(img_data)
                    save.close()
                else:
                    print("Couldn't fetch data")
            global kill
            kill = False
            self.huntingMenu(self.pokemon_name)

    def search_hunt(self,pokemonName):
        folder = "currentHunt/"
        files = os.listdir(folder)
        if pokemonName in files:
            file = open(folder+pokemonName,"r")
            return file.readline()
        return 0
    
    def huntingMenu(self,pokemonName):
        for widget in self.root.winfo_children():
            widget.destroy()
        file_path = "image/"+pokemonName+".png"

        if os.path.exists(file_path):
            img = Image.open(file_path)
            img = img.resize((125, 125))
            self.img = ImageTk.PhotoImage(img)
            img_label = tk.Label(root, image=self.img)
            img_label.pack(pady=10)
        else:
            self.img_label.config(text="Image not found", image="")

        self.counter = int(self.search_hunt(pokemonName))
        self.counter_label = tk.Label(self.root,text=self.counter,font=("Arial",14))
        self.counter_label.pack(pady = 10)
        self.quit = tk.Button(self.root,text="Exit",width=10 ,command=self.save_hunt)
        self.quit.pack(pady=10)
        thread = threading.Thread(target=self.run_loop)
        thread.start()

    def save_hunt(self):
        global kill
        file = open("currentHunt/"+self.pokemon_name,"w")
        file.write(str(self.counter))
        file.close()
        kill = True
        self.main_menu()

    def run_loop(self):
        global kill
        seen = False
        start = time.time()
        while not kill:
            next = time.time()
            if next-start > 1:
                img = self.capture_screen()
                result = pytesseract.image_to_string(img)
                if  self.pokemon_name in result:
                    if not seen:
                        print(self.pokemon_name+" seen")
                        self.counter+=1
                        self.counter_label.config(text=self.counter)
                        seen  = True
                else:
                    seen = False
                start = time.time()
    def capture_screen(self):
        with mss.mss() as sct:
            screenshot = sct.grab(sct.monitors[1])
            img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
            img = ImageOps.grayscale(img)
            width,heigth = img.size
            img = img.crop((0,heigth//2,width//2,heigth))
            return img
root = tk.Tk()
app = ShinyCounterApp(root)
root.mainloop()