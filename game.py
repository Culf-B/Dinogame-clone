import pygame
from random import randint
from os import walk
import json
import math
import pickle
import ctypes

from menuItems import Button, Text
import data

pygame.init()

class Game:
    def __init__(self, true_monitor_res):
        # Vars
        self.gameOver = False
        self.paused = False

        self.speed_noDelta = 40
        self.speed = self.speed_noDelta

        # Clock
        self.clock = pygame.time.Clock()

        # Set stop/status code
        self.stopCode = "idle"

        # Set screen size
        self.screenSize = true_monitor_res

        # Obstackle spawning
        self.obstackles = []
        self.timeSinceLastObs = self.screenSize[0]

        # Settings
        self.settings = {}
        self.updateSettings()

        # Menu
        self.menu = PauseMenu(self.setStopCode, self.screenSize, self.unPause)

        # delta and stats
        self.lastTicksSinceInit = 0.16
        self.fps = 0

    def setStopCode(self, code):
        self.stopCode = code

    def unPause(self):
        self.paused = False

    def updateSettings(self):
        self.settings = data.get_settings()

    def reset(self):
        # Vars
        self.gameOver = False
        self.paused = False
        self.speed_noDelta = 40
        self.speed = self.speed_noDelta

        # Set stop/status code
        self.stopCode = "idle"

        # Init game objects
        self.scene = Scene((self.screenSize[0], self.screenSize[1]//5), self.screenSize)
        self.player = Player(self, 'images\\dino\\')

        # Obstackle spawning
        self.obstackles = []
        self.timeSinceLastObs = self.screenSize[0]

    def runGame(self):

        # Display settings
        self.screen = pygame.display.set_mode(self.screenSize, pygame.FULLSCREEN)

        self.reset() # Reset the game before starting
        self.updateSettings() # Update game settings
        
        pygame.display.set_caption("Game")

        # Set stopCode
        self.stopCode = "running"

        # Mainloop
        while self.stopCode == "running":
            # Eventloop
            for event in pygame.event.get():
                # Exit with stopcode "close"
                if event.type == pygame.QUIT:
                    self.stopCode = "close"
                # Toggle pause menu
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if self.paused: self.paused = False
                    else: self.paused = True

            # Calculate deltatime
            self.ticksSinceInit = pygame.time.get_ticks()
            # deltaTime in seconds.
            self.deltaTime = (self.ticksSinceInit - self.lastTicksSinceInit) / 1000
            self.lastTicksSinceInit = self.ticksSinceInit

            # Calculate fps and speed
            if self.deltaTime != 0: self.fps = 1//self.deltaTime
            self.speed = self.deltaTime * self.speed_noDelta

            # If gameover: go to menu
            if self.gameOver:
                self.stopCode = "menu"
            if self.paused:
                self.menu.show(self.screen)
                self.menu.getInput()
                # Update display
                pygame.display.flip()
                self.clock.tick_busy_loop(60)
                continue

            # Draw
            self.scene.draw(self.screen, self.speed)
            self.scene.showScore(self.screen, self.player.score)

            self.player.draw(self.screen)
            self.player.checkForEvents()
            self.player.jump(self.speed, self.deltaTime)

            # Show fps if showPerformance setting == True
            if self.settings["showPerformance"]: self.scene.showFPS(self.screen, self.fps)

            # Obstackles
            if self.player.jumps > 0: self.spawnObstackles() # Spawn obstackles if player is running (player starts running when it jumps the 1. time)
            else: self.scene.showStartText(self.screen)# Show text that tells user to jump to start the game
            for obstackle in self.obstackles:
                obstackle.draw(self.screen)
                obstackle.move(self.speed)
                if obstackle.checkCollision(self.player):
                    self.stopCode = "gameOver"

            # Update display
            pygame.display.flip()
            self.clock.tick_busy_loop(60)

            # clean up
            self.delObstackles()

    # Will delete all obstackles that has moved outside the screen
    def delObstackles(self):

        self.toDelete = []

        for i in range(len(self.obstackles)):
            if self.obstackles[i].isOut():
                self.toDelete.append(i)

        for i in self.toDelete:
            del self.obstackles[i]

        self.toDelete = []

    def spawnObstackles(self):
        if self.timeSinceLastObs > self.player.jumpTime * 1.3:
            if randint(0,10) == 0:
                self.obstackles.append(Obstackle('images\cactus.png', self, obsType=randint(0,1)))
                self.timeSinceLastObs = 0
                self.speed_noDelta *= 1.005
                self.player.score += 1
        self.timeSinceLastObs += 1

class Player(pygame.sprite.Sprite):
    def __init__(self, game, imgFolder):

        pygame.sprite.Sprite.__init__(self)

        # Images and animations
        # Images will be scaled to this size
        self.imageScale = (200,200)
        # path to the folder where dino images is stored
        self.imgFolder = imgFolder
        # dict of all loaded images
        self.images = {}
        self.masks = {}
        # Animation
        self.runImg = 1
        self.runImgCounter = 0
        # Load the images to self.images and masks to self.masks
        self.loadImages()
        # set default image
        self.image = self.images["dino"]
        self.mask = self.masks["dino"]

        # Rect
        self.rect = pygame.Rect(0,0,0,0)
        self.updateRectSize()

        # Pos
        self.rect.x = game.screenSize[0]//10
        self.rect.y = game.screenSize[1] - game.scene.groundSize[1]

        self.rect.y -= self.rect.width

        self.orgY = self.rect.y

        # Is self crouching?
        self.crouching = False

        # Jump control
        self.jumping = False
        # Jump physic vars
        self.mass = 0.2
        self.velocity = 20
        # Original jump physics
        self.jumpPower = self.velocity
        self.orgMass = self.mass
        # Jump stats
        self.jumps = 0 # How many times self has jumped
        # How many long self has jumped in one jump
        self.jumpTime = 100
        self.currentJumpTime = 0

        # Score
        self.score = 0

    # Blit correct image to surf
    def draw(self, surf):
        # Image

        # Jump image
        if self.rect.y < self.orgY:
            self.image = self.images["jump"]
            self.mask = self.masks["jump"]
        # If game not started: show normal dino image
        elif self.jumps == 0:
            self.image = self.images["dino"]
            self.mask = self.masks["dino"]
        # Run animation
        else:
            # img 1 or 2
            if self.runImg == 1:
                # Crouch or run img 1
                if not self.crouching:
                    self.image = self.images["dinoRun1"]
                    self.mask = self.masks["dinoRun1"]
                else:
                    self.image = self.images["dinoCrouchRun1"]
                    self.mask = self.masks["dinoCrouchRun1"]
            else:
                # Crouch or run img 2
                if not self.crouching:
                    self.image = self.images["dinoRun2"]
                    self.mask = self.masks["dinoRun2"]
                else:
                    self.image = self.images["dinoCrouchRun2"]
                    self.mask = self.masks["dinoCrouchRun2"]

            # Shift images
            if self.runImgCounter >= 5:
                self.runImgCounter = 0
                if self.runImg == 1: self.runImg = 2
                else: self.runImg = 1

            self.updateRectSize()
            self.runImgCounter += 1
        
        surf.blit(self.image, (self.rect.x, self.rect.y))

    def updateRectSize(self):
        self.rect.width = self.image.get_width()
        self.rect.height = self.image.get_height()

    def jump(self, speed, delta):
        if self.jumping:

            self.currentJumpTime += 1

            # Jump physics
            self.force = ((1 / 2) * self.mass * (self.velocity**2)) * speed

            self.rect.y -= self.force

            self.velocity -= speed

            if self.velocity < 0:
                self.mass = -self.orgMass
            
            # End jump
            if self.velocity <= -(self.jumpPower+1):

                self.jumping = False

                self.velocity = self.jumpPower
                self.mass = self.orgMass
                self.rect.y = self.orgY

                self.jumpTime = self.currentJumpTime
                self.currentJumpTime = 0

    def checkForEvents(self):
        # Get pressed keys
        self.kPressed = pygame.key.get_pressed()
        # Jum?
        if self.kPressed[pygame.K_SPACE] or self.kPressed[pygame.K_UP]:
            if self.jumping != True: self.jumps += 1
            self.jumping = True
        # Update self.crouching
        if self.kPressed[pygame.K_DOWN]: self.crouching = True
        else: self.crouching = False

    def loadImages(self):
        self.imagesNames = []
        
        for (dirpath, dirnames, filenames) in walk(self.imgFolder):
            self.imagesNames.extend(filenames)
            break

        self.images = {}
        self.masks = {}
        for name in self.imagesNames:
            self.name = name.replace(".png", "")
            # Images
            self.images[self.name] = pygame.image.load(self.imgFolder + name).convert_alpha()
            self.images[self.name] = pygame.transform.scale(self.images[self.name], self.imageScale)
            # Masks
            self.masks[self.name] = pygame.mask.from_surface(self.images[self.name])

class Obstackle(pygame.sprite.Sprite):
    def __init__(self, img, game, width=100, height=100, obsType=0):

        pygame.sprite.Sprite.__init__(self)

        self.rect = pygame.Rect(0,0,0,0)

        # Set position
        self.rect.width = width
        self.rect.height = height

        self.rect.x = game.screenSize[0] + randint(0,500)
        self.rect.y = game.screenSize[1] - game.scene.groundSize[1] - self.rect.height
        if obsType == 1: # If bird
            self.rect.y = self.birdY(self.rect.y)

        self.obsType = obsType # 0 = cactus, 1 = bird
        # Load image
        self.loadImages("images\\obstackle")

        self.currentImage = 0
        self.timeToNextAniFrame = 10
        
        self.speed = 25

    # Blit image to surf
    def draw(self, surf):
        # Image
        surf.blit(self.images[self.currentImage], (self.rect.x, self.rect.y))
        # Animation
        if self.timeToNextAniFrame == 0:
            self.timeToNextAniFrame = 10
            if self.currentImage < len(self.images) - 1: self.currentImage += 1
            else: self.currentImage = 0
        else:
            self.timeToNextAniFrame -= 1

    # Generate bird y pos
    def birdY(self, normalY):
        self.birdHeights = [20, 140, 260]
        return normalY - self.birdHeights[randint(0,len(self.birdHeights)-1)]

    def move(self, gameSpeed=1):
        # Move
        self.rect.x -= self.speed * gameSpeed

    def isOut(self):
        # Check if self has moved outside the screen
        if self.rect.x < 0 - self.rect.width:
            return True

    def checkCollision(self, sprite):
        self.image = self.images[self.currentImage]
        return pygame.sprite.collide_mask(self, sprite)

    def loadImages(self, obstackleImageFolder):
        self.imgDirs = []
        self.imagesNames = []
        
        for (dirpath, dirnames, filenames) in walk(obstackleImageFolder):
            self.imgDirs.extend(dirnames)
            break

        self.imgFolder = obstackleImageFolder + "\\" + self.imgDirs[self.obsType]

        for (dirpath, dirnames, filenames) in walk(self.imgFolder):
            self.imagesNames.extend(filenames)
            break

        self.images = []
        self.masks = []
        for name in self.imagesNames:
            # Images
            self.images.append(pygame.image.load(self.imgFolder + "\\" + name).convert_alpha())
            self.i = len(self.images)-1
            self.images[self.i] = pygame.transform.scale(self.images[self.i], (self.rect.width, self.rect.height))
            # Masks
            self.masks.append(pygame.mask.from_surface(self.images[self.i]))

class Scene:
    def __init__(self, groundSize = [1000,100], surfSize = [1000, 500], groundColor = [255,255,90]):
        self.groundSize = groundSize
        self.groundColor = groundColor

        self.sun = Sun(surfSize=surfSize)
        self.deco = Decoration(surfSize, groundSize)

        self.night = self.sun.isNight

        self.font = pygame.font.SysFont("sans serif", 50)
        self.highscore = data.get_playerdata()["high"]

        self.skyColor = {
            "day":(66, 135, 245),
            "night":(0,0,50)
        }

    def draw(self, surf, gameSpeed=1):
        # Draw the sky
        surf.fill(self.skyColor["night"] if self.night else self.skyColor["day"])
        # Night sky decoration
        if self.night:
            self.deco.drawNightSky(surf)
        # Day sky decoration
        else:
            self.deco.drawDaySky(surf)
        # Draw the sun
        self.sun.draw(surf)
        self.sun.move()
        self.night = True if self.sun.isNight else False
        # Draw the ground rect
        pygame.draw.rect(surf, self.groundColor, pygame.Rect(0, surf.get_height() - self.groundSize[1], self.groundSize[0], self.groundSize[1]))
        # Draw ground deco
        self.deco.drawGround(surf, gameSpeed)

    def showScore(self, surf, score): # And highscore
        self.scoreText = self.font.render(f"Score: {score}", True, (255,255,255))
        surf.blit(self.scoreText, (0,0))
        self.highScoreText = self.font.render(f"Highscore: {self.highscore}", True, (255,255,255))
        surf.blit(self.highScoreText, (0,self.scoreText.get_height()))

    def showFPS(self, surf, fps):
        self.fpsText = self.font.render(f"FPS: {str(int(fps))}", True, (255,255,255))
        surf.blit(self.fpsText, (surf.get_width()-self.fpsText.get_width(),0))

    def showStartText(self, surf):
        self.startText = self.font.render(f"Press space to start the game", True, (255,255,255))
        surf.blit(self.startText, (surf.get_width()//2-self.startText.get_width()//2, surf.get_height()//2 - self.startText.get_height()//2))

class Sun: # and moon
    def __init__(self, x = 0, radius = 50, surfSize = [1000,500]):
        # Planet size
        self.planetMiddle = [surfSize[0]//2,surfSize[1]]
        self.planetRadius = surfSize[0]//2
        self.planetSize = surfSize

        # Pos and size
        self.x = x
        self.y = self.calculateY()
        self.radius = radius

        self.isNight = False

        # Styling
        self.color = {
            "day":(255,255,0),
            "night":(200,200,200)
        }

    def draw(self, surf):
        pygame.draw.circle(surf, self.color["day"] if not self.isNight else self.color["night"], (self.x, self.y), self.radius)

    def calculateY(self):
        for i in range(self.planetSize[1]):
            if int(math.dist((self.x, i), self.planetMiddle)) == self.planetRadius:
                return i

    def move(self):
        self.x += 1
        if self.x > self.planetRadius*2:
            self.x = 0
            self.isNight = False if self.isNight else True
        self.y = self.calculateY()

class Decoration:
    def __init__(self, surfSize, groundSize, stars=250):
        self.surfSize = surfSize
        self.groundSize = groundSize

        self.starAmount = stars # The amount of stars to generate and draw.

        self.stars = []

        self.generateStars()

    # Star stuff
    def generateStars(self):
        for _ in range(self.starAmount):
            self.stars.append(Star(randint(0,self.surfSize[0]), randint(0,self.surfSize[1]-self.groundSize[1]), randint(1,4)))

    # Draw night sky decorations
    def drawNightSky(self, surf):
        # Draw stars
        for star in self.stars:
            star.draw(surf)

    # Draw day sky decorations
    def drawDaySky(self, surf):
        pass

    # Stone stuff
    def drawGround(self, surf, gameSpeed=1):
        pass

class decoCircle:
    def __init__(self, x, y, size, color):
        self.x = x
        self.y = y
        self.size = size
        self.color = color

    def draw(self, surf):
        pygame.draw.circle(surf, self.color, (self.x, self.y), self.size)

class Star(decoCircle):
    def __init__(self, x, y, size, color=(255,255,255)):
        super().__init__(x, y, size, color)

class PauseMenu:
    def __init__(self, setGameCodeFunc, screenSize, unPauseFunc):

        self.screenSize = screenSize

        self.mPressed = False
        # Set game stopcode
        self.setGameCode = setGameCodeFunc
        # Unpause game
        self.unPause = unPauseFunc

        self.text = []
        self.buttons = []

        self.text.append(Text(screenSize[0]//2, screenSize[1]//2-200, "Menu!", (255,255,255))) # Header

        self.buttons.append(Button(screenSize[0]//2-125, screenSize[1]//2-100, 250, 100, "Continue", (255,255,255), lambda obj=None: self.unPause(), 1)) # Continue game
        self.buttons.append(Button(screenSize[0]//2-125, screenSize[1]//2, 250, 100, "Main menu", (255,255,255), lambda obj=None: self.setGameCode("menu"), 1)) # Return to main menu
        self.buttons.append(Button(screenSize[0]//2-125, screenSize[1]//2+100, 250, 100, "Quit", (255,255,255), lambda obj=None: self.setGameCode("close"), 1)) # Quit the game

    def show(self, surface):
        # Draw
        for text in self.text:
            text.draw(surface)
        for button in self.buttons:
            button.draw(surface)

    def getInput(self):
        if pygame.mouse.get_pressed()[0]: self.mPressed = True
        else:
            if self.mPressed:
                self.mPressed = False

                for button in self.buttons:
                    if button.getRect().collidepoint(pygame.mouse.get_pos()):
                        if button.codeType == 0:
                            self.stopCode = button.onClick()
                        else:
                            button.onClick()
