import pygame, sys
from settings import *
from user import *
from mob import *
from pygame.math import Vector2 as vec 
import shelve

pygame.init()

class App:
    def __init__(self):
        self.running = True
        self.state = 'prime'
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.time = pygame.time.Clock()
        self.cellWidth = MAP_WIDTH // COLUMNS
        self.cellHeight = MAP_HEIGHT // ROWS
        self.walls = []
        self.points = []
        self.mobs = []
        self.mobPositions = []
        self.userPosition = None
        self.counterGames = 0
        self.load()
        self.user = User(self, vec(self.userPosition))
        self.createMobs()
        

    def run(self):
        while self.running:
            if self.state == 'prime':
                self.primeEvents()
                self.primeDraw()
            elif self.state == 'main':
                self.mainEvents()
                self.mainUpdate()
                self.mainDraw()
            elif self.state == 'losing':
                self.losingEvents()
                self.losingDraw()
            else:
                self.running = False
            self.time.tick(FPS)

        pygame.quit()
        sys.exit()

## HELPERS #########################################################

    def drawText(self, words, screen, position, size, colour, fontName, centered = False):
        font = pygame.font.SysFont(fontName, size)
        text = font.render(words, False, colour)
        textSize = text.get_size()
        if centered:
            position[0] = position[0] - textSize[0] // 2
            position[1] = position[1] - textSize[1] // 2
        # display text on screen
        screen.blit(text, position)

    def load(self):
        self.background = pygame.image.load('code/background.png')
        self.background = pygame.transform.scale(self.background, (MAP_WIDTH, MAP_HEIGHT))


        # walls list with co-ords of walls stored as vectors
        with open("code/walls.txt", 'r') as file:
            for yIndex, line in enumerate(file):
                for xIndex, sign in enumerate(line):
                    if sign == "w":
                        self.walls.append(vec(xIndex, yIndex))
                    elif sign == "p":
                        self.points.append(vec(xIndex, yIndex))
                    elif sign == "U":
                        self.userPosition = [xIndex, yIndex]
                    elif sign in ["2", "3", "4", "5"]:
                        self.mobPositions.append([xIndex, yIndex])
                    elif sign == "g":
                        pygame.draw.rect(self.background, BLACK, (xIndex * self.cellWidth, yIndex * self.cellHeight, self.cellWidth, self.cellHeight))

    def createMobs(self):
        for index, position in enumerate(self.mobPositions):
            self.mobs.append(mob(self, vec(position), index))

    def drawGrid(self):
        for x in range(WIDTH // self.cellWidth):
            pygame.draw.line(self.background, GREY, (x * self.cellWidth, 0),
                             (x * self.cellWidth, HEIGHT))
        for y in range(HEIGHT // self.cellHeight):
            pygame.draw.line(self.background, GREY, (0, y * self.cellHeight),
                             (WIDTH, y * self.cellHeight))

    def reboot(self):
        self.user.lives = 3
        self.user.currentScore = 0
        self.user.gridPosition = vec(self.user.startingPosition)
        self.user.pixelPosition = self.user.getPixelPosition()
        self.user.direction *= 0
        for mob in self.mobs:
            mob.gridPosition = vec(mob.startingPosition)
            mob.pixelPosition = mob.getPixelPosition()
            mob.direction *= 0

        self.points = []
        with open("code/walls.txt", 'r') as file:
            for yIndex, line in enumerate(file):
                for xIndex, sign in enumerate(line):
                    if sign == 'p':
                        self.points.append(vec(xIndex, yIndex))
        self.state = "main"


## PRIME #######################################################

    def primeEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.state = 'main'


    def primeDraw(self):
        self.screen.fill(BLACK)
        self.drawText('Press <enter> to start play', self.screen, [
                       WIDTH // 2, HEIGHT // 2 - INDENT], PRIME_TEXT_SIZE, (170, 132, 58), PRIME_FONT, centered = True)
        self.drawText('Press <esc> to exit game', self.screen, [
                       WIDTH // 2, HEIGHT // 2 + INDENT], PRIME_TEXT_SIZE, (44, 167, 198), PRIME_FONT, centered = True)
        pygame.display.update()

## MAIN ##########################################################

    def mainEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.user.move(vec(-1, 0))
                if event.key == pygame.K_RIGHT:
                    self.user.move(vec(1, 0))
                if event.key == pygame.K_UP:
                    self.user.move(vec(0, -1))
                if event.key == pygame.K_DOWN:
                    self.user.move(vec(0, 1))
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False


    def mainUpdate(self):
        self.user.update()
        for mob in self.mobs:
            mob.update()

        for mob in self.mobs:
            if mob.gridPosition == self.user.gridPosition:
                self.deleteLife()

    def mainDraw(self):
        self.drawGrid()
        self.screen.fill(BLACK)
        self.screen.blit(self.background, (INDENT // 2, INDENT // 2))
        self.draw_points()
        self.drawText(f'CURRENT SCORE: {self.user.currentScore}',
                       self.screen, [60, 0], 18, WHITE, PRIME_FONT)
        self.drawText(f'BEST SCORE: {self.user.bestScore}', self.screen, [WIDTH // 2 + 60, 0], 18, WHITE, PRIME_FONT)
        self.user.draw()
        for mob in self.mobs:
            mob.draw()
        pygame.display.update()

    def deleteLife(self):
        self.user.lives -= 1
        if self.user.lives == 0:
            self.counterGames += 1
            self.state = "losing"
            if self.user.currentScore > self.user.bestScore:
                self.user.bestScore = self.user.currentScore          

        else:
            # back to start user position 
            self.user.gridPosition = vec(self.user.startingPosition)
            self.user.pixelPosition = self.user.getPixelPosition()
            self.user.direction *= 0
            # back to start all mobs
            for mob in self.mobs:
                mob.gridPosition = vec(mob.startingPosition)
                mob.pixelPosition = mob.getPixelPosition()
                mob.direction *= 0

    def draw_points(self):
        for point in self.points:
            pygame.draw.circle(self.screen, POINT_COLOUR,
                               (int(point.x * self.cellWidth) + self.cellWidth // 2 + INDENT//2,
                                int(point.y * self.cellHeight) + self.cellHeight // 2 + INDENT // 2), 5)

## LOSING ################################################################

    def losingEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.reboot()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False

    def losingDraw(self):
        self.screen.fill(BLACK)
        exitText = "Press the escape button to exit"
        playAgainText = "Press SPACE bar to PLAY AGAIN"
        self.drawText("losing", self.screen, [WIDTH//2, 100],  52, RED, "arial", centered = True)
        self.drawText(playAgainText, self.screen, [
                       WIDTH // 2, HEIGHT // 2],  36, (190, 190, 190), "arial", centered = True)
        self.drawText(exitText, self.screen, [
                       WIDTH // 2, HEIGHT // 1.5],  36, (190, 190, 190), "arial", centered = True)
        self.drawText(f'Games over: {self.counterGames}', self.screen, [
                       WIDTH // 2, HEIGHT // 1.2],  36, (190, 190, 190), "arial", centered = True)
        pygame.display.update()


app = App()
app.run()