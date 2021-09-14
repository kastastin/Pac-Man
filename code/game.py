import sys, pygame
from settings import *
from pacman import *
from ghost import *
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
        # self.generateLevel()
        self.generateTxtFile()
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


### GENERATE LEVEL ###################################################


    def generateLevel(self):
        rows, columns = 14, 7
        horizontalWalls = [["ww"] * rows + ['ww'] for i in range(columns + 1)]
        verticalWalls = [["wp"] * rows + ['ww'] for i in range(columns)]
        checkedSquares = [[0] * rows + [1] for i in range(columns)] + [[1] * (rows + 1)]
        def step(x, y):
            checkedSquares[y][x] = 1
            directions = [(x - 1, y), (x, y + 1), (x + 1, y), (x, y - 1)]
            shuffle(directions) # перемешать список
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
        for (a, b) in zip(horizontalWalls, verticalWalls):
            data += ''.join(a + ['\n'] + b + ['\n'])
        reversedData = data[::-1]
        data = data + reversedData.lstrip()
        data = data[:560] + 'U' + data[560+1:]
        data = data[:35] + '2' + data[35+1:]
        data = data[:36] + '3' + data[36+1:]
        data = data[:37] + '4' + data[37+1:]
        data = data[:38] + '5' + data[38+1:]
        with open("generator.txt", 'w') as txtFile:
            txtFile.write(data)


