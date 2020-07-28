# Ink Spill (a Flood It clone)
# http://inventwithpython.com/pygame
# By Al Sweigart al@inventwithpython.com
# Released under a "Simplified BSD" license

import inkspill_ai2 as ai
import queue
import random as rnd
import sys, webbrowser, copy, pygame
from pygame.locals import *

# There are different box sizes, number of boxes, and
# life depending on the "board size" setting selected.
SMALLBOXSIZE  = 60 # size is in pixels
MEDIUMBOXSIZE = 20
LARGEBOXSIZE  = 11

SMALLBOARDSIZE  = 6 # size is in boxes
MEDIUMBOARDSIZE = 17
LARGEBOARDSIZE  = 30

SMALLMAXLIFE  = 10 # number of turns
MEDIUMMAXLIFE = 30
LARGEMAXLIFE  = 64

FPS = 30
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
boxSize = MEDIUMBOXSIZE
PALETTEGAPSIZE = 10
PALETTESIZE = 45
EASY = 0   # arbitrary but unique value
MEDIUM = 1 # arbitrary but unique value
HARD = 2   # arbitrary but unique value

difficulty = MEDIUM # game starts in "medium" mode
maxLife = MEDIUMMAXLIFE
boardWidth = MEDIUMBOARDSIZE
boardHeight = MEDIUMBOARDSIZE


#            R    G    B
WHITE    = (255, 255, 255)
DARKGRAY = ( 70,  70,  70)
BLACK    = (  0,   0,   0)
RED      = (255,   0,   0)
GREEN    = (  0, 255,   0)
BLUE     = (  0,   0, 255)
YELLOW   = (255, 255,   0)
ORANGE   = (255, 128,   0)
PURPLE   = (255,   0, 255)

# The first color in each scheme is the background color, the next six are the palette colors.
COLORSCHEMES = (((240, 240, 240), RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE),
                ((0, 155, 104),  (97, 215, 164),  (228, 0, 69),  (0, 125, 50),   (204, 246, 0),   (148, 0, 45),    (241, 109, 149)),
                ((195, 179, 0),  (255, 239, 115), (255, 226, 0), (147, 3, 167),  (24, 38, 176),   (166, 147, 0),   (197, 97, 211)),
                ((85, 0, 0),     (155, 39, 102),  (0, 201, 13),  (255, 118, 0),  (206, 0, 113),   (0, 130, 9),     (255, 180, 115)),
                ((191, 159, 64), (183, 182, 208), (4, 31, 183),  (167, 184, 45), (122, 128, 212), (37, 204, 7),    (88, 155, 213)),
                ((200, 33, 205), (116, 252, 185), (68, 56, 56),  (52, 238, 83),  (23, 149, 195),  (222, 157, 227), (212, 86, 185)))
for i in range(len(COLORSCHEMES)):
    assert len(COLORSCHEMES[i]) == 7, 'Color scheme %s does not have exactly 7 colors.' % (i)
bgColor = COLORSCHEMES[0][0]
paletteColors = COLORSCHEMES[0][1:]


class Board():
    def __init__(self, field, width, height, palette_colors):
        self.field = field
        self.width = width
        self.height = height
        self.palette_colors = palette_colors

    def __getitem__(self, key):
        return self.field[key]

    def draw(self, transparency=255):
        # The colored squares are drawn to a temporary surface which is then
        # drawn to the DISPLAYSURF surface. This is done so we can draw the
        # squares with transparency on top of DISPLAYSURF as it currently is.
        tempSurf = pygame.Surface(DISPLAYSURF.get_size())
        tempSurf = tempSurf.convert_alpha()
        tempSurf.fill((0, 0, 0, 0))

        for x in range(self.width):
            for y in range(self.height):
                left, top = leftTopPixelCoordOfCells(x, y)
                r, g, b = paletteColors[self.field[x][y]]
                pygame.draw.rect(tempSurf, (r, g, b, transparency), (left, top, boxSize, boxSize))
        left, top = leftTopPixelCoordOfCells(0, 0)
        pygame.draw.rect(tempSurf, BLACK, (left - 1, top - 1, boxSize * boardWidth + 1, boxSize * boardHeight + 1), 1)
        DISPLAYSURF.blit(tempSurf, (0, 0))


