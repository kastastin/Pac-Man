import pygame, random
from settings import *
from pygame.math import Vector2 as vec 

class Ghost:
    def __init__(self, game, position):
        self.game = game
        self.gridCoordinate = position
        self.type = type
        self.direction = vec(0, 0)
        self.pixelCoordinate = self.getPixelCoordinate()
        self.startingCoordinate = [position.x, position.y]
        self.target = None

    def getPixelCoordinate(self):
        return vec((self.gridCoordinate.x * SQUARE_WIDTH) + HALF_INDENT + SQUARE_WIDTH // 2, (self.gridCoordinate.y * SQUARE_HEIGHT) + HALF_INDENT + SQUARE_HEIGHT // 2)

    def updateGhost(self):
        self.target = self.game.Pacman.gridCoordinate
        if self.target != self.gridCoordinate:   
            self.pixelCoordinate += self.direction
            if self.isTimeToMove():
                self.move()
        self.gridCoordsToPixelCoords()

    # set grid position in reference to pixel position
    def gridCoordsToPixelCoords(self):
        self.gridCoordinate[0] = (self.pixelCoordinate[0] - INDENT + SQUARE_WIDTH // 2) // SQUARE_WIDTH + 1
        self.gridCoordinate[1] = (self.pixelCoordinate[1] - INDENT + SQUARE_HEIGHT // 2) // SQUARE_HEIGHT + 1

    def displayGhost(self):
        self.playerImage = pygame.image.load('ghost.png')
        self.playerImage = pygame.transform.scale(self.playerImage, (SQUARE_WIDTH, SQUARE_HEIGHT))
        self.game.screen.blit(self.playerImage, (int(self.pixelCoordinate.x - INDENT // 5),int(self.pixelCoordinate.y - INDENT // 5)))    

    def isTimeToMove(self):
        if int(self.pixelCoordinate.x + INDENT // 2) % SQUARE_WIDTH == 0:
            if self.direction == vec(1, 0) or self.direction == vec(-1, 0) or self.direction == vec(0, 0):
                return True
        if int(self.pixelCoordinate.y + INDENT // 2) % SQUARE_HEIGHT == 0:
            if self.direction == vec(0, 1) or self.direction == vec(0, -1) or self.direction == vec(0, 0):
                return True
        return False

    def move(self):
        self.direction = self.getRandomDirection()

    def getRandomDirection(self):
        while True:
            randomDigit = random.randint(0, 4) 
            if randomDigit == 0:
                x, y = 1, 0
            elif randomDigit == 1:
                x, y = 0, 1
            elif randomDigit == 2:
                x, y = -1, 0
            else:
                x, y = 0, -1

            nextCoordinate = vec(self.gridCoordinate.x + x, self.gridCoordinate.y + y)
            if nextCoordinate not in self.game.walls:
                break
        return vec(x, y)