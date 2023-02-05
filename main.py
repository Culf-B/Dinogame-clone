import os
import ctypes

import menu, game

# Get monitor res with this fix: # https://gamedev.stackexchange.com/questions/105750/pygame-fullsreen-display-issue
ctypes.windll.user32.SetProcessDPIAware()
monitor_res = (ctypes.windll.user32.GetSystemMetrics(0),ctypes.windll.user32.GetSystemMetrics(1))

# Functions
def checkStopCode(stopCode):
    global stopCodes
    #try:
    stopCodes[stopCode]()
    '''except Exception as e:
        print("Error: ", stopCode)
        stopCodes["menu"]()'''

def gameOver():
    global pages
    score = pages["game"].player.score
    pages["game"].reset()
    pages["endScreen"].showEndScreen(score)

# Init menus/pages
pages = {
    "menu": menu.MainMenu(monitor_res),
    "game": game.Game(monitor_res),
    "endScreen": menu.EndScreen(monitor_res),
    "settings": menu.Settings(monitor_res)
}

# Load/init stopcodes
stopCodes = {
    "close": lambda: os._exit(1),
    "menu":pages["menu"].showMenu,
    "game":pages["game"].runGame,
    "settings":pages["settings"].showSettings,
    "gameOver": gameOver
}

# Set current stopcode
currentCode = "menu"

# Mainloop
while True:
    # Loop throug all pages
    for page in pages:
        # If page is neither idle or running:
        if pages[page].stopCode != "idle" and pages[page].stopCode != "running":
            # Set current code to the current page's code if it is neither running or idle
            currentCode = pages[page].stopCode
            # Set the page to idle
            pages[page].stopCode = "idle"
    # Run the code
    checkStopCode(currentCode)