def main():
    global FPSCLOCK, DISPLAYSURF, LOGOIMAGE, SPOTIMAGE, SETTINGSIMAGE, SETTINGSBUTTONIMAGE, RESETBUTTONIMAGE, UNDOBUTTONIMAGE

    def draw_screen(mainBoard, life):
        # Draw the screen.
        DISPLAYSURF.fill(bgColor)
        drawLogoAndButtons()
        mainBoard.draw()
        drawLifeMeter(life)
        drawPalettes()

    def load_images():
        global LOGOIMAGE, SPOTIMAGE, SETTINGSIMAGE, SETTINGSBUTTONIMAGE, RESETBUTTONIMAGE, UNDOBUTTONIMAGE
        # Load images
        LOGOIMAGE = pygame.image.load('inkspill_logo.png')
        SPOTIMAGE = pygame.image.load('inkspill_spot.png')
        UNDOBUTTONIMAGE = pygame.image.load('inkspill_undo_button.png')
        SETTINGSIMAGE = pygame.image.load('inkspill_settings.png')
        SETTINGSBUTTONIMAGE = pygame.image.load('inkspill_move_button.png')
        # SETTINGSBUTTONIMAGE = pygame.image.load('inkspill_settings_button.png')
        RESETBUTTONIMAGE = pygame.image.load('inkspill_reset_button.png')


    def is_settings_button_pressed():
        return pygame.Rect(WINDOWWIDTH - SETTINGSBUTTONIMAGE.get_width(),
                            WINDOWHEIGHT - SETTINGSBUTTONIMAGE.get_height(),
                            SETTINGSBUTTONIMAGE.get_width(),
                            SETTINGSBUTTONIMAGE.get_height()).collidepoint(mousex, mousey)
    def is_reset_button_pressed():
        return pygame.Rect(WINDOWWIDTH - RESETBUTTONIMAGE.get_width(),
                            WINDOWHEIGHT - SETTINGSBUTTONIMAGE.get_height() - RESETBUTTONIMAGE.get_height(),
                            RESETBUTTONIMAGE.get_width(),
                            RESETBUTTONIMAGE.get_height()).collidepoint(mousex, mousey)

    def is_undo_button_pressed():
        return pygame.Rect(WINDOWWIDTH - UNDOBUTTONIMAGE.get_width(),
                            WINDOWHEIGHT - SETTINGSBUTTONIMAGE.get_height() - RESETBUTTONIMAGE.get_height() - UNDOBUTTONIMAGE.get_height(),
                            UNDOBUTTONIMAGE.get_width(),
                            UNDOBUTTONIMAGE.get_height()).collidepoint(mousex, mousey)


    load_images()

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))


    pygame.display.set_caption('Ink Spill')
    mousex = 0
    mousey = 0
    f_resetGame = True

    mainBoard_history = []

    while True: # main game loop
        if f_resetGame:
            mainBoard = Board(generateRandomBoard(boardWidth, boardHeight, difficulty), boardWidth, boardHeight, paletteColors)
            life = maxLife
            lastPaletteClicked = mainBoard.field[0][0]

            f_resetGame = False

        paletteClicked = None

        draw_screen(mainBoard, life)

        checkForQuit()
        for event in pygame.event.get():  # event handling loop
            if event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                if is_settings_button_pressed():
                    # f_resetGame = showSettingsScreen() # clicked on Settings button
                    mainBoard_old = copy.deepcopy(mainBoard)
                    mainBoard_history.append(mainBoard_old)
                    move = ai.make_move(mainBoard, life)
                    if move is not None:
                        x0, y0 = 0, 0
                        floodFill(mainBoard, move, x0, y0)
                    life -= 1
                elif is_reset_button_pressed():
                    f_resetGame = True # clicked on Reset button
                elif is_undo_button_pressed():
                    print('Undo pressed')
                    mainBoard = mainBoard_history.pop()
                    life += 1
                else:
                    # check if a palette button was clicked
                    paletteClicked = getColorOfPaletteAt(mousex, mousey)
            elif event.type == KEYDOWN:
                # support up to 9 palette keys
                try:
                    key = int(event.unicode)
                except:
                    key = None

                if key != None and key > 0 and key <= len(paletteColors):
                    paletteClicked = key - 1

        if paletteClicked != None and paletteClicked != lastPaletteClicked:
            # a palette button was clicked that is different from the
            # last palette button clicked (this check prevents the player
            # from accidentally clicking the same palette twice)
            mainBoard_old = copy.deepcopy(mainBoard)
            mainBoard_history.append(mainBoard_old)

            lastPaletteClicked = paletteClicked
            floodAnimation(mainBoard, paletteClicked)
            life -= 1

            f_resetGame = False
            if hasWon(mainBoard):
                for i in range(4): # flash border 4 times
                    flashBorderAnimation(WHITE, mainBoard)
                f_resetGame = True
                pygame.time.wait(2000) # pause so the player can bask in victory
            elif life == 0:
                # life is zero, so player has lost
                drawLifeMeter(0)
                pygame.display.update()
                pygame.time.wait(400)
                for i in range(4):
                    flashBorderAnimation(BLACK, mainBoard)
                f_resetGame = True
                pygame.time.wait(2000) # pause so the player can suffer in their defeat

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def checkForQuit():
    # Terminates the program if there are any QUIT or escape key events.
    for event in pygame.event.get(QUIT): # get all the QUIT events
        pygame.quit() # terminate if any QUIT events are present
        sys.exit()
    for event in pygame.event.get(KEYUP): # get all the KEYUP events
        if event.key == K_ESCAPE:
            pygame.quit() # terminate if the KEYUP event was for the Esc key
            sys.exit()
        pygame.event.post(event) # put the other KEYUP event objects back


