import sys, pygame, random, skimage
from pygame.math import Vector2 as vector
from settings import *
from pacman import *
from ghost import *
from agent import *


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.agent = Agent()
        self.last_reward = 0
        self.last_best_result = 0
        self.record = 0
        self.Lose = True
        self.clock = pygame.time.Clock()
        self.isLaunching = True
        self.state = 'game'
        self.walls = []
        self.points = []
        self.ghosts = []
        self.ghostCoordinates = []
        self.pacmanCoordinate = None
        self.generateLevel()

        self.Pacman = Pacman(self, vector(self.pacmanCoordinate))
        self.createGhosts()

    def get_state(self):
        image = skimage.color.rgb2gray(pygame.surfarray.array3d(pygame.display.get_surface()))
        image = skimage.transform.resize(image, (28, 30))
        return np.array(image).flatten()


#################### Generate Level ####################


    def generateLevel(self):
        self.setBackground()
        self.readTxt()

    def setBackground(self):
        self.background = pygame.image.load('../img/gameBackground.jpg')
        self.background = pygame.transform.scale(self.background, (MAP_WIDTH, MAP_HEIGHT))

    def readTxt(self):
        with open("../maze.txt", 'r') as file:
            self.saveVectors(file)
    
    def saveVectors(self, file): 
        for y, line in enumerate(file):
            for x, sign in enumerate(line):
                if sign == "w":
                    self.walls.append(vector(x, y))
                elif sign == "p":
                    self.points.append(vector(x, y))
                elif sign == "U":
                    self.pacmanCoordinate = [x, y]
                elif sign in ["2", "3", "4", "5"]:
                    self.ghostCoordinates.append([x, y])


#################### Create Ghosts ####################


    def createGhosts(self):
        for ghost, position in enumerate(self.ghostCoordinates):
            self.ghosts.append(Ghost(self, vector(position), ghost))


#################### Reset Game ####################
    

    def resetGame(self):
        self.Lose = True
        self.walls = []
        self.points = []    
        self.Pacman.score = 0    
        self.resetPacman()
        self.resetGhosts()
        self.generateLevel() 
        self.state = "game"      

    def resetPacman(self, isReset = True):
        if isReset:
            self.Pacman.lives = 3
        self.Pacman.gridCoordinate = vector(self.Pacman.startingCoordinate)
        self.Pacman.pixelCoordinate = self.Pacman.getPixelCoordinate()
        self.Pacman.direction *= 0
        self.pacmanCoordinate = None

    def resetGhosts(self):
        self.ghostCoordinates = []
        for ghost in self.ghosts:
            ghost.gridCoordinate = vector(ghost.startingCoordinate)
            ghost.pixelCoordinate = ghost.getPixelCoordinate()
            ghost.direction *= 0
            
  
#################### Menu state ####################


    def menuEvents(self):
        for event in pygame.event.get():
            self.closeByEsc(event)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.state = 'game'

    def menuDisplay(self):
        self.screen.fill(MENU_BACKGROUND_COLOUR)
        self.displayText(PLAY_AGAIN_TEXT, self.screen, [WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - INDENT], menu_TEXT_SIZE, MENU_TEXT_COLOUR, menu_FONT, centered = True)
        self.displayText(EXIT_TEXT, self.screen, [WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + INDENT], menu_TEXT_SIZE, MENU_TEXT_COLOUR, menu_FONT, centered = True)
        pygame.display.update()


#################### Game state ####################


    def gameEvents(self):
        self.closeGame()
                    
    def gameUpdate(self, direction):


        cur_score = self.Pacman.score
        cur_lives = self.Pacman.lives

        self.Pacman.updatePacman(direction)
        for ghost in self.ghosts:
            ghost.updateGhost()
            if ghost.gridCoordinate == self.Pacman.gridCoordinate:
                self.deleteLife()

        reward = 0
        if cur_score < self.Pacman.score:
            reward = 1
        if cur_lives > self.Pacman.lives:
            reward = -1

        return reward, self.Lose, self.Pacman.score

        
                        
    def gameDisplay(self):
        self.screen.fill(GAME_BACKGROUND_COLOUR)
        self.screen.blit(self.background, (HALF_INDENT, HALF_INDENT))
        self.displayText(f'SCORE: {self.Pacman.score}', self.screen, [280, 0], 18, SCORE_COLOUR, menu_FONT)
        self.displayLines()
        self.displayWalls()
        self.displayPoints()
        self.Pacman.displayPacman()
        self.Pacman.displayLives()
        for ghost in self.ghosts:
            ghost.displayGhost()
        pygame.display.update()        


#################### Result state ####################


    def resultEvents(self):
        for event in pygame.event.get():
            self.closeByEsc(event)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.resetGame()

    def resultDisplay(self):
        self.screen.fill(RESULT_BACKGROUND_COLOUR)
        self.displayText("You lose", self.screen, [WINDOW_WIDTH//2, 100],  52, RESULT_TEXT_COLOUR, "arial", True)
        self.displayText(PLAY_AGAIN_TEXT, self.screen, [WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2],  36, RESULT_COLOUR, "arial", True)
        self.displayText(EXIT_TEXT, self.screen, [WINDOW_WIDTH // 2, WINDOW_HEIGHT // 1.5],  36, RESULT_COLOUR, "arial", True)
        pygame.display.update()


#################### Next state ####################


    def nextEvents(self):
        for event in pygame.event.get():
            self.closeByEsc(event)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.resetGame()

    def nextDraw(self):
        self.screen.fill(RESULT_BACKGROUND_COLOUR)
        self.displayText("Level passed", self.screen, [WINDOW_WIDTH//2, 100],  52, RESULT_TEXT_COLOUR, "arial", True)
        self.displayText(PLAY_NEXT_LEVEL_TEXT, self.screen, [WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2],  36, RESULT_COLOUR, "arial", True)
        self.displayText(EXIT_TEXT, self.screen, [WINDOW_WIDTH // 2, WINDOW_HEIGHT // 1.5],  36, RESULT_COLOUR, "arial", True)
        pygame.display.update()


#################### Delete Life ####################


    def deleteLife(self):
        self.Pacman.lives -= 1
        if self.Pacman.lives == 0:
            self.Lose = False
        else:
            self.resetPacman(False)
            self.resetGhosts()


#################### Display ####################
        

    def displayLines(self):
        for x in range(X_LINE):
            pygame.draw.line(self.background, LINES_COLOUR, (x * SQUARE_WIDTH, 0), (x * SQUARE_WIDTH, WINDOW_HEIGHT))
        for y in range(Y_LINE):
            pygame.draw.line(self.background, LINES_COLOUR, (0, y * SQUARE_HEIGHT), (WINDOW_WIDTH, y * SQUARE_HEIGHT))

    def displayWalls(self):
        for wall in self.walls:
            pygame.draw.rect(self.background, WALL_COLOUR, (wall.x * SQUARE_WIDTH, wall.y * SQUARE_HEIGHT, SQUARE_WIDTH, SQUARE_HEIGHT))

    def displayPoints(self):
        for point in self.points:
            pygame.draw.circle(self.screen, POINT_COLOUR, (int(point.x * SQUARE_WIDTH) + SQUARE_WIDTH // 2 + HALF_INDENT, int(point.y * SQUARE_HEIGHT) + SQUARE_HEIGHT // 2 + HALF_INDENT), 5)

    def displayText(self, words, screen, position, size, colour, fontName, centered = False):
        font = pygame.font.SysFont(fontName, size)
        text = font.render(words, False, colour)
        textSize = text.get_size()
        if centered:
            position[0] = position[0] - textSize[0] // 2
            position[1] = position[1] - textSize[1] // 2
        screen.blit(text, position)


#################### Close Game ####################


    def closeGame(self):
        for event in pygame.event.get():
            self.closeByEsc(event)
    
    def closeByEsc(self, event):
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.isLaunching = False


#################### Launch Game ####################


    def launchGame(self):
        while self.isLaunching:
            if self.state == 'game':
                self.gameEvents()
                self.gameDisplay()
                self.state_old = self.get_state()

                self.final_move = self.agent.get_action(self.state_old)

                reward, game_over, score = self.gameUpdate(self.final_move)

                state_new = self.get_state()

                self.agent.train_short_memory(self.state_old, self.final_move, reward, state_new, game_over)

                self.agent.remember(self.state_old, self.final_move, reward, state_new, game_over)

                if game_over == False:
                    
                    self.agent.n_games += 1
                    self.agent.train_long_memory()
                    if score > self.record:
                        self.record = score
                        self.agent.model.save()
                    self.resetGame()
                    print("Game", self.agent.n_games, 'Score', score, 'Record', self.record)    
            elif self.state == 'result':
                self.resultEvents()
                self.resultDisplay()
            elif self.state == 'next':
                self.nextEvents()
                self.nextDraw()
            else:
                self.isLaunching = False
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit() 


pygame.init()
game = Game().launchGame()