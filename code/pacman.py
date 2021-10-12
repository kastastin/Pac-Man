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
        self.lives = 3
        self.score = 0
        self.target = None
        self.aStar = Astar(None, None)

    
#################### Get pixel co-rds ####################


    def getPixelCoordinate(self):
        return vector((self.gridCoordinate[0] * SQUARE_WIDTH) + HALF_INDENT + SQUARE_WIDTH // 2, (self.gridCoordinate[1] * SQUARE_HEIGHT) + HALF_INDENT + SQUARE_HEIGHT // 2)


#################### UPDATE ####################


    def updatePacman(self):
        self.target = self.setTarget()
        if self.target != self.gridCoordinate:
            self.pixelCoordinate += self.direction * 2
            if self.score % 10 == 0:
                random.shuffle(self.game.points)
            if self.isTimeToMove():
                self.move()

        self.gridCoordinate[0] = (self.pixelCoordinate[0]- INDENT + SQUARE_WIDTH//2)//SQUARE_WIDTH+1
        self.gridCoordinate[1] = (self.pixelCoordinate[1]- INDENT + SQUARE_HEIGHT//2)//SQUARE_HEIGHT+1
        if self.onPoint():
            self.takePoint()


#################### ... ####################


    def setTarget(self):
        return self.game.points[0]

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
        nextSquare = self.getNextSquare(target)
        x = nextSquare[1] - self.gridCoordinate[0]
        y = nextSquare[0] - self.gridCoordinate[1]
        return vector(x, y)

    def getNextSquare(self, target):
        map = [[0 for x in range(30)] for x in range(30)] #27/29
        for step in self.game.walls:
            if step[0] < 30 and step[1] < 30: #27/29
                map[int(step[1])][int(step[0])] = 1
        path = self.aStar.astar(map, (int(self.gridCoordinate[1]), int(self.gridCoordinate[0])), (int(target[1]), int(target[0])))
        return path[1]

    def onPoint(self): 
        if self.gridCoordinate in self.game.points:
            if self.direction == vector(1, 0) or self.direction == vector(-1, 0):
                return True
            if self.direction == vector(0, 1) or self.direction == vector(0, -1) or self.direction == vector(0, 0):
                return True
        return False

    def takePoint(self):
        self.game.points.remove(self.gridCoordinate)
        self.score += 1
        if len(self.game.points) == 0:
            self.game.state = 'next'


#################### DISPLAY ####################


    def displayPacman(self):
        self.playerImage = pygame.image.load('img/pacman.png')
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


####################  A*  #################### 


class Astar:
    def __init__(self, beforeCoordinate, coordinate):
        self.beforeCoordinate = beforeCoordinate
        self.coordinate = coordinate
        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.coordinate == other.coordinate

    def astar(self, field, start, end):
        indexList = []
        nodeList = []

        currentStage = 0
        neighbours = ((0, -1), (0, 1), (-1, 0), (1, 0))
        maxStage = (len(field) // 2) ** 2

        endSearch = Astar(None, end)
        startSearch = Astar(None, start)
        startSearch.g = startSearch.h = startSearch.f = 0
        endSearch.g = endSearch.h = endSearch.f = 0
        indexList.append(startSearch)

        while len(indexList) > 0:
            currentStage += 1
            currentNode = indexList[0]
            currentIndex = 0

            for index, item in enumerate(indexList):
                if item.f < currentNode.f:
                    currentNode = item
                    currentIndex = index
                    
            if currentStage > maxStage:
                path = []
                current = currentNode
                
                while current is not None:
                    path.append(current.coordinate)
                    current = current.beforeCoordinate
                return path[::-1] 

            indexList.pop(currentIndex)
            nodeList.append(currentNode)

            if currentNode == endSearch:
                path = []
                current = currentNode
                
                while current is not None:
                    path.append(current.coordinate)
                    current = current.beforeCoordinate
                return path[::-1]

            children = []

            for next in neighbours:
                currenNodeCoordinate = (currentNode.coordinate[0] + next[0], currentNode.coordinate[1] + next[1])

                inGraph = [currenNodeCoordinate[0] > (len(field) - 1), currenNodeCoordinate[0] < 0, currenNodeCoordinate[1] > (len(field[len(field) - 1]) - 1), currenNodeCoordinate[1] < 0]
                
                if any(inGraph):
                    continue
                if field[currenNodeCoordinate[0]][currenNodeCoordinate[1]] != 0:
                    continue

                newSearch = Astar(currentNode, currenNodeCoordinate)

                children.append(newSearch)

            for child in children:
                if len([nodeChild for nodeChild in nodeList if nodeChild == child]) > 0:
                    continue

                child.g = currentNode.g + 1
                child.h = ((child.coordinate[0] - endSearch.coordinate[0]) ** 2) + ((child.coordinate[1] - endSearch.coordinate[1]) ** 2)
                child.f = child.g + child.h

                if len([indexChild for indexChild in indexList if child == indexChild and child.g > indexChild.g]) > 0:
                    continue

                indexList.append(child)