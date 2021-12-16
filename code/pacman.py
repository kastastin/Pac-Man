import pygame, random
from pygame.math import Vector2 as vector
from settings import *


class Pacman:
    def __init__(self, game, position):
        self.game = game
        self.startingCoordinate = [position.x, position.y]
        self.gridCoordinate = position
        self.pixelCoordinate = self.getPixelCoordinate() 
        self.direction = vector(0, 0)
        self.score = 0
        self.lives = 1
        self.speed = 10
        self.target = None

    
#################### Get pixel co-rds ####################


    def getPixelCoordinate(self):
        return vector((self.gridCoordinate[0] * SQUARE_WIDTH) + HALF_INDENT + SQUARE_WIDTH // 2, (self.gridCoordinate[1] * SQUARE_HEIGHT) + HALF_INDENT + SQUARE_HEIGHT // 2)


#################### UPDATE ####################

    
    def updatePacman(self, direction):
        self.target = direction
        if self.score != 2000:
            if self.isTimeToMove():
                self.move()
            self.pixelCoordinate += self.direction * self.speed

        self.gridCoordinate[0] = (self.pixelCoordinate[0]- INDENT + SQUARE_WIDTH // 2) // SQUARE_WIDTH + 1
        self.gridCoordinate[1] = (self.pixelCoordinate[1] - INDENT + SQUARE_HEIGHT // 2) // SQUARE_HEIGHT + 1
        if self.onPoint():
            self.takePoint()


#################### Move ####################


    def isTimeToMove(self):
        if int(self.pixelCoordinate.x + HALF_INDENT) % SQUARE_WIDTH == 0:
            if self.direction == vector(1, 0) or self.direction == vector(-1, 0) or self.direction == vector(0, 0):
                return True
        if int(self.pixelCoordinate.y + HALF_INDENT) % SQUARE_HEIGHT == 0:
            if self.direction == vector(0, 1) or self.direction == vector(0, -1) or self.direction == vector(0, 0):
                return True
        return False

    def move(self):
        self.direction = self.getPathDirection(self.target)

    def getPathDirection(self, target):
        xdir = 0
        ydir = 0
        if target[0] == 1:
            xdir = 1
            ydir = 0
        elif target[1] == 1:
            xdir = -1
            ydir = 0
        elif target[2] == 1:
            xdir = 0
            ydir = -1
        elif target[3] == 1:
            xdir = 0
            ydir = 1

        next_cell = [int(xdir + self.gridCoordinate[0]), int(ydir + self.gridCoordinate[1])]

        grid = [[0 for x in range(30)] for x in range(30)]
        for step in self.game.walls:
            if step[0] < 30 and step[1] < 30:
                grid[int(step[1])][int(step[0])] = 1
        if next_cell[0] < 30 and next_cell[1] < 30:
            if grid[next_cell[1]][next_cell[0]] != 1:
                return vector(xdir, ydir)
            else:
                return vector(0,0)
        else:
            return vector(0,0)

    def getNextSquare(self, target):
        map = [[0 for x in range(30)] for x in range(30)] #27/29
        for step in self.game.walls:
            if step[0] < 30 and step[1] < 30: #27/29
                map[int(step[1])][int(step[0])] = 1
                # changeeee minimax - expectimax
        path = self.minmax.makeMinimax(map, (int(self.gridCoordinate[1]), int(self.gridCoordinate[0])), (int(target[1]), int(target[0])))
        # path = self.Alg([int(self.gridCoordinate[0]), int(self.gridCoordinate[1])], [int(target[0]), int(target[1])])

        return path[1]

    def onPoint(self): 
        if self.gridCoordinate in self.game.points:
            if self.direction == vector(1, 0) or self.direction == vector(-1, 0):
                return True
            if self.direction == vector(0, 1) or self.direction == vector(0, -1) or self.direction == vector(0, 0):
                return True
        return False

    def takePoint(self):
        # random.shuffle(self.game.points)
        self.game.points.remove(self.gridCoordinate)
        self.score += 10
        # if len(self.game.points) == 0 or self.score == 80:
        if len(self.game.points) == 0 or self.score == 1000:
            self.game.is_game_lost = False
    


#################### DISPLAY ####################


    def displayPacman(self):
        self.playerImage = pygame.image.load('../img/pacman.png')
        if self.direction == vector(0, -1):
            self.playerImage = pygame.transform.rotate(self.playerImage, 90)
        if self.direction == vector(0, 1):
            self.playerImage = pygame.transform.rotate(self.playerImage, -90)
        if self.direction == vector(-1, 0):
            self.playerImage = pygame.transform.flip(self.playerImage, 1, 0)
        self.playerImage = pygame.transform.scale(self.playerImage, (SQUARE_WIDTH, SQUARE_HEIGHT))
        self.game.screen.blit(self.playerImage, (int(self.pixelCoordinate.x - INDENT // 5),int(self.pixelCoordinate.y - INDENT // 5)))

    def displayLives(self):
        for x in range(self.lives):
            self.game.screen.blit(self.playerImage, (30 + 20 * x, WINDOW_HEIGHT - 23))