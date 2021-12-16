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
        self.lives = 3
        self.speed = 10
        self.target = None
        self.minmax = Minimax(None, None)

    
#################### Get pixel co-rds ####################


    def getPixelCoordinate(self):
        return vector((self.gridCoordinate[0] * SQUARE_WIDTH) + HALF_INDENT + SQUARE_WIDTH // 2, (self.gridCoordinate[1] * SQUARE_HEIGHT) + HALF_INDENT + SQUARE_HEIGHT // 2)


#################### UPDATE ####################

    


    def updatePacman(self, direction):
        self.target = direction
        if self.score != 200:
            if self.isTimeToMove():
                self.move()
            self.pixelCoordinate += self.direction * self.speed

        self.gridCoordinate[0] = (self.pixelCoordinate[0]- INDENT + SQUARE_WIDTH // 2) // SQUARE_WIDTH + 1
        self.gridCoordinate[1] = (self.pixelCoordinate[1] - INDENT + SQUARE_HEIGHT // 2) // SQUARE_HEIGHT + 1
        if self.onPoint():
            self.takePoint()


#################### Move ####################


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
        self.score += 1
        # if len(self.game.points) == 0 or self.score == 80:
        if len(self.game.points) == 0 or self.score == 100:
            self.game.Lose = False
    


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

























    def Alg(self, start, target):
        map = [[0 for x in range(ROWS)] for x in range(COLUMNS)]  # [[0], [0], [0] x30]
        for wall in self.game.walls:
            if wall.x < ROWS and wall.y < COLUMNS:
                map[int(wall.y)][int(wall.x)] = 1
        queue = [start]
        path = []
        visited = []
        while queue:
            current = queue[0]
            queue.remove(queue[0])
            visited.append(current)
            if current == target:
                break
            else:
                neighbours = [[0, -1], [1, 0], [0, 1], [-1, 0]]
                for neighbour in neighbours:
                    if neighbour[0]+current[0] >= 0 and neighbour[0] + current[0] < len(map[0]):
                        if neighbour[1]+current[1] >= 0 and neighbour[1] + current[1] < len(map):
                            next_cell = [neighbour[0] + current[0], neighbour[1] + current[1]]
                            if next_cell not in visited:
                                if map[next_cell[1]][next_cell[0]] != 1:
                                    queue.append(next_cell)
                                    path.append({"Current": current, "Next": next_cell})
        shortest = [target]
        while target != start:
            for step in path:
                if step["Next"] == target:
                    target = step["Current"]
                    shortest.insert(0, step["Current"])
        return shortest



class Minimax:
    def __init__(self, parent, pos):
        self.parent = parent
        self.pos = pos
        self.f = 0   # общая стоимость пути
        self.g = 0   # стоимость между текущей и начальной вершиной
        self.h = 0   # эвристическая функция (Пифагора)

    def __eq__(self, other):
        return self.pos == other.pos

    def makeMinimax(self, field, firstTarget, lastTarget): # f = g + h (такой же как bfs, только юзаем эврестическую формулу и выбираем наименбшую f)
        uncheckedCoords = [] # непроверенные координаты
        checkedCoords = []   # проверенные координаты
        step = 0 # итерации
        neighbours = ((0, -1), (1, 0), (0, 1), (-1, 0))
        stepLimit = (len(field) // 2) ** 2 # формула
        firstTop = Minimax(None, firstTarget)
        firstTop.f = 0
        firstTop.g = 0
        firstTop.h = 0
        lastTop = Minimax(None, lastTarget)
        lastTop.f = 0
        lastTop.g = 0
        lastTop.h = 0
        uncheckedCoords.append(firstTop)

        while uncheckedCoords:
            step += 1 # 
            currChecked = uncheckedCoords[0]
            currUnchecked = 0

            for i, coord in enumerate(uncheckedCoords):
                if coord.f < currChecked.f:           # сравниваем значение f
                    currChecked = coord
                    currUnchecked = i 

            if step > stepLimit: # возвращаем путь, который нашли (с конца)
                path = []
                currTop = currChecked
                
                while currTop is not None:
                    path.append(currTop.pos)
                    currTop = currTop.parent
                return path[::-1] 

            uncheckedCoords.pop(currUnchecked)
            checkedCoords.append(currChecked)

            if currChecked == lastTop:
                path = []
                currTop = currChecked
                while currTop is not None:
                    path.append(currTop.pos)
                    currTop = currTop.parent
                return path[::-1]

            # генерация детей
            childrens = []

            for neighbour in neighbours:
                top = (currChecked.pos[0] + neighbour[0], currChecked.pos[1] + neighbour[1])

                isInRange = [
                    top[0] < 0,
                    top[1] < 0,
                    top[0] > (len(field) - 1),
                    top[1] > (len(field[len(field) - 1]) - 1)
                ]

                if any(isInRange): # если в графе
                    continue

                if field[top[0]][top[1]] != 0:
                    continue

                newTop = Minimax(currChecked, top)

                childrens.append(newTop)

            for child in childrens:
                if len([nodeChild for nodeChild in checkedCoords if nodeChild == child]) > 0:
                    continue

                child.g = currChecked.g + 1 # первая точка
                # теорема пифагора
                child.h = ((child.pos[0] - lastTop.pos[0]) ** 2) + ((child.pos[1] - lastTop.pos[1]) ** 2)
                child.f = child.g + child.h # child.g - точка, с которой начинаем обход

                if len([indexChild for indexChild in uncheckedCoords if child == indexChild and child.g > indexChild.g]) > 0: # ссравниваем типа f
                    continue

                uncheckedCoords.append(child)


    