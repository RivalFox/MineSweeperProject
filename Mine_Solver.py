import pygame
from random import randrange
import time

"""GLOBAL VARIABLES"""

white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
dark_red = (200, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
grey = (127, 127, 127)

cellPixelWH = 50
borderWH = 2
width = 9
height = 9
mineCount = 10

lost = 0
won = 0
start_t = time.perf_counter()
total_t = 0

"""END OF GLOBAL VARIABLES"""

class Cell:
    mine = False
    clicked = False
    marked = False
    neighbourMines = 0
    
    #AI Parameters
    mineProbability = 0
    analyzed = False
    neighbourIndices = []
    

class Minesweeper:
    
    width = 10
    height = 10
    mineCount = 10
    flagCount = 10
    uncoveredCells = 0
    firstClick = True
    gameOver = False
    gameWon = False
    field = []
    last_clickedX = -1
    last_clickedY = -1
    
    #Constructor: Sets the number of cells in the game as width*height and the number of mines to be placed
    #NOTE: There must be at least 9 safe cells, i.e. (mineCount <= width*height-9) is imposed, because the first clicked cell and its immediate surrounding will be generated as "safe"
    def __init__(self, width, height, mineCount):
        self.width = width
        self.height = height
        self.mineCount = min(mineCount, width*height-9)
        self.flagCount = self.mineCount
        for x in range(width):
            self.field.append([])
            for y in range(height):
                self.field[x].append([])
                self.field[x][y] = Cell()
                             
    #Updates a given cell with the count of neighbouring mines
    def updateCellNeighbourCount(self, x, y):
        self.field[x][y].neighbourMines = self.getCellNeighbourMineCount(x, y)
            
    #Returns the tuples corresponding to each adjacent cell
    def getNeighbouringIndices(self, x, y):
        neighbours = []
        if x > 0:
            neighbours.append((x-1,y))
            if y > 0:
                neighbours.append((x-1,y-1))
            if y < ms.height - 1:
                neighbours.append((x-1,y+1))
        if y < ms.height - 1:
            neighbours.append((x,y+1))
        if y > 0:
            neighbours.append((x,y-1))
        if x < ms.width - 1:
            neighbours.append((x+1,y))
            if y > 0:
                neighbours.append((x+1,y-1))
            if y < ms.height - 1:
                neighbours.append((x+1,y+1))
        return neighbours
        
    #Counts the number of surrounding mines
    def getCellNeighbourMineCount(self, x, y):
        mines = 0
        if x > 0:
            if (self.field[x-1][y].mine):
                mines += 1
            if y > 0:
                if (self.field[x-1][y-1].mine):
                    mines += 1
            if y < self.height - 1:
                if (self.field[x-1][y+1].mine):
                    mines += 1
        if y < self.height - 1:
            if (self.field[x][y+1].mine):
                mines += 1
        if y > 0:
            if (self.field[x][y-1].mine):
                mines += 1
        if x < self.width - 1:
            if (self.field[x+1][y].mine):
                mines += 1
            if y > 0:
                if (self.field[x+1][y-1].mine):
                    mines += 1
            if y < self.height - 1:
                if (self.field[x+1][y+1].mine):
                    mines += 1
        return mines
    
    def getCellFromTuple(self, t):
        return self.field[t[0]][t[1]]
    
    #Resets the game state
    def resetField(self):
        self.flagCount = self.mineCount
        self.uncoveredCells = 0
        self.gameOver = False
        self.gameWon = False
        self.firstClick = True
        for x in range(self.width):
            for y in range(self.height):
                self.field[x][y].mine = False
                self.field[x][y].clicked = False
                self.field[x][y].marked = False
                self.field[x][y].neighbourMines = 0
                self.field[x][y].neighbourIndices = self.getNeighbouringIndices(x,y)
                self.field[x][y].mineProbability = 0
    
    #Generates the minefield, with no mine on safeX and safeY and one block radius surrounding it
    def generateField(self, safeX, safeY):
        minesToGenerate = self.mineCount
        while (minesToGenerate):
            x = randrange(self.width)
            y = randrange(self.height)
            if ((x != safeX) or (y != safeY)) and ((x != safeX-1) or (y != safeY)) and ((x != safeX-1) or (y != safeY-1)) and ((x != safeX-1) or (y != safeY+1)) and ((x != safeX) or (y != safeY+1)) and ((x != safeX) or (y != safeY-1)) and((x != safeX+1) or (y != safeY+1)) and ((x != safeX+1) or (y != safeY)) and ((x != safeX+1) or (y != safeY-1)) and self.field[x][y].mine == False:
            #if ((x != safeX) or (y != safeY)) and self.field[x][y].mine == False:
                self.field[x][y].mine = True
                minesToGenerate -= 1
        for x in range(self.width):
            for y in range(self.height):
                self.field[x][y].neighbourMines = self.getCellNeighbourMineCount(x, y)
                self.field[x][y].neighbourIndices = self.getNeighbouringIndices(x, y)
    
    #Sets a flag at the select location
    def setFlag(self, x, y):
        if (self.field[x][y].clicked) or (self.gameOver) or (self.gameWon):
            return
        if (not self.field[x][y].marked) and (self.flagCount > 0):
            self.field[x][y].marked = True
            self.flagCount -= 1
        elif (self.field[x][y].marked):
            self.field[x][y].marked = False
            self.flagCount += 1
    
    #Uncovers all surrounding fields that do not contain a mine
    #This is done via recursive calls of the click-method
    def uncoverNeighbours(self, x, y, ms_ai):
        if x > 0:
            if (not self.field[x-1][y].mine):
                self.click(x-1, y, ms_ai)
            if y > 0:
                if (not self.field[x-1][y-1].mine):
                    self.click(x-1, y-1, ms_ai)
            if y < self.height - 1:
                if (not self.field[x-1][y+1].mine):
                    self.click(x-1, y+1, ms_ai)
        if y < self.height - 1:
            if (not self.field[x][y+1].mine):
                self.click(x, y+1, ms_ai)
        if y > 0:
            if (not self.field[x][y-1].mine):
                self.click(x, y-1, ms_ai)
        if x < self.width - 1:
            if (not self.field[x+1][y].mine):
                self.click(x+1, y, ms_ai)
            if y > 0:
                if (not self.field[x+1][y-1].mine):
                    self.click(x+1, y-1, ms_ai)
            if y < self.height - 1:
                if (not self.field[x+1][y+1].mine):
                    self.click(x+1, y+1, ms_ai)
    
    #Clicks a field and updates the game state accordingly (explodes a mine if one is present, uncovers neighbours if there are no surrounding mines, etc)
    def click(self, x, y, ms_ai):
        if (self.gameOver) or (self.gameWon):
            return
        if (self.firstClick):
            self.generateField(x, y)
            self.firstClick = False
            self.click(x, y, ms_ai)
        elif (not self.field[x][y].clicked):
            self.field[x][y].clicked = True
            self.uncoveredCells += 1
            if self.field[x][y].mine:
                self.gameOver = True
            else:
                if (self.field[x][y].marked == True):
                    self.field[x][y].marked = False
                    self.flagCount += 1
                if (self.uncoveredCells == self.width*self.height - self.mineCount):
                    self.gameWon = True
                #The AI "shadows" the game, i.e. knowledge needs to be updated
                ms_ai.updateKnowledge(self, x, y)
                if (self.field[x][y].neighbourMines == 0):
                    self.uncoverNeighbours(x, y, ms_ai)       
        self.last_clickedX = x
        self.last_clickedY = y

class KnowledgeDatum:
    
    cells = []
    mineCount = 0
    x = -1
    y = -1

class Minesweeper_AI:
    
    knowledge = []
    guesses = 0
    moves = 0
    printKnowledge = False

    def __init__(self):
        pass
    
    def randomMove(self, ms):
        mv = (randrange(ms.width), randrange(ms.height))
        while ((ms.getCellFromTuple(mv).clicked) or (ms.getCellFromTuple(mv).mineProbability == 1)):
            mv = (randrange(ms.width), randrange(ms.height))
        return mv
    
    def contains(self, small, big):
        return set(small).issubset(set(big))
    
    def intersection(self, lst1, lst2): 
        return list(set(lst1) & set(lst2)) 
    
    def generateProbabilities(self, ms):
        flagsSet = (ms.mineCount-ms.flagCount)
        defaultProbability = (ms.flagCount) / (ms.width*ms.height-flagsSet-ms.uncoveredCells)
        for x in range(ms.width):
            for y in range(ms.height):
                ms.field[x][y].analyzed = False
                if ms.field[x][y].clicked:
                    #Cell is known to be safe
                    ms.field[x][y].mineProbability = 0
                elif not ms.field[x][y].mineProbability == 1:
                    #Cell is not already known to be a mine, probability can be overridden
                    ms.field[x][y].mineProbability = defaultProbability
        #Update by known cell neighbours
        for kd in self.knowledge:
            if (kd.cells != []):
                newProbability = kd.mineCount / len(kd.cells)
                for cell in kd.cells:
                    if (not ms.getCellFromTuple(cell).clicked) and (not ms.getCellFromTuple(cell).marked):
                        if (not ms.getCellFromTuple(cell).analyzed): #Cell will have defaultProbability assigned to it - can update
                            ms.getCellFromTuple(cell).mineProbability = newProbability
                            ms.getCellFromTuple(cell).analyzed = True
                        if (ms.getCellFromTuple(cell).analyzed) and (ms.getCellFromTuple(cell).mineProbability < newProbability): #Cell has been analyzed before, but a new lower bound is found
                            ms.getCellFromTuple(cell).mineProbability = newProbability
    
    #Returns the coordinate of the (non-clicked) cell with the lowest minimum mine probabilizy
    def getMinProbabilityCell(self, ms):
        minProb = 1
        cell = None
        for x in range(ms.width):
            for y in range(ms.height):
                if not ms.field[x][y].clicked:
                    if ms.field[x][y].mineProbability <= minProb:
                        cell = (x, y)
                        minProb = ms.field[x][y].mineProbability
        return cell
    
    def generateKnowledge(self, ms):
        pass           
    
    def move(self, ms):
        
        #Update the flags on the game board
        for x in range(ms.width):
            for y in range(ms.height):
                if ((ms.field[x][y].marked) and (ms.field[x][y].mineProbability < 1)) or (not (ms.field[x][y].marked) and (ms.field[x][y].mineProbability == 1)):
                    ms.setFlag(x,y)
                      
        if ms.firstClick:
            #Return a random move if it is the first click
            self.moves+=1
            return self.randomMove(ms)
        if ms.gameWon:
            #Nothing to do
            return

        #Check if any cells are known to be safe - if so, return such a cell
        for kd in self.knowledge:
            if (kd.mineCount == 0) and (len(kd.cells) > 0):
                self.moves+=1
                return kd.cells[0]
            
        #No known safe cell - choose cell with lowest (naive) probability estimate
        self.generateProbabilities(ms)
        cell = self.getMinProbabilityCell(ms)

        self.moves+=1
        self.guesses+=1
        return cell
    
    def updateKnowledge(self, ms, x, y):
        
        if (ms.field[x][y].clicked):
    
            #Initialize new knowledge datum
            kd = KnowledgeDatum()
            kd.mineCount = ms.field[x][y].neighbourMines
            kd.x = x
            kd.y = y
            
            #Keep track of which sets of knowledge are updated by revealing cell (x,y)
            updatedKnowledge = []
            if (not ms.field[x][y].mine):
                for kd2 in self.knowledge:
                    if ((x, y) in kd2.cells):
                        kd2.cells.remove((x,y))
                        updatedKnowledge.append(kd2)
                    
            if kd.mineCount == 0:
                return
            
            #The new knowledge datum can be trimmed by those cells that are already clicked
            kd.cells = ms.getNeighbouringIndices(x,y)
            for cell in ms.field[x][y].neighbourIndices:
                if ms.getCellFromTuple(cell).clicked:
                    kd.cells.remove(cell)
              
            self.knowledge.append(kd)

            #Add new knowledge items yielded via deduction from subsets
            newKnowledge = []
            for kd3 in updatedKnowledge:
                
                if len(kd3.cells) > 1:
                    for kd2 in self.knowledge:
                        if (kd2 != kd3):
                            if (len(kd2.cells) > 0) and self.contains(kd3.cells, kd2.cells):
                                newkd = KnowledgeDatum()
                                newkd.cells = [x for x in kd2.cells if x not in kd3.cells]
                                newkd.mineCount = kd2.mineCount - kd3.mineCount
                                newKnowledge.append(newkd)
            self.knowledge = self.knowledge + newKnowledge    
            
        
            #Update the probability of cells known to be mines to 1                
            for kd2 in self.knowledge:
                if len(kd2.cells) == kd2.mineCount : #all surrounding cells are mines
                    for cell in kd2.cells:
                        ms.getCellFromTuple(cell).mineProbability = 1
                            
            #Cells known to be mines should reduce the minecount of all sets they are contained in
            for x in range(ms.width):
                for y in range(ms.height):
                    if (ms.field[x][y].mineProbability == 1):
                        for kd2 in self.knowledge:
                            if (x,y) in kd2.cells:
                                kd2.cells.remove((x,y))
                                kd2.mineCount -= 1
        
#Takes a screen, font, and minesweeper instance and draws it. The font is needed for the number of surrounding mines
def drawMS(screen, font, ms):
    for x in range(ms.width):
        for y in range(ms.height):
            if ((ms.field[x][y].clicked) or (ms.gameOver)) and (ms.field[x][y].mine):
                if ms.last_clickedX == x and ms.last_clickedY == y:
                     pygame.draw.rect(screen, dark_red, (borderWH+(cellPixelWH+borderWH)*x,borderWH+(cellPixelWH+borderWH)*y,cellPixelWH,cellPixelWH), 0) 
                else:
                    pygame.draw.rect(screen, red, (borderWH+(cellPixelWH+borderWH)*x,borderWH+(cellPixelWH+borderWH)*y,cellPixelWH,cellPixelWH), 0) 
                if (ms.field[x][y].marked):
                    srf = font.render("!", True, white)
                    screen.blit(srf, ((borderWH+(cellPixelWH+borderWH)*x+cellPixelWH//2.5,borderWH+(cellPixelWH+borderWH)*y+cellPixelWH//4)))
            elif (ms.field[x][y].clicked) and (not ms.field[x][y].mine):
                pygame.draw.rect(screen, white, (borderWH+(cellPixelWH+borderWH)*x,borderWH+(cellPixelWH+borderWH)*y,cellPixelWH,cellPixelWH), 0) 
                font.render(str(ms.field[x][y].neighbourMines), True, blue)
                if ms.field[x][y].neighbourMines > 0:
                    srf = font.render(str(ms.field[x][y].neighbourMines), True, blue)
                    screen.blit(srf, ((borderWH+(cellPixelWH+borderWH)*x+cellPixelWH//2.5,borderWH+(cellPixelWH+borderWH)*y+cellPixelWH//4)))
            else:
                pygame.draw.rect(screen, black, (borderWH+(cellPixelWH+borderWH)*x,borderWH+(cellPixelWH+borderWH)*y,cellPixelWH,cellPixelWH), 0) 
                if (ms.field[x][y].marked):
                    srf = font.render("!", True, white)
                    screen.blit(srf, ((borderWH+(cellPixelWH+borderWH)*x+cellPixelWH//2.5,borderWH+(cellPixelWH+borderWH)*y+cellPixelWH//4)))

#Converts mouse coordinates to cell coordinates within the minefield
def mouseToField(x, y):
    fieldX = int(x / (cellPixelWH+borderWH))
    fieldY = int(y / (cellPixelWH+borderWH))
    return [fieldX, fieldY]
          
def printText(ms, ms_ai, font, screen):
    
    if (ms.gameOver):
        srf = font_text.render("BOOM - Game Over.", True, black)
        screen.blit(srf, ((ms.width*(cellPixelWH+borderWH)+borderWH+10,10)))
    elif (ms.gameWon):
        srf = font_text.render("Game Won!", True, black)
        screen.blit(srf, ((ms.width*(cellPixelWH+borderWH)+borderWH+10,10)))
    else:
        srf = font_text.render("Playing..", True, black)
        screen.blit(srf, ((ms.width*(cellPixelWH+borderWH)+borderWH+10,10)))
        
    srf = font_text.render("Flags: " + str(ms.flagCount), True, black)
    screen.blit(srf, ((ms.width*(cellPixelWH+borderWH)+borderWH+10,40)))
    
    srf = font_text.render("SESSION STATS", True, black)
    screen.blit(srf, ((ms.width*(cellPixelWH+borderWH)+borderWH+10,90)))
    srf = font_text.render("Games: "+ str(won+lost), True, black)
    screen.blit(srf, ((ms.width*(cellPixelWH+borderWH)+borderWH+10,110)))
    if (won+lost>0):
        percentage = round((won/(won+lost))*100,2)
    else:
        percentage = "-" 
    srf = font_text.render("Wins: "+ str(won) + ", "+str(percentage)+"%", True, black)
    screen.blit(srf, ((ms.width*(cellPixelWH+borderWH)+borderWH+10,130)))
    srf = font_text.render("Losses: "+ str(lost), True, black)
    screen.blit(srf, ((ms.width*(cellPixelWH+borderWH)+borderWH+10,150)))
    
    srf = font_text.render("AI STATS", True, black)
    screen.blit(srf, ((ms.width*(cellPixelWH+borderWH)+borderWH+10,200)))
    srf = font_text.render("Moves: "+ str(ms_ai.moves), True, black)
    screen.blit(srf, ((ms.width*(cellPixelWH+borderWH)+borderWH+10,220)))
    srf = font_text.render("Guesses: "+ str(ms_ai.guesses), True, black)
    screen.blit(srf, ((ms.width*(cellPixelWH+borderWH)+borderWH+10,240)))
    if (won+lost > 0):
        srf = font_text.render("Avg time/game: "+ str(round(total_t / (won+lost),2))+"s", True, black)
        screen.blit(srf, ((ms.width*(cellPixelWH+borderWH)+borderWH+10,260)))
        
    srf = font_text.render("CONTROLS", True, black)
    screen.blit(srf, ((ms.width*(cellPixelWH+borderWH)+borderWH+10,310)))
    srf = font_text.render("Left click to uncover", True, black)
    screen.blit(srf, ((ms.width*(cellPixelWH+borderWH)+borderWH+10,330)))
    srf = font_text.render("Right click to set flag", True, black)
    screen.blit(srf, ((ms.width*(cellPixelWH+borderWH)+borderWH+10,350)))
    srf = font_text.render("Spacebar to reset game", True, black)
    screen.blit(srf, ((ms.width*(cellPixelWH+borderWH)+borderWH+10,370))) 
    srf = font_text.render("Enter for an AI move", True, black)
    screen.blit(srf, ((ms.width*(cellPixelWH+borderWH)+borderWH+10,390))) 
    srf = font_text.render("L to toggle AI loop", True, black)
    screen.blit(srf, ((ms.width*(cellPixelWH+borderWH)+borderWH+10,410))) 
        
    srf = font.render(str(fieldCoord[0]) + ", " + str(fieldCoord[1]), True, black)
    screen.blit(srf, ((ms.width*(cellPixelWH+borderWH)+borderWH+10,ms.height*(cellPixelWH+borderWH)+borderWH-60)))

pygame.init()
ms = Minesweeper(width, height, mineCount)
font = pygame.font.SysFont("comicsansms", 20)
font_text = pygame.font.SysFont("arialms", 30)
screen = pygame.display.set_mode((ms.width*(cellPixelWH+borderWH)+borderWH+250, ms.height*(cellPixelWH+borderWH)+borderWH))

running = True
ai_loop = False
waitForNG = False
ms_ai = Minesweeper_AI()

while running:
    fieldCoord = mouseToField(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        #Space bar to reset the game
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                ms.resetField()
                ms_ai.knowledge = []
                waitForNG = False
        #Enter for AI move
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                mv = ms_ai.move(ms)
                if mv is not None:
                    ms.click(mv[0],mv[1], ms_ai)
                    print("=>"+str(mv))
            if event.key == pygame.K_l:
                start_t = time.perf_counter()
                ai_loop = not ai_loop

        if event.type == pygame.MOUSEBUTTONDOWN:
            #Left click to uncover a mine field
            if pygame.mouse.get_pressed()[0]:
                if (fieldCoord[0] < ms.width) and (fieldCoord[1] < ms.height):
                    ms.click(fieldCoord[0], fieldCoord[1], ms_ai)

            #Right click to flag a spot
            if pygame.mouse.get_pressed()[2]:
                if (fieldCoord[0] < ms.width) and (fieldCoord[1] < ms.height):
                    ms.setFlag(fieldCoord[0], fieldCoord[1])
      
    if (ai_loop):
        mv = ms_ai.move(ms)
        if mv is not None:
            ms.click(mv[0],mv[1], ms_ai)
            print("=>"+str(mv))
    screen.fill(grey)
    drawMS(screen, font, ms)
    if (ms.gameOver) or (ms.gameWon):
        if (not waitForNG):
            if (ms.gameOver):
                lost += 1
            if (ms.gameWon):
                won += 1
            waitForNG = True
        if (ai_loop):
            end_t = time.perf_counter()
            time_taken = end_t - start_t
            total_t += time_taken
            ms.resetField()
            ms_ai.knowledge = []
            waitForNG = False
            start_t = time.perf_counter()
            
    printText(ms, ms_ai, font_text, screen)
    pygame.display.update()
    
pygame.quit()