def hasWon(board):
    # if the entire board is the same color, player has won
    for x in range(boardWidth):
        for y in range(boardHeight):
            if board[x][y] != board[0][0]:
                return False # found a different color, player has not won
    return True


def showSettingsScreen():
    global difficulty, boxSize, boardWidth, boardHeight, maxLife, paletteColors, bgColor

    # The pixel coordinates in this function were obtained by loading
    # the inkspillsettings.png image into a graphics editor and reading
    # the pixel coordinates from there. Handy trick.

    origDifficulty = difficulty
    origBoxSize = boxSize
    screenNeedsRedraw = True

    while True:
        if screenNeedsRedraw:
            DISPLAYSURF.fill(bgColor)
            DISPLAYSURF.blit(SETTINGSIMAGE, (0,0))

            # place the ink spot marker next to the selected difficulty
            if difficulty == EASY:
                DISPLAYSURF.blit(SPOTIMAGE, (30, 4))
            if difficulty == MEDIUM:
                DISPLAYSURF.blit(SPOTIMAGE, (8, 41))
            if difficulty == HARD:
                DISPLAYSURF.blit(SPOTIMAGE, (30, 76))

            # place the ink spot marker next to the selected size
            if boxSize == SMALLBOXSIZE:
                DISPLAYSURF.blit(SPOTIMAGE, (22, 150))
            if boxSize == MEDIUMBOXSIZE:
                DISPLAYSURF.blit(SPOTIMAGE, (11, 185))
            if boxSize == LARGEBOXSIZE:
                DISPLAYSURF.blit(SPOTIMAGE, (24, 220))

            for i in range(len(COLORSCHEMES)):
                drawColorSchemeBoxes(500, i * 60 + 30, i)

            pygame.display.update()

        screenNeedsRedraw = False # by default, don't redraw the screen
        for event in pygame.event.get(): # event handling loop
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYUP:
                if event.key == K_ESCAPE:
                    # Esc key on settings screen goes back to game
                    return not (origDifficulty == difficulty and origBoxSize == boxSize)
            elif event.type == MOUSEBUTTONUP:
                screenNeedsRedraw = True # screen should be redrawn
                mousex, mousey = event.pos # syntactic sugar

                # check for clicks on the difficulty buttons
                if pygame.Rect(74, 16, 111, 30).collidepoint(mousex, mousey):
                    difficulty = EASY
                elif pygame.Rect(53, 50, 104, 29).collidepoint(mousex, mousey):
                    difficulty = MEDIUM
                elif pygame.Rect(72, 85, 65, 31).collidepoint(mousex, mousey):
                    difficulty = HARD

                # check for clicks on the size buttons
                elif pygame.Rect(63, 156, 84, 31).collidepoint(mousex, mousey):
                    # small board size setting:
                    boxSize = SMALLBOXSIZE
                    boardWidth = SMALLBOARDSIZE
                    boardHeight = SMALLBOARDSIZE
                    maxLife = SMALLMAXLIFE
                elif pygame.Rect(52, 192, 106,32).collidepoint(mousex, mousey):
                    # medium board size setting:
                    boxSize = MEDIUMBOXSIZE
                    boardWidth = MEDIUMBOARDSIZE
                    boardHeight = MEDIUMBOARDSIZE
                    maxLife = MEDIUMMAXLIFE
                elif pygame.Rect(67, 228, 58, 37).collidepoint(mousex, mousey):
                    # large board size setting:
                    boxSize = LARGEBOXSIZE
                    boardWidth = LARGEBOARDSIZE
                    boardHeight = LARGEBOARDSIZE
                    maxLife = LARGEMAXLIFE
                elif pygame.Rect(14, 299, 371, 97).collidepoint(mousex, mousey):
                    # clicked on the "learn programming" ad
                    webbrowser.open('http://inventwithpython.com') # opens a web browser
                elif pygame.Rect(178, 418, 215, 34).collidepoint(mousex, mousey):
                    # clicked on the "back to game" button
                    return not (origDifficulty == difficulty and origBoxSize == boxSize)

                for i in range(len(COLORSCHEMES)):
                    # clicked on a color scheme button
                    if pygame.Rect(500, 30 + i * 60, MEDIUMBOXSIZE * 3, MEDIUMBOXSIZE * 2).collidepoint(mousex, mousey):
                        bgColor = COLORSCHEMES[i][0]
                        paletteColors  = COLORSCHEMES[i][1:]


def drawColorSchemeBoxes(x, y, schemeNum):
    # Draws the color scheme boxes that appear on the "Settings" screen.
    for boxy in range(2):
        for boxx in range(3):
            pygame.draw.rect(DISPLAYSURF, COLORSCHEMES[schemeNum][3 * boxy + boxx + 1], (x + MEDIUMBOXSIZE * boxx, y + MEDIUMBOXSIZE * boxy, MEDIUMBOXSIZE, MEDIUMBOXSIZE))
            if paletteColors == COLORSCHEMES[schemeNum][1:]:
                # put the ink spot next to the selected color scheme
                DISPLAYSURF.blit(SPOTIMAGE, (x - 50, y))


def flashBorderAnimation(color, board, animationSpeed=30):
    origSurf = DISPLAYSURF.copy()
    flashSurf = pygame.Surface(DISPLAYSURF.get_size())
    flashSurf = flashSurf.convert_alpha()
    for start, end, step in ((0, 256, 1), (255, 0, -1)):
        # the first iteration on the outer loop will set the inner loop
        # to have transparency go from 0 to 255, the second iteration will
        # have it go from 255 to 0. This is the "flash".
        for transparency in range(start, end, animationSpeed * step):
            DISPLAYSURF.blit(origSurf, (0, 0))
            r, g, b = color
            flashSurf.fill((r, g, b, transparency))
            DISPLAYSURF.blit(flashSurf, (0, 0))
            board.draw()  # draw board ON TOP OF the transparency layer
            pygame.display.update()
            FPSCLOCK.tick(FPS)
    DISPLAYSURF.blit(origSurf, (0, 0)) # redraw the original surface


def floodAnimation(board, paletteClicked, animationSpeed=25):
    origBoard = copy.deepcopy(board)
    floodFill(board, paletteClicked, 0, 0)

    for transparency in range(0, 255, animationSpeed):
        # The "new" board slowly become opaque over the original board.
        origBoard.draw()
        board.draw(transparency)
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def generateRandomBoard(width, height, difficulty=MEDIUM):
    # Creates a board data structure with random colors for each box.
    board = [[rnd.randint(0, len(paletteColors) - 1) for _ in range(height)] for _ in range(width)]

    # Make board easier by setting some boxes to same color as a neighbor.

    # Determine how many boxes to change.
    if difficulty == EASY:
        if boxSize == SMALLBOXSIZE:
            boxesToChange = 100
        else:
            boxesToChange = 1500
    elif difficulty == MEDIUM:
        if boxSize == SMALLBOXSIZE:
            boxesToChange = 5
        else:
            boxesToChange = 100
    else:
        boxesToChange = 0

    # Change neighbor's colors:
    for i in range(boxesToChange):
        # Randomly choose a box whose color will be changed
        x = rnd.randint(1, width-2)
        y = rnd.randint(1, height-2)

        # Randomly choose neighbors to change.
        dx = rnd.randint(-1, 1)
        dy = [-1, 1, 0][rnd.randint(0, 2 if dx else 1)]
        board[x][y] = board[x + dx][y + dy]
    return board