######################################################





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
            self.typeSearch = 'No'
        # if self.typeSearch == 'BFS':
        #     self.typeSearch = 'DFS'
        # if self.typeSearch == 'DFS':
        #     self.typeSearch = ''

    def gameDisplay(self):
        self.screen.fill(GAME_BACKGROUND_COLOUR)
        self.screen.blit(self.background, (INDENT // 2, INDENT // 2))
        self.displayLines()
        self.displayWalls()


        

        # for ghost in self.ghosts:
        #     if self.typeSearch == 'BFS':
        #         self.showBFS(self.BFS([int(self.Pacman.gridCoordinate.x), int(self.Pacman.gridCoordinate.y)], [int(ghost.gridCoordinate.x), int(ghost.gridCoordinate.y)]))
        #     elif self.typeSearch == 'DFS':
        #         self.showDFS(self.DFS([int(self.Pacman.gridCoordinate.x), int(self.Pacman.gridCoordinate.y)], [int(ghost.gridCoordinate.x), int(ghost.gridCoordinate.y)]))

        # to 1 ghost
        if self.typeSearch == 'BFS':
            timeStartBFS = time()
            self.showBFS(self.BFS([int(self.Pacman.gridCoordinate.x), int(self.Pacman.gridCoordinate.y)], [int(self.ghosts[0].gridCoordinate.x), int(self.ghosts[0].gridCoordinate.y)]))
            timeEndBFS = time()
            self.speedSearch = timeEndBFS - timeStartBFS
        elif self.typeSearch == 'DFS':
            timeStartDFS = time()
            self.showDFS(self.DFS([int(self.Pacman.gridCoordinate.x), int(self.Pacman.gridCoordinate.y)], [int(self.ghosts[0].gridCoordinate.x), int(self.ghosts[0].gridCoordinate.y)]))
            timeEndDFS = time()
            self.speedSearch = timeEndDFS - timeStartDFS


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


### BFS ##########################################################################


    def BFS(self, start, target):
        rows, columns = ROWS, COLUMNS
        squares = [[0 for x in range(rows)] for x in range(columns)]
        for wall in self.walls:
            if wall.x < rows and wall.y < columns:
                squares[int(wall.y)][int(wall.x)] = 1
        queue = [start]
        way, visitedSquares = [], []
        while queue:
            currentQueueItem = queue[0]
            queue.remove(queue[0])
            visitedSquares.append(currentQueueItem)
            if currentQueueItem == target:
                break;
            else:
                neighbours = [[0, -1], [1, 0], [0, 1], [-1, 0]]
                for neighbour in neighbours:
                    if neighbour[0] + currentQueueItem[0] >= 0 and neighbour[0] + currentQueueItem[0] < len(squares):
                        if neighbour[1] + currentQueueItem[1] >= 0 and neighbour[1] + currentQueueItem[1] < len(squares):
                            nextCell = [neighbour[0] + currentQueueItem[0], neighbour[1] + currentQueueItem[1]]
                            if nextCell not in visitedSquares:
                                if squares[nextCell[1]][nextCell[0]] != 1:
                                    queue.append(nextCell)
                                    way.append({"Current": currentQueueItem, "Next": nextCell})
        shortest = [target]
        while target != start:
            for step in way:
                if step["Next"] == target:
                    target = step["Current"]
                    shortest.insert(0, step["Current"])
        return shortest

    def showBFS(self, arr):
        for cell in arr:
            pygame.draw.rect(self.screen, BFS_COLOUR, (cell[0] * SQUARE_WIDTH + HALF_INDENT, cell[1] * SQUARE_HEIGHT + HALF_INDENT, SQUARE_WIDTH, SQUARE_HEIGHT), 5)


### DFS ##########################################################################

    def DFS(self, start, target):
        grid = [[0 for x in range(30)] for x in range(30)]
        for cell in self.walls:
            if cell.x < 30 and cell.y < 30:
                grid[int(cell.y)][int(cell.x)] = 1

        visited = []
        path = []
        fringe = PriorityQueue()
        fringe.put((0, start, path, visited))

        while not fringe.empty():
            depth, current, path, visited = fringe.get()

            if current == target:
                return path + [current]

            visited = visited + [current]
            neighbours = [[0, -1], [1, 0], [0, 1], [-1, 0]]
            for neighbour in neighbours:
                if neighbour[0]+current[0] >= 0 and neighbour[0] + current[0] < len(grid[0]):
                    if neighbour[1]+current[1] >= 0 and neighbour[1] + current[1] < len(grid):
                        next_cell = [neighbour[0] + current[0], neighbour[1] + current[1]]
                        if next_cell not in visited:
                            if next_cell == target:
                                return path + [next_cell]
                            if grid[next_cell[1]][next_cell[0]] != 1:
                                depth_of_node = len(path)
                                fringe.put((-depth_of_node, next_cell, path + [next_cell], visited))

        return path

    def showDFS(self, arr):
        for cell in arr:
            pygame.draw.rect(self.screen, DFS_COLOUR, (cell[0] * SQUARE_WIDTH + HALF_INDENT, cell[1] * SQUARE_HEIGHT + HALF_INDENT, SQUARE_WIDTH, SQUARE_HEIGHT), 5)
    
    def replaceSignByIndex(self, str, index, sign):
        str = str[:index] + f'{sign}' + str[index + 1:]
        return str
    
    def generateTxtFile(self):
        data = ''
        for i in range(900):
            if len(data) % 31 == 0:
                data += '\n'
            else:
                data += 'w'
        data = data.replace('\n', 'w' * 30 + '\n', 1)


        coordsWithoutBorder = []
        for y in range(32, 897, 31):
            for x in range(y, y + 28):
                data = self.replaceSignByIndex(data, x, 'p')
                coordsWithoutBorder.append(x)
        

        def getRandomCoord():
            return choice(coordsWithoutBorder)

        startRandomCoordinates = []
        for i in range(35):
            startRandomCoordinates.append(getRandomCoord())
            data = self.replaceSignByIndex(data, startRandomCoordinates[i], 'w')
            if startRandomCoordinates[i] + 1 in coordsWithoutBorder:
                data = self.replaceSignByIndex(data, startRandomCoordinates[i] + 1, 'w')
            if startRandomCoordinates[i] + 3 in coordsWithoutBorder:
                data = self.replaceSignByIndex(data, startRandomCoordinates[i] + 3, 'w')
            if startRandomCoordinates[i] + 5 in coordsWithoutBorder:
                data = self.replaceSignByIndex(data, startRandomCoordinates[i] + 5, 'w')
            if startRandomCoordinates[i] - 1 in coordsWithoutBorder:
                data = self.replaceSignByIndex(data, startRandomCoordinates[i] - 1, 'w')
            if startRandomCoordinates[i] - 3 in coordsWithoutBorder:
                data = self.replaceSignByIndex(data, startRandomCoordinates[i] - 3, 'w')
            if startRandomCoordinates[i] - 5 in coordsWithoutBorder:
                data = self.replaceSignByIndex(data, startRandomCoordinates[i] - 5, 'w')
            # if startRandomCoordinates[i] - 31 in coordsWithoutBorder:
            #     data = self.replaceSignByIndex(data, startRandomCoordinates[i] - 31, 'w')
            # if startRandomCoordinates[i] - 62 in coordsWithoutBorder:
            #     data = self.replaceSignByIndex(data, startRandomCoordinates[i] - 62, 'w')
            # if startRandomCoordinates[i] + 31 in coordsWithoutBorder:
            #     data = self.replaceSignByIndex(data, startRandomCoordinates[i] + 31, 'w')
                

        

        data = self.replaceSignByIndex(data, 883, 'U')
        data = self.replaceSignByIndex(data, 71, '2')
        data = self.replaceSignByIndex(data, 73, '3')
        data = self.replaceSignByIndex(data, 75, '4')
        data = self.replaceSignByIndex(data, 78, '5')

        with open("generator.txt", 'w') as txtFile:
                txtFile.write(data)




pygame.init()
game = Game()
game.launchGame()