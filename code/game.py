import sys, pygame
from settings import *
from pacman import *
from ghost import *
from collections import deque 
from pygame.math import Vector2 as vec 
from random import shuffle, randrange
from queue import PriorityQueue
from time import time
from random import choice




class Game:
    def __init__(self):
        self.launching = True
        self.state = 'menu'
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.walls = []
        self.points = []
        self.ghosts = []
        self.ghostCoordinates = []
        self.pacmanCoordinate = None
        self.saveVectorsAllObjects()
        self.Pacman = Pacman(self, vec(self.pacmanCoordinate))
        self.createGhosts()
        self.typeSearch = 'No'
        self.speedSearch = 0.0
        

    def launchGame(self):
        while self.launching:
            if self.state == 'menu':
                self.menuEvents()
                self.menuDisplay()
            elif self.state == 'game':
                self.gameEvents()
                self.gameUpdate()
                self.gameDisplay()
            elif self.state == 'result':
                self.resultEvents()
                self.resultDisplay()
            elif self.state == 'next':
                self.nextEvents()
                self.nextDraw()
            else:
                self.launching = False
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

### HELPERS ###################################################################

    def saveVectorsAllObjects(self):
        self.background = pygame.image.load('img/gameBackground.jpg')
        self.background = pygame.transform.scale(self.background, (MAP_WIDTH, MAP_HEIGHT))
        self.generateLevel()
        # self.generateTxtFile()
        # walls list with co-ords of walls stored as vectors
        with open("generator.txt", 'r') as file:
            for yIndex, line in enumerate(file):
                for xIndex, sign in enumerate(line):
                    if sign == "w":
                        self.walls.append(vec(xIndex, yIndex))
                    elif sign == "p":
                        self.points.append(vec(xIndex, yIndex))
                    elif sign == "U":
                        self.pacmanCoordinate = [xIndex, yIndex]
                    elif sign in ["2", "3", "4", "5"]:
                        self.ghostCoordinates.append([xIndex, yIndex])

    def displayLines(self):
        for x in range(WINDOW_WIDTH // SQUARE_WIDTH):
            pygame.draw.line(self.background, LINES_COLOUR, (x * SQUARE_WIDTH, 0),
                             (x * SQUARE_WIDTH, WINDOW_HEIGHT))
        for y in range(WINDOW_HEIGHT // SQUARE_HEIGHT):
            pygame.draw.line(self.background, LINES_COLOUR, (0, y * SQUARE_HEIGHT),
                             (WINDOW_WIDTH, y * SQUARE_HEIGHT))

    def displayWalls(self):
        for wall in self.walls:
            pygame.draw.rect(self.background, GAME_WALLS_COLOUR, (wall.x * SQUARE_WIDTH, wall.y * SQUARE_HEIGHT, SQUARE_WIDTH, SQUARE_HEIGHT))

    def displayText(self, words, screen, position, size, colour, fontName, centered = False):
        font = pygame.font.SysFont(fontName, size)
        text = font.render(words, False, colour)
        textSize = text.get_size()
        if centered:
            position[0] = position[0] - textSize[0] // 2
            position[1] = position[1] - textSize[1] // 2
        # display text on screen
        screen.blit(text, position)

    def createGhosts(self):
        for index, position in enumerate(self.ghostCoordinates):
            self.ghosts.append(Ghost(self, vec(position)))

    def reboot(self):
        self.background = pygame.image.load('img/gameBackground.jpg')
        self.background = pygame.transform.scale(self.background, (MAP_WIDTH, MAP_HEIGHT))
        self.Pacman.lives = 3
        self.Pacman.gridCoordinate = vec(self.Pacman.startingCoordinate)
        self.Pacman.pixelCoordinate = self.Pacman.getPixelCoordinate()
        self.Pacman.direction *= 0
        for ghost in self.ghosts:
            ghost.gridCoordinate = vec(ghost.startingCoordinate)
            ghost.pixelCoordinate = ghost.getPixelCoordinate()
            ghost.direction *= 0

        self.walls = []
        self.points = []
        self.ghostCoordinates = []
        self.pacmanCoordinate = None
        self.generateLevel()
        with open("generator.txt", 'r') as file:
            for yIndex, line in enumerate(file):
                for xIndex, sign in enumerate(line):
                    if sign == "w":
                        self.walls.append(vec(xIndex, yIndex))
                    elif sign == "p":
                        self.points.append(vec(xIndex, yIndex))
                    elif sign == "U":
                        self.pacmanCoordinate = [xIndex, yIndex]
                    elif sign in ["2", "3", "4", "5"]:
                        self.ghostCoordinates.append([xIndex, yIndex])
        self.state = "game"


### GENERATOR ###################################################


    def generateLevel(self):
        rows, columns = 14, 7
        horizontalWalls = [["ww"] * rows + ['ww'] for i in range(columns + 1)] # [['ww'], ['ww'] x14]
                                                                               # [['ww'], ['ww'] x14]  | x8
        verticalWalls = [["wp"] * rows + ['ww'] for i in range(columns)]       # [['wp'], ['wp'], [ww]]
        checkedSquares = [[0] * rows + [1] for i in range(columns)] + [[1] * (rows + 1)] # 
        # print(horizontalWalls)
        def step(x, y):
            checkedSquares[y][x] = 1
            directions = [(x - 1, y), (x, y + 1), (x + 1, y), (x, y - 1)]
            shuffle(directions) # перемешка списка
            for (xIndex, yIndex) in directions:
                if checkedSquares[yIndex][xIndex]:
                    continue
                if yIndex == y:
                    verticalWalls[y][max(x, xIndex)] = 'pp'
                if xIndex == x:
                    horizontalWalls[max(y, yIndex)][x] = 'wp'
                step(xIndex, yIndex)
        step(0, 0)
        data = ''
        # сначало horizontalWalls 1 список, потом verticalWalls 1 список и в цикл
        for (a, b) in zip(horizontalWalls, verticalWalls):
            data += ''.join(a + ['\n'] + b + ['\n'])
        reversedData = data[::-1]
        data = data + reversedData.lstrip() # удалить пробелы
        data = data[:312] + 'U' + data[312+1:]
        data = data[:35] + '2' + data[35+1:]
        data = data[:36] + '3' + data[36+1:]
        data = data[:37] + '4' + data[37+1:]
        data = data[:38] + '5' + data[38+1:]
        with open("generator.txt", 'w') as txtFile:
            txtFile.write(data)


### MENU STATE #######################################################


    def menuEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.launching = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.state = 'game'

    def menuDisplay(self):
        self.screen.fill(MENU_BACKGROUND_COLOUR)
        self.displayText(PLAY_AGAIN_TEXT, self.screen, [
                       WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - INDENT], menu_TEXT_SIZE, MENU_TEXT_COLOUR, menu_FONT, centered = True)
        self.displayText(EXIT_TEXT, self.screen, [
                       WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + INDENT], menu_TEXT_SIZE, MENU_TEXT_COLOUR, menu_FONT, centered = True)
        pygame.display.update()


### GAME STATE ##################################################################


    def gameEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.launching = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.Pacman.move(vec(-1, 0))
                if event.key == pygame.K_RIGHT:
                    self.Pacman.move(vec(1, 0))
                if event.key == pygame.K_UP:
                    self.Pacman.move(vec(0, -1))
                if event.key == pygame.K_DOWN:
                    self.Pacman.move(vec(0, 1))
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.launching = False
                
                if event.type == pygame.KEYDOWN and event.key == pygame.K_z:
                    self.changeTypeSearch(self.typeSearch)
                    
    def gameUpdate(self):
        self.Pacman.updatePacman()
        for ghost in self.ghosts:
            ghost.updateGhost()
        for ghost in self.ghosts:
            if ghost.gridCoordinate == self.Pacman.gridCoordinate:
                self.deleteLife()

    def changeTypeSearch(self, type):
        if type == 'No':
            self.typeSearch = 'BFS'
        if type == 'BFS':
            self.typeSearch = 'DFS'
        if type == 'DFS':
            self.typeSearch = 'UCS'
        if type == 'UCS':
            self.typeSearch = 'No'
            
            

    def gameDisplay(self):
        self.screen.fill(GAME_BACKGROUND_COLOUR)
        self.screen.blit(self.background, (INDENT // 2, INDENT // 2))
        self.displayLines()
        self.displayWalls()

        
        # Path to all ghosts

        # if self.typeSearch == 'BFS':
        #     timeStartBFS = time()
        #     for ghost in self.ghosts:
        #         self.showAlgorithm(self.useAlgorithm([int(self.Pacman.gridCoordinate.x), int(self.Pacman.gridCoordinate.y)], [int(ghost.gridCoordinate.x), int(ghost.gridCoordinate.y)], 'BFS'), BFS_COLOUR)
        #     timeEndBFS = time()
        #     self.speedSearch = timeEndBFS - timeStartBFS

        # elif self.typeSearch == 'DFS':
        #     timeStartDFS = time()
        #     for ghost in self.ghosts:
        #         self.showAlgorithm(self.useAlgorithm([int(self.Pacman.gridCoordinate.x), int(self.Pacman.gridCoordinate.y)], [int(ghost.gridCoordinate.x), int(ghost.gridCoordinate.y)], 'DFS'), DFS_COLOUR)
        #     timeEndDFS = time()
        #     self.speedSearch = timeEndDFS - timeStartDFS

        # elif self.typeSearch == 'UCS':
        #     timeStartDFS = time()
        #     for ghost in self.ghosts:
        #         self.showUniform(self.useUniformCostSearch([int(self.Pacman.gridCoordinate.x), int(self.Pacman.gridCoordinate.y)], [int(ghost.gridCoordinate.x), int(ghost.gridCoordinate.y)]))
        #     timeEndDFS = time()
        #     self.speedSearch = timeEndDFS - timeStartDFS

        # Path to 1 ghost
        if self.typeSearch == 'BFS':
            timeStartBFS = time()
            self.showAlgorithm(self.useAlgorithm([int(self.Pacman.gridCoordinate.x), int(self.Pacman.gridCoordinate.y)], [int(self.ghosts[0].gridCoordinate.x), int(self.ghosts[0].gridCoordinate.y)], 'BFS'), BFS_COLOUR)
            timeEndBFS = time()
            self.speedSearch = timeEndBFS - timeStartBFS
        elif self.typeSearch == 'DFS':
            timeStartDFS = time()
            self.showAlgorithm(self.useAlgorithm([int(self.Pacman.gridCoordinate.x), int(self.Pacman.gridCoordinate.y)], [int(self.ghosts[0].gridCoordinate.x), int(self.ghosts[0].gridCoordinate.y)], 'DFS'), DFS_COLOUR)
            timeEndDFS = time()
            self.speedSearch = timeEndDFS - timeStartDFS
        elif self.typeSearch == 'UCS':
            timeStartBFS = time()
            self.showUniform(self.useUniformCostSearch([int(self.Pacman.gridCoordinate.x), int(self.Pacman.gridCoordinate.y)], [int(self.ghosts[0].gridCoordinate.x), int(self.ghosts[0].gridCoordinate.y)]))
            timeEndBFS = time()
            self.speedSearch = timeEndBFS - timeStartBFS




        self.draw_points()
        self.displayText(f'SCORE: {self.Pacman.score}',
                       self.screen, [280, 0], 18, GAME_SCORE_COLOUR, menu_FONT)
        self.Pacman.displayPacman()
        self.Pacman.displayLives()
        for ghost in self.ghosts:
            ghost.displayGhost()
        self.displayText(f'Time: {self.speedSearch}',
                       self.screen, [360, 645], 18, GAME_SCORE_COLOUR, menu_FONT)
        pygame.display.update()

    def deleteLife(self):
        self.Pacman.lives -= 1
        if self.Pacman.lives == 0:
            self.Pacman.score = 0
            self.state = "result"          
        else:
            # back to start Pacman position 
            self.Pacman.gridCoordinate = vec(self.Pacman.startingCoordinate)
            self.Pacman.pixelCoordinate = self.Pacman.getPixelCoordinate()
            self.Pacman.direction *= 0
            # back to start all ghosts
            for ghost in self.ghosts:
                ghost.gridCoordinate = vec(ghost.startingCoordinate)
                ghost.pixelCoordinate = ghost.getPixelCoordinate()
                ghost.direction *= 0

    def draw_points(self):
        for point in self.points:
            pygame.draw.circle(self.screen, GAME_POINT_COLOUR,
                               (int(point.x * SQUARE_WIDTH) + SQUARE_WIDTH // 2 + HALF_INDENT,
                                int(point.y * SQUARE_HEIGHT) + SQUARE_HEIGHT // 2 + HALF_INDENT), 5)


### RESULT STATE ################################################################


    def resultEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.launching = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.reboot()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.launching = False

    def resultDisplay(self):
        self.screen.fill(RESULT_BACKGROUND_COLOUR)
        self.displayText("You lose", self.screen, [WINDOW_WIDTH//2, 100],  52, RESULT_TEXT_COLOUR, "arial", centered = True)
        self.displayText(PLAY_AGAIN_TEXT, self.screen, [
                       WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2],  36, (190, 190, 190), "arial", centered = True)
        self.displayText(EXIT_TEXT, self.screen, [
                       WINDOW_WIDTH // 2, WINDOW_HEIGHT // 1.5],  36, (190, 190, 190), "arial", centered = True)
        pygame.display.update()


### NEXT STATE #########################################################################


    def nextEvents(self):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.launching = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self.reboot()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.launching = False

    def nextDraw(self):
        self.screen.fill(RESULT_BACKGROUND_COLOUR)
        self.displayText("Level passed", self.screen, [WINDOW_WIDTH//2, 100],  52, RESULT_TEXT_COLOUR, "arial", centered = True)
        self.displayText(PLAY_NEXT_LEVEL_TEXT, self.screen, [
                       WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2],  36, (190, 190, 190), "arial", centered = True)
        self.displayText(EXIT_TEXT, self.screen, [
                       WINDOW_WIDTH // 2, WINDOW_HEIGHT // 1.5],  36, (190, 190, 190), "arial", centered = True)
        pygame.display.update()


### BFS and DFS ##########################################################################


    def useAlgorithm(self, start, target, type):
        squares = [[0 for x in range(ROWS)] for x in range(COLUMNS)]  # [[0], [0], [0] x30]
        for wall in self.walls:
            if wall.x < ROWS and wall.y < COLUMNS:
                squares[int(wall.y)][int(wall.x)] = 1
        queue = [start]
        way, visitedSquares = [], []
        while queue:
            elementFromQueue = 0
            if type == 'DFS':
                elementFromQueue = len(queue) - 1
            # take first elem
            curQElement = queue[elementFromQueue]
            queue.remove(queue[elementFromQueue])
            visitedSquares.append(curQElement)
            if curQElement == target:
                break
            else:
                neighbours = [[0, -1], [1, 0], [0, 1], [-1, 0]]
                for neighbour in neighbours:
                    # проверка (следующая клетка в поле by х?)
                    if neighbour[0] + curQElement[0] >= 0 and neighbour[0] + curQElement[0] < len(squares):
                        # проверка (следующая клетка в поле? by y)
                        if neighbour[1] + curQElement[1] >= 0 and neighbour[1] + curQElement[1] < len(squares):
                            # записать next клетку
                            nextSquare = [neighbour[0] + curQElement[0], neighbour[1] + curQElement[1]]
                            # если еще не был
                            if nextSquare not in visitedSquares:
                                # если следующая клетка не стенка
                                if squares[nextSquare[1]][nextSquare[0]] != 1:
                                    queue.append(nextSquare)
                                    way.append({"Current": curQElement, "Next": nextSquare})
        shortest = [target]
        while target != start:
            for step in way:
                if step["Next"] == target:
                    target = step["Current"]
                    shortest.insert(0, step["Current"])
        return shortest

    def showAlgorithm(self, arr, color):
        for cell in arr:
            pygame.draw.rect(self.screen, color, (cell[0] * SQUARE_WIDTH + HALF_INDENT, cell[1] * SQUARE_HEIGHT + HALF_INDENT, SQUARE_WIDTH, SQUARE_HEIGHT), 5)


### Uniform Cost Search ##########################################################################


    def useUniformCostSearch(self, start, target):
        squares = [[0 for x in range(ROWS)] for x in range(COLUMNS)]
        visitedSquares = [[0 for x in range(ROWS)] for x in range(COLUMNS)]
        cost = [[0 for x in range(ROWS)] for x in range(COLUMNS)]
        for step in self.walls:
            if step[0] < 30 and step[1] < 30:
                squares[int(step[1])][int(step[0])] = 1

        paths = []

        for i in range(31 * 31):
            paths.append([0,0])
        queue = deque()
        bestWay = []
        bestCost = 100000 
        queue.append(start)
        while queue:
            current = queue.popleft() # получить 1 элемент и удалить с очереди
            currentCost = -1

            for point in self.points:
                # если текущая клетка в монетке
                if point[0] == current[0] and point[1] == current[1]:
                    currentCost -= 1

            if current[0] == target[0] and current[1] == target[1]:
                if bestCost > cost[current[1]][current[0]]:
                    bestCost = cost[current[1]][current[0]]
                    bestWay = []
                    needCoord = current
        
                    while needCoord[0] != start[0] or needCoord[1] != start[1]:
                        needCoord[0] = paths[needCoord[0] * 30 + needCoord[1]][0]
                        needCoord[1] = paths[needCoord[0] * 30 + needCoord[1]][1]
                        bestWay.append([needCoord[0], needCoord[1]])
                        
            neighbours = [[1, 0], [-1, 0], [0, -1], [0, 1]]
            for neighbour in neighbours:
                if neighbour[0] + current[0] >= 0 and visitedSquares[current[1]][neighbour[0] + current[0]] == 0 and neighbour[0] + current[0] < 30:
                        if squares[current[1]][neighbour[0] + current[0]] != 1:
                            paths[(neighbour[0] + current[0])*30 + current[1]] = [current[0], current[1]]
                            visitedSquares[current[1]][neighbour[0] + current[0]] = 1
                            cost[current[1]][neighbour[0] + current[0]] -= currentCost
                            queue.append([neighbour[0] + current[0], current[1]])
                elif neighbour[1] + current[1] >= 0 and visitedSquares[neighbour[1] + current[1]][current[0]] == 0 and neighbour[1] + current[1] < 30:
                        if squares[neighbour[1] + current[1]][current[0]] != 1:
                            paths[(current[0])*30 + neighbour[1] + current[1]] = [current[0], current[1]]
                            visitedSquares[neighbour[1] + current[1]][current[0]] = 1
                            cost[neighbour[1] + current[1]][current[0]] -= currentCost
                            queue.append([current[0], neighbour[1] + current[1]])
                
        return bestWay

    def showUniform(self, arr):
        for cell in arr:
            pygame.draw.rect(self.screen, UCS_COLOUR, (cell[0] * SQUARE_WIDTH + HALF_INDENT, cell[1] * SQUARE_HEIGHT + HALF_INDENT, SQUARE_WIDTH, SQUARE_HEIGHT), 5)
    

### GENERATOR #################################################################
    # def replaceSignByIndex(self, str, index, sign):
    #     str = str[:index] + f'{sign}' + str[index + 1:]
    #     return str
    
    # def generateTxtFile(self):
    #     data = ''
    #     for i in range(900):
    #         if len(data) % 31 == 0:
    #             data += '\n'
    #         else:
    #             data += 'w'
    #     data = data.replace('\n', 'w' * 30 + '\n', 1)


    #     coordsWithoutBorder = []
    #     for y in range(32, 897, 31):
    #         for x in range(y, y + 28):
    #             data = self.replaceSignByIndex(data, x, 'p')
    #             coordsWithoutBorder.append(x)
        

    #     def getRandomCoord():
    #         return choice(coordsWithoutBorder)

    #     startRandomCoordinates = []
    #     for i in range(35):
    #         startRandomCoordinates.append(getRandomCoord())
    #         data = self.replaceSignByIndex(data, startRandomCoordinates[i], 'w')
    #         if startRandomCoordinates[i] + 1 in coordsWithoutBorder:
    #             data = self.replaceSignByIndex(data, startRandomCoordinates[i] + 1, 'w')
    #         if startRandomCoordinates[i] + 3 in coordsWithoutBorder:
    #             data = self.replaceSignByIndex(data, startRandomCoordinates[i] + 3, 'w')
    #         if startRandomCoordinates[i] + 5 in coordsWithoutBorder:
    #             data = self.replaceSignByIndex(data, startRandomCoordinates[i] + 5, 'w')
    #         if startRandomCoordinates[i] - 1 in coordsWithoutBorder:
    #             data = self.replaceSignByIndex(data, startRandomCoordinates[i] - 1, 'w')
    #         if startRandomCoordinates[i] - 3 in coordsWithoutBorder:
    #             data = self.replaceSignByIndex(data, startRandomCoordinates[i] - 3, 'w')
    #         if startRandomCoordinates[i] - 5 in coordsWithoutBorder:
    #             data = self.replaceSignByIndex(data, startRandomCoordinates[i] - 5, 'w')
                
    #     data = self.replaceSignByIndex(data, 883, 'U')
    #     data = self.replaceSignByIndex(data, 71, '2')
    #     data = self.replaceSignByIndex(data, 73, '3')
    #     data = self.replaceSignByIndex(data, 75, '4')
    #     data = self.replaceSignByIndex(data, 78, '5')

    #     with open("generator.txt", 'w') as txtFile:
    #             txtFile.write(data)


pygame.init()
game = Game()
game.launchGame()