from pygame.math import Vector2 as vector
import sys, pygame, skimage
from diagram import plot
from settings import *
from pacman import *
from ghost import *
from agent import *


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.is_game_launched = True
        self.is_game_lost = True
        self.agent = Agent()
        self.walls, self.points, self.ghosts = [], [], []
        self.ghost_cords = []
        self.pacman_cord = None
        self.generateLevel()
        self.createGhosts()
        self.Pacman = Pacman(self, vector(self.pacman_cord))
        self.diagram_score = []
        self.diagram_average_score = []
        self.sum_score = 0
        self.best_score = 0

    
    def get_state(self):
        image = skimage.color.rgb2gray(pygame.surfarray.array3d(pygame.display.get_surface()))
        image = skimage.transform.resize(image, (30, 30))
        return np.array(image).flatten()
        

    ##############  Run Game  ##############


    def run_game(self):
        
        while self.is_game_launched:
            self.clock.tick(FPS)
            self.exit_by_esc()
            self.gameDisplay()

            state = self.get_state()
            direction = self.agent.get_direction(state)
            reward, is_game_running, score = self.gameUpdate(direction)
            new_state = self.get_state()
            self.agent.train_short_memory(state, direction, reward, new_state, is_game_running)
            self.agent.remember(state, direction, reward, new_state, is_game_running)

            if is_game_running == False:
                self.agent.number_of_games += 1
                self.agent.train_long_memory()
    
                if score > self.best_score:
                    self.best_score = score
                    self.agent.model.save()
                    
                print("Game", self.agent.number_of_games, 'Score', score, 'Best Score', self.best_score)    
                self.diagram_score.append(score)
                self.sum_score += score
                mean_score = self.sum_score / self.agent.number_of_games
                self.diagram_average_score.append(mean_score)
                plot(self.diagram_score, self.diagram_average_score)

                self.resetGame()
                

        pygame.quit()
        sys.exit() 


    ###########  Generate Level  ###########


    def generateLevel(self):
        self.background = pygame.image.load('../img/gameBackground.jpg')
        self.background = pygame.transform.scale(self.background, (MAP_WIDTH, MAP_HEIGHT))
        
        with open("../maze.txt", 'r') as file:
            for y, line in enumerate(file):
                for x, sign in enumerate(line):
                    if sign == "w":
                        self.walls.append(vector(x, y))
                    elif sign == "p":
                        self.points.append(vector(x, y))
                    elif sign == "U":
                        self.pacman_cord = [x, y]
                    elif sign in ["1", "2", "3", "4"]:
                        self.ghost_cords.append([x, y])


    ###########  Create Ghosts  ############


    def createGhosts(self):
        for ghost, position in enumerate(self.ghost_cords):
            self.ghosts.append(Ghost(self, vector(position), ghost))


    #############  Reset Game  #############
    

    def resetGame(self):
        self.is_game_lost = True
        self.walls = []
        self.points = []    
        self.Pacman.score = 0    
        self.resetPacman()
        self.resetGhosts()
        self.generateLevel() 

    def resetPacman(self, isReset = True):
        if isReset:
            self.Pacman.lives = 1
        self.Pacman.gridCoordinate = vector(self.Pacman.startingCoordinate)
        self.Pacman.pixelCoordinate = self.Pacman.getPixelCoordinate()
        self.Pacman.direction *= 0
        self.pacman_cord = None

    def resetGhosts(self):
        self.ghost_cords = []
        for ghost in self.ghosts:
            ghost.gridCoordinate = vector(ghost.startingCoordinate)
            ghost.pixelCoordinate = ghost.getPixelCoordinate()
            ghost.direction *= 0


    ############  Game Update  ############


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

        return reward, self.is_game_lost, self.Pacman.score

        
    ############  Delete Life  ############


    def deleteLife(self):
        self.Pacman.lives -= 1
        if self.Pacman.lives == 0:
            self.is_game_lost = False
        else:
            self.resetPacman(False)
            self.resetGhosts()


    ##############  Display  ##############


    def gameDisplay(self):
        self.screen.fill(BACKGROUND_COLOR)
        self.screen.blit(self.background, (HALF_INDENT, HALF_INDENT))
        self.displayText(f'SCORE: {self.Pacman.score}', self.screen, [280, 0], 18, TEXT_COLOR, FONT)
        self.displayLines()
        self.displayWalls()
        self.displayPoints()
        self.Pacman.displayPacman()
        self.Pacman.displayLives()
        for ghost in self.ghosts:
            ghost.displayGhost()
        pygame.display.update()
        
    def displayLines(self):
        for x in range(X_LINE):
            pygame.draw.line(self.background, LINES_COLOR, (x * SQUARE_WIDTH, 0), (x * SQUARE_WIDTH, WINDOW_HEIGHT))
        for y in range(Y_LINE):
            pygame.draw.line(self.background, LINES_COLOR, (0, y * SQUARE_HEIGHT), (WINDOW_WIDTH, y * SQUARE_HEIGHT))

    def displayWalls(self):
        for wall in self.walls:
            pygame.draw.rect(self.background, WALL_COLOR, (wall.x * SQUARE_WIDTH, wall.y * SQUARE_HEIGHT, SQUARE_WIDTH, SQUARE_HEIGHT))

    def displayPoints(self):
        for point in self.points:
            pygame.draw.circle(self.screen, POINT_COLOR, (int(point.x * SQUARE_WIDTH) + SQUARE_WIDTH // 2 + HALF_INDENT, int(point.y * SQUARE_HEIGHT) + SQUARE_HEIGHT // 2 + HALF_INDENT), 5)

    def displayText(self, words, screen, position, size, colour, fontName, centered = False):
        font = pygame.font.SysFont(fontName, size)
        text = font.render(words, False, colour)
        textSize = text.get_size()
        if centered:
            position[0] = position[0] - textSize[0] // 2
            position[1] = position[1] - textSize[1] // 2
        screen.blit(text, position)


    #############  Close Game  #############


    def exit_by_esc(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.is_game_launched = False


pygame.init()
game = Game().run_game()