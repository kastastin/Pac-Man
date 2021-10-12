import pygame
from pygame.math import Vector2 as vector
from settings import *
 

class Ghost:
    def __init__(self, game, position):
        self.game = game
        self.startingCoordinate = [position.x, position.y]
        self.gridCoordinate = position
        self.aStar = Astar(None, None)
        self.type = type
        self.direction = vector(0, 0)
        self.pixelCoordinate = self.getPixelCoordinate()
        
        self.target = None

    def getPixelCoordinate(self):
        return vector((self.gridCoordinate.x * SQUARE_WIDTH) + HALF_INDENT + SQUARE_WIDTH // 2, (self.gridCoordinate.y * SQUARE_HEIGHT) + HALF_INDENT + SQUARE_HEIGHT // 2)

    def updateGhost(self):
        self.target = self.set_target()
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
        self.playerImage = pygame.image.load('img/ghost.png')
        self.playerImage = pygame.transform.scale(self.playerImage, (SQUARE_WIDTH, SQUARE_HEIGHT))
        self.game.screen.blit(self.playerImage, (int(self.pixelCoordinate.x - INDENT // 5),int(self.pixelCoordinate.y - INDENT // 5)))    

    def isTimeToMove(self):
        if int(self.pixelCoordinate.x + INDENT // 2) % SQUARE_WIDTH == 0:
            if self.direction == vector(1, 0) or self.direction == vector(-1, 0) or self.direction == vector(0, 0):
                return True
        if int(self.pixelCoordinate.y + INDENT // 2) % SQUARE_HEIGHT == 0:
            if self.direction == vector(0, 1) or self.direction == vector(0, -1) or self.direction == vector(0, 0):
                return True
        return False

    def move(self):
        self.direction = self.get_path_direction(self.target)

    def set_target(self):
        return self.game.Pacman.gridCoordinate

    def get_path_direction(self, target):
        next_cell = self.find_next_cell_in_path(target)
        xdir = next_cell[1] - self.gridCoordinate[0]
        ydir = next_cell[0] - self.gridCoordinate[1]
        return vector(xdir, ydir)

    def find_next_cell_in_path(self, target):
        grid = [[0 for x in range(28)] for x in range(30)]
        for step in self.game.walls:
            if step[0] < 28 and step[1] < 30:
                grid[int(step[1])][int(step[0])] = 1
        path = self.aStar.astar(grid, (int(self.gridCoordinate[1]), int(self.gridCoordinate[0])), (int(target[1]), int(target[0])))
        return path[1]
################  A*  #################  

class Astar:
    def __init__(self, beforeCoordinate, coordinate):
        self.beforeCoordinate = beforeCoordinate
        self.coordinate = coordinate
        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.coordinate == other.coordinate

    def astar(self, grid, start, end):
        indexList = []
        nodeList = []

        currentStage = 0
        neighbours = ((0, -1), (0, 1), (-1, 0), (1, 0))
        maxStage = (len(grid) // 2) ** 2

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

                inGraph = [currenNodeCoordinate[0] > (len(grid) - 1), currenNodeCoordinate[0] < 0, currenNodeCoordinate[1] > (len(grid[len(grid) - 1]) - 1), currenNodeCoordinate[1] < 0]
                
                if any(inGraph):
                    continue
                if grid[currenNodeCoordinate[0]][currenNodeCoordinate[1]] != 0:
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