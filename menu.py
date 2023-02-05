import pygame
import json
import pickle

from menuItems import Button, Text, Menu
import data

# Menu pages

# Main menu
class MainMenu(Menu):
    def __init__(self, true_monitor_res):
        super().__init__(true_monitor_res)

        # Create the menu
        self.text.append(Text(self.screenSize[0]//2, 20, "Dinosaur Game!", (200,200,255))) # Header
        self.buttons.append(Button(self.screenSize[0]//2-100, self.screenSize[1]//2-50, 200, 100, "Play!", (200,200,255), "game")) # Play
        self.buttons.append(Button(20, self.screenSize[1] - 70, 200, 50, "Settings", (200,200,255), "settings")) # Open Settings
        self.text.append(Text(self.screenSize[0]//2, self.screenSize[1]-50, f'Highscore: {data.get_playerdata()["high"]}', (200,200,255))) # Highscore
        self.buttons.append(Button(self.screenSize[0]-220, self.screenSize[1]-70, 200, 50, "Quit", (200,200,255), "close"))


    def showMenu(self):
        # Display settings
        self.screen = pygame.display.set_mode(self.screenSize, pygame.FULLSCREEN)
        pygame.display.set_caption("Game Over!")

        # Set stopCode
        self.stopCode = "running"

        while self.stopCode == "running":
            self.loop()

# End menu
class EndScreen(Menu):
    def __init__(self, true_monitor_res):
        super().__init__(true_monitor_res)

        # Get saved gamedata from gamedata.dat
        self.data = data.get_playerdata()

        # Score
        self.highScore = self.data["high"]
        self.lastScore = 0

        # Create the endscreen
        self.text.append(Text(self.screenSize[0]//2, 20, "Game Over!", (200,200,255))) # Header

        self.text.append(Text(self.screenSize[0]//2, 100, f"Highscore: {self.highScore}", (200,200,255), "high")) # Highscore
        self.text.append(Text(self.screenSize[0]//2, 200, f"Score: {self.lastScore}", (200,200,255), "last")) # Last score

        self.buttons.append(Button(self.screenSize[0]//2 - 225, 300, 200, 100, "Main menu", (200, 200, 255), "menu")) # Go to menu
        self.buttons.append(Button(self.screenSize[0]//2 + 25, 300, 200, 100, "Play again!", (200, 200, 255), "game")) # Play agai

    def showEndScreen(self, lastScore = 0):
        self.lastScore = lastScore
        # Safe last score as highscore if last score is greater than highscore
        if self.lastScore > self.highScore:
            # Save gamedata
            data.update_playerdata({"high":self.lastScore})      
            self.highScore = self.lastScore

        # Display settings
        self.screen = pygame.display.set_mode(self.screenSize, pygame.FULLSCREEN)
        pygame.display.set_caption("Game Over!")

        # Set stopCode
        self.stopCode = "running"

        # Mainloop
        while self.stopCode == "running":
            self.loop()
            for text in self.text:
                if text.id == "high": text.setText(f"Highscore: {self.highScore}")
                if text.id == "last": text.setText(f"Score: {self.lastScore}")

# Settings menu
class Settings(Menu):
    def __init__(self, true_monitor_res):
        super().__init__(true_monitor_res)

        # Create the settings menu
        self.text.append(Text(self.screenSize[0]//2, 20, "Settings", (200,200,255))) # Header

        # Settings
        self.settings = data.get_settings()

        self.y = 70
        for i in self.settings:
            self.buttons.append(Button(
                self.screenSize[0]//2 - (self.screenSize[0] - 40)//2, self.y, self.screenSize[0] - 40, 50, # Pos and size
                f"{i}: {self.settings[i]}", # Text
                (200,200,255), # Color
                lambda button: button.otherArgs["settings"].changeSetting(button.id), # Function
                1, # Codetype
                i, # ID (settingbutton id = setting)
                {"settings":self} # Other: referance to self (self = settings menu)
                ))
            self.y += 50

        self.buttons.append(Button(self.screenSize[0]//2 - 50, self.screenSize[1] - 75, 100, 50, "Menu", (200,200,255), "menu")) # Go to menu

    def changeSetting(self, setting):
        # Update setting
        if self.settings[setting] == True: self.settings[setting] = False
        else: self.settings[setting] = True
        # Update settings file
        data.update_settings(self.settings)
        # Update button text
        for button in self.buttons:
            if button.id == setting:
                button.setText(f"{setting}: {self.settings[setting]}")

    def showSettings(self):
        # Display settings
        self.screen = pygame.display.set_mode(self.screenSize, pygame.FULLSCREEN)
        pygame.display.set_caption("Settings")

        # Set stopCode
        self.stopCode = "running"

        # Mainloop
        while self.stopCode == "running":
            self.loop()
            