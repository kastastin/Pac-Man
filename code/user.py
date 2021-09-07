import pygame
from settings import *
from pygame.math import Vector2 as vec 

class User:
    def __init__(self, app, position):
        self.app = app
        self.gridPosition = position
        self.startingPosition = [position.x, position.y]
        self.pixelPosition = self.getPixelPosition() #vec
        self.direction = vec(0, 0) # vec
        self.isAbleToMove = True
        self.speed = 2
        self.lives = 3
        self.currentScore = 0
        self.bestScore = 0
        self.savedDirection = None

    def update(self):
        if self.isAbleToMove:
            self.pixelPosition += self.direction * self.speed
        
        if self.isTimeToMove():
            if self.savedDirection != None:
                self.direction = self.savedDirection
            self.isAbleToMove = self.canMove()

        # set grid position in reference to pixel position
        self.gridPosition[0] = (self.pixelPosition[0] + self.app.cellWidth // 2 - INDENT) // self.app.cellWidth + 1
        self.gridPosition[1] = (self.pixelPosition[1] + self.app.cellHeight // 2 - INDENT) // self.app.cellHeight + 1

        if self.onPoint():
            self.takePoint()


    def draw(self):
        pygame.draw.circle(self.app.screen, USER_COLOUR, (int(self.pixelPosition.x), int(self.pixelPosition.y)), self.app.cellWidth // 2 - 2)

        # draw lives
        for x in range(self.lives):
            pygame.draw.circle(self.app.screen, USER_COLOUR, (30 + 20 * x, HEIGHT - 15), 7)

    def onPoint(self): 
        if self.gridPosition in self.app.points:
            if int(self.pixelPosition.x + INDENT // 2) % self.app.cellWidth == 0:
                if self.direction == vec(1, 0) or self.direction == vec(-1, 0):
                    return True
            if int(self.pixelPosition.y + INDENT//2) % self.app.cellHeight == 0:
                if self.direction == vec(0, 1) or self.direction == vec(0, -1):
                    return True
        return False

    def takePoint(self):
        self.app.points.remove(self.gridPosition)
        self.currentScore += 1

    def move(self, direction):
        self.savedDirection = direction

    def getPixelPosition(self):
        return vec((self.gridPosition[0] * self.app.cellWidth) + INDENT // 2 + self.app.cellWidth // 2, (self.gridPosition[1] * self.app.cellHeight) + INDENT // 2 + self.app.cellHeight // 2)

    def isTimeToMove(self):
        if int(self.pixelPosition.x + INDENT // 2) % self.app.cellWidth == 0:
            if self.direction == vec(1, 0) or self.direction == vec(-1, 0) or self.direction == vec(0, 0):
                return True
        if int(self.pixelPosition.y + INDENT//2) % self.app.cellHeight == 0:
            if self.direction == vec(0, 1) or self.direction == vec(0, -1) or self.direction == vec(0, 0):
                return True

    def canMove(self):
        for wall in self.app.walls:
            if vec(self.gridPosition + self.direction) == wall:
                return False
        return True