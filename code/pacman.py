import pygame
from settings import *
from pygame.math import Vector2 as vec 

class Pacman:
    def __init__(self, game, position):
        self.game = game
        self.gridCoordinate = position
        self.startingCoordinate = [position.x, position.y]
        self.pixelCoordinate = self.getPixelCoordinate() #vec
        self.direction = vec(0, 0) # vec
        self.isAbleToMove = True
        self.lives = 3
        self.score = 0
        self.savedDirection = None

    def updatePacman(self):
        if self.isAbleToMove:
            self.pixelCoordinate += self.direction * 2
        if self.isTimeToMove():
            if self.savedDirection != None:
                self.direction = self.savedDirection
            self.isAbleToMove = self.canMove()
        self.gridCoordsToPixelCoords()
        if self.onPoint():
            self.takePoint()
    
    # set grid position in reference to pixel position
    def gridCoordsToPixelCoords(self):
        self.gridCoordinate[0] = (self.pixelCoordinate[0] + SQUARE_WIDTH // 2 - INDENT) // SQUARE_WIDTH + 1
        self.gridCoordinate[1] = (self.pixelCoordinate[1] + SQUARE_HEIGHT // 2 - INDENT) // SQUARE_HEIGHT + 1

    def displayPacman(self):
        self.playerImage = pygame.image.load('img/pacman.png')
        if self.direction == vec(0, -1):
            self.playerImage = pygame.transform.rotate(self.playerImage, 90)
        if self.direction == vec(0, 1):
            self.playerImage = pygame.transform.rotate(self.playerImage, -90)
        if self.direction == vec(-1, 0):
            self.playerImage = pygame.transform.flip(self.playerImage, 1, 0)
        
        self.playerImage = pygame.transform.scale(self.playerImage, (SQUARE_WIDTH, SQUARE_HEIGHT))
        self.game.screen.blit(self.playerImage, (int(self.pixelCoordinate.x - INDENT // 5),int(self.pixelCoordinate.y - INDENT // 5)))


    def displayLives(self):
        for x in range(self.lives):
            self.game.screen.blit(self.playerImage, (30 + 20 * x, WINDOW_HEIGHT - 23))

    def onPoint(self): 
        if self.gridCoordinate in self.game.points:
            if int(self.pixelCoordinate.x + INDENT // 2) % SQUARE_WIDTH == 0:
                if self.direction == vec(1, 0) or self.direction == vec(-1, 0):
                    return True
            if int(self.pixelCoordinate.y + INDENT // 2) % SQUARE_HEIGHT == 0:
                if self.direction == vec(0, 1) or self.direction == vec(0, -1):
                    return True
        return False

    def takePoint(self):
        self.game.points.remove(self.gridCoordinate)
        self.score += 1
        if len(self.game.points) == 0:
            self.game.state = 'next'

    def move(self, direction):
        self.savedDirection = direction

    def getPixelCoordinate(self):
        return vec((self.gridCoordinate[0] * SQUARE_WIDTH) + HALF_INDENT + SQUARE_WIDTH // 2, (self.gridCoordinate[1] * SQUARE_HEIGHT) + HALF_INDENT + SQUARE_HEIGHT // 2)

    def isTimeToMove(self):
        if int(self.pixelCoordinate.x + HALF_INDENT) % SQUARE_WIDTH == 0:
            if self.direction == vec(1, 0) or self.direction == vec(-1, 0) or self.direction == vec(0, 0):
                return True
        if int(self.pixelCoordinate.y + HALF_INDENT) % SQUARE_HEIGHT == 0:
            if self.direction == vec(0, 1) or self.direction == vec(0, -1) or self.direction == vec(0, 0):
                return True

    def canMove(self):
        for wall in self.game.walls:
            if vec(self.gridCoordinate + self.direction) == wall:
                return False
        return True