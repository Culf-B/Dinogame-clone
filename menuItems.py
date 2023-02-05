import pygame

pygame.init()

# Menu objects
class Menu:
    def __init__(self, res, fullscreen=True):

        # Setup pygame
        self.clock = pygame.time.Clock()

        self.stopCode = "idle"
        self.mPressed = False
        self.text = []
        self.buttons = []

        # Set screen size
        self.screenSize = res

    def updateText(self, textId, newText):
        for text in self.text:
            if text.id == textId: text.setText(newText)

    def loop(self):
        # Eventloop
        for event in pygame.event.get():
            # Use stopCode "close" to exit/close the program
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.stopCode = "close"

        # Mouse events
        if pygame.mouse.get_pressed()[0]:
            self.mPressed = True
        else:
            if self.mPressed:
                self.mPressed = False
                for button in self.buttons:
                    if button.getRect().collidepoint(pygame.mouse.get_pos()):
                        if button.codeType == 0:
                            self.stopCode = button.onClick()
                        else:
                            button.onClick()
        
        # Clear screen
        self.screen.fill((10,10,15))

        # Draw
        for text in self.text:
            text.draw(self.screen)
        for button in self.buttons:
            button.draw(self.screen)

        # Update display
        pygame.display.flip()
        self.clock.tick(60)

class Button:
    def __init__(self, x, y, width, height, text, color, code, codeType = 0, ID = "", other = {}):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.text = text

        self.codeType = codeType # If 0: button will return code as a stopcode to main, else: button will run code()
        self.code = code

        self.font = pygame.font.SysFont("sans serif", 50)
        self.color = color

        self.id = ID
        self.otherArgs = other

    def draw(self, surface):
        # Box
        pygame.draw.rect(surface, self.color, pygame.Rect(self.x,self.y,self.width,self.height),2)
    
        # Text
        self.renderedText = self.font.render(self.text, True, self.color)
        surface.blit(self.renderedText, self.centeredText(self.renderedText.get_width(), self.renderedText.get_height()))

    def centeredText(self, textWidth, textHeight):
        self.result = []
        self.result.append(self.x + self.width // 2 - textWidth // 2)
        self.result.append(self.y + self.height // 2 - textHeight // 2)
        return self.result

    def getRect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def onClick(self):
        if self.codeType == 0:
            return self.code
        else:
            self.code(self)

    def setText(self, text):
        self.text = text

class Text:
    def __init__(self, x, y, text, color=(0,0,0), ID=""):
        self.x = x
        self.y = y
        
        self.text = text
        self.color = color
        self.font = pygame.font.SysFont("sans serif", 50)
        self.id = ID

    def draw(self, surface):
        self.renderedText = self.font.render(self.text, True, self.color)
        surface.blit(self.renderedText, (self.centeredText(self.renderedText.get_width()), self.y))

    def centeredText(self, textWidth):
        return self.x - textWidth//2

    def setText(self, text):
        self.text = text