def drawLogoAndButtons():
    # draw the Ink Spill logo and Settings and Reset buttons.
    DISPLAYSURF.blit(LOGOIMAGE, (WINDOWWIDTH - LOGOIMAGE.get_width(), 0))
    DISPLAYSURF.blit(SETTINGSBUTTONIMAGE,
                     (WINDOWWIDTH - SETTINGSBUTTONIMAGE.get_width(), WINDOWHEIGHT - SETTINGSBUTTONIMAGE.get_height()))
    DISPLAYSURF.blit(RESETBUTTONIMAGE,
                     (WINDOWWIDTH - RESETBUTTONIMAGE.get_width(),
                      WINDOWHEIGHT - SETTINGSBUTTONIMAGE.get_height() - RESETBUTTONIMAGE.get_height()))
    DISPLAYSURF.blit(UNDOBUTTONIMAGE,
                     (WINDOWWIDTH - UNDOBUTTONIMAGE.get_width(),
                      WINDOWHEIGHT - SETTINGSBUTTONIMAGE.get_height() - RESETBUTTONIMAGE.get_height() - UNDOBUTTONIMAGE.get_height()))



def drawPalettes():
    # Draws the six color palettes at the bottom of the screen.
    numColors = len(paletteColors)
    xmargin = int((WINDOWWIDTH - ((PALETTESIZE * numColors) + (PALETTEGAPSIZE * (numColors - 1)))) / 2)
    for i in range(numColors):
        left = xmargin + (i * PALETTESIZE) + (i * PALETTEGAPSIZE)
        top = WINDOWHEIGHT - PALETTESIZE - 10
        pygame.draw.rect(DISPLAYSURF, paletteColors[i], (left, top, PALETTESIZE, PALETTESIZE))
        pygame.draw.rect(DISPLAYSURF, bgColor,   (left + 2, top + 2, PALETTESIZE - 4, PALETTESIZE - 4), 2)


def drawLifeMeter(currentLife):
    lifeBoxSize = int((WINDOWHEIGHT - 40) / maxLife)

    # Draw background color of life meter.
    pygame.draw.rect(DISPLAYSURF, bgColor, (20, 20, 20, 20 + (maxLife * lifeBoxSize)))

    for i in range(maxLife):
        if currentLife >= (maxLife - i): # draw a solid red box
            pygame.draw.rect(DISPLAYSURF, RED, (20, 20 + (i * lifeBoxSize), 20, lifeBoxSize))
        pygame.draw.rect(DISPLAYSURF, WHITE, (20, 20 + (i * lifeBoxSize), 20, lifeBoxSize), 1) # draw white outline


def getColorOfPaletteAt(x, y):
    # Returns the index of the color in paletteColors that the x and y parameters
    # are over. Returns None if x and y are not over any palette.
    numColors = len(paletteColors)
    xmargin = int((WINDOWWIDTH - ((PALETTESIZE * numColors) + (PALETTEGAPSIZE * (numColors - 1)))) / 2)
    top = WINDOWHEIGHT - PALETTESIZE - 10

    # Find out if the mouse click is inside any of the palettes.
    x -= xmargin
    y -= top
    i, j = divmod(x, PALETTESIZE + PALETTEGAPSIZE)

    if (y >= 0 and y < PALETTESIZE and
        x >= 0 and i < numColors and j < PALETTESIZE):
        return i
    return None # no palette exists at these x, y coordinates


def floodFill(board, color_new, x0, y0):
    """This is the flood fill algorithm."""
    color_old = board[x0][y0]
    if color_old == color_new:
        return
    
    cell_queue = queue.Queue()
    cell_queue.put((x0, y0))

    while not cell_queue.empty():
        x, y = cell_queue.get()
        if board[x][y] != color_old:
            continue

        board[x][y] = color_new

        if x > 0:
            cell_queue.put((x - 1, y))
        if x < boardWidth - 1:
            cell_queue.put((x + 1, y))
        if y > 0:
            cell_queue.put((x, y - 1))
        if y < boardHeight - 1:
            cell_queue.put((x, y + 1))


def leftTopPixelCoordOfCells(cell_x, cell_y):
    # Returns the x and y of the left-topmost pixel of the xth & yth box.
    margin_x = int((WINDOWWIDTH - (boardWidth * boxSize)) / 2)
    margin_y = int((WINDOWHEIGHT - (boardHeight * boxSize)) / 2)
    return (cell_x * boxSize + margin_x, cell_y * boxSize + margin_y)


if __name__ == '__main__':
    main()
