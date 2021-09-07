import pygame, random
from settings import *
from pygame.math import Vector2 as vec 

class mob:
    def __init__(self, app, position, number):
        self.app = app
        self.gridPosition = position
        self.number = number
        self.direction = vec(0, 0)
        self.pixelPosition = self.getPixelPosition()
        self.startingPosition = [position.x, position.y]
        self.radius = int(self.app.cellWidth // 2.3)
        self.colour = self.setColour()
        self.target = None

    def update(self):
        self.target = self.app.user.gridPosition
        if self.target != self.gridPosition:   
            self.pixelPosition += self.direction
            if self.isTimeToMove():
                self.move()

        # set grid position in reference to pixel position
        self.gridPosition[0] = (self.pixelPosition[0] - INDENT + self.app.cellWidth // 2) // self.app.cellWidth + 1
        self.gridPosition[1] = (self.pixelPosition[1] - INDENT + self.app.cellHeight // 2) // self.app.cellHeight + 1

    def draw(self):
        pygame.draw.circle(self.app.screen, self.colour, (int(self.pixelPosition.x), int(self.pixelPosition.y)), self.radius)        

    def isTimeToMove(self):
        if int(self.pixelPosition.x + INDENT // 2) % self.app.cellWidth == 0:
            if self.direction == vec(1, 0) or self.direction == vec(-1, 0) or self.direction == vec(0, 0):
                return True
        if int(self.pixelPosition.y + INDENT // 2) % self.app.cellHeight == 0:
            if self.direction == vec(0, 1) or self.direction == vec(0, -1) or self.direction == vec(0, 0):
                return True
        return False

    def move(self):
        self.direction = self.getRandomDirection()

    def getRandomDirection(self):
        while True:
            number = random.randint(0, 4) 
            if number == 0:
                xDirection, yDirection = 1, 0
            elif number == 1:
                xDirection, yDirection = 0, 1
            elif number == 2:
                xDirection, yDirection = -1, 0
            else:
                xDirection, yDirection = 0, -1

            nextPosition = vec(self.gridPosition.x + xDirection, self.gridPosition.y + yDirection)
            if nextPosition not in self.app.walls:
                break
        return vec(xDirection, yDirection)

    def getPixelPosition(self):
        return vec((self.gridPosition.x * self.app.cellWidth) + INDENT // 2 + self.app.cellWidth // 2, (self.gridPosition.y * self.app.cellHeight) + INDENT // 2 + self.app.cellHeight // 2)

    def setColour(self):
        if self.number == 0:
            return (43, 78, 203)
        if self.number == 1:
            return (197, 200, 27)
        if self.number == 2:
            return (189, 29, 29)
        if self.number == 3:
            return (215, 159, 33)