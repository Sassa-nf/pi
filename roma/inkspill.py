# Ink Spill (a Flood It clone)
# http://inventwithpython.com/pygame
# By Al Sweigart al@inventwithpython.com
# Released under a "Simplified BSD" license

import enum
import inkspill_ai as ai
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

class Action(enum.Enum):
    cell_change = 1
    life_change = 2
    color_change = 3
    score_change = 4
    border_change = 5

class Player:
    def __init__(self, num=None, coord=(None, None), color=None, life=None, score=None, border=[]):
        self.coord = coord
        self.color = color
        self.life = life
        self.score = score
        self.border = border
        self.num = num

class Board():
    def __init__(self, width, height, palette_colors):
        self.field = []
        self.width = width
        self.height = height
        self.palette_colors = palette_colors
        self.difficulty = difficulty
        self.history = []
        # players start at 1 because there is 0 color, if 0 is accessed it should give an error
        self.player = []
        self.player.append(Player())

        # life is incremented because move decreases it at the start, score is 1 because first cell belongs to player
        coord = (0, 0)
        self.player.append(Player(num=len(self.player), coord=coord, color=None, life=maxLife + 1, score=1, border=[coord]))

        self.generate_random_board()

        # init current_color for all players
        for num in range(1, len(self.player)):
            x, y = self.player[num].coord
            color = self.field[x][y]
            self.field[x][y] = -num
            self.player[num].color = None
            self.move(num, color)


    def _set_color(self, x, y, color):
        self.history.append({'action': Action.cell_change, 'value': (x, y, self.field[x][y])})
        self.field[x][y] = color

    def get_color(self, x, y):
        color = self.field[x][y]
        return color if color >= 0 else self.player[-color].color

    def get_value(self, x, y):
        return self.field[x][y]

    def _set_player_life(self, player_num, life):
        self.history.append({'action': Action.life_change, 'value': (player_num, self.player[player_num].life)})
        self.player[player_num].life = life

    def _set_player_score(self, player_num, score):
        self.history.append({'action': Action.score_change, 'value': (player_num, self.player[player_num].score)})
        self.player[player_num].score = score

    def _set_player_color(self, player_num, color):
        self.history.append({'action': Action.color_change, 'value': (player_num, self.player[player_num].color)})
        self.player[player_num].color = color

    def _set_player_border(self, player_num, border):
        border_old = self.player[player_num].border
        self.history.append({'action': Action.border_change, 'value': (player_num, border_old)})
        self.player[player_num].border = border

    def undo_to(self, state):
        t = len(self.history)
        while t > state:
            change = self.history.pop()
            if change['action'] == Action.cell_change:
                x, y, color = change['value']
                self.field[x][y] = color
            elif change['action'] == Action.life_change:
                num, life = change['value']
                self.player[num].life = life
            elif change['action'] == Action.color_change:
                num, color = change['value']
                self.player[num].color = color
            elif change['action'] == Action.score_change:
                num, score = change['value']
                self.player[num].score = score
            elif change['action'] == Action.border_change:
                num, border = change['value']
                self.player[num].border = border
            else:
                raise Exception(f"Unknown action in boards history {change['action']}")
            t -= 1

    def get_history_state(self):
        return len(self.history)

    def draw(self, transparency=255):
        # The colored squares are drawn to a temporary surface which is then
        # drawn to the DISPLAYSURF surface. This is done so we can draw the
        # squares with transparency on top of DISPLAYSURF as it currently is.
        tempSurf = pygame.Surface(DISPLAYSURF.get_size())
        tempSurf = tempSurf.convert_alpha()
        tempSurf.fill((0, 0, 0, 0))

        for x in range(self.width):
            for y in range(self.height):
                left, top = get_left_top_pixelcoord_of_cells(x, y)
                color = self.get_color(x, y)
                r, g, b = paletteColors[color]
                pygame.draw.rect(tempSurf, (r, g, b, transparency), (left, top, boxSize, boxSize))
        left, top = get_left_top_pixelcoord_of_cells(0, 0)
        pygame.draw.rect(tempSurf, BLACK, (left - 1, top - 1, boxSize * boardWidth + 1, boxSize * boardHeight + 1), 1)
        DISPLAYSURF.blit(tempSurf, (0, 0))

    def generate_random_board(self):
        # Creates a board data structure with random colors for each box.
        self.field = [None] * self.width
        for x in range(self.width):
            self.field[x] = [rnd.randint(0, len(paletteColors) - 1) for _ in range(self.height)]

        # Make board easier by setting some boxes to same color as a neighbor.

        # Determine how many boxes to change.
        if self.difficulty == EASY:
            if boxSize == SMALLBOXSIZE:
                boxesToChange = 100
            else:
                boxesToChange = 1500
        elif self.difficulty == MEDIUM:
            if boxSize == SMALLBOXSIZE:
                boxesToChange = 5
            else:
                boxesToChange = 50
        else:
            boxesToChange = 0

        # Change neighbor's colors:
        for i in range(boxesToChange):
            # Randomly choose a box whose color will be changed
            x = rnd.randint(1, self.width - 2)
            y = rnd.randint(1, self.height - 2)

            # Randomly choose neighbors to change.
            dx, dy = 0, 0
            while dx == 0 and dy == 0:
                dx = rnd.randint(-1, 1)
                dy = rnd.randint(-1, 1)
                self.field[x][y] = self.field[x + dx][y + dy]


    def has_won(self, player_num):
        # if the entire board is the same color, player has won
        color = self.player[player_num].color
        for x in range(self.width):
            for y in range(self.height):
                if self.get_color(x, y) != color:
                    return False  # found a different color, player has not won
        return True

    def _border_fill(self, player_num, color):
        """This is the flood fill algorithm."""
        border = self.player[player_num].border.copy()
        border_new = []
        dif_lst = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        acquired = 0
        for x, y in border:
            f_append = False
            for dx, dy in dif_lst:
                xn, yn = x + dx, y + dy
                if 0 <= xn < self.width and 0 <= yn < self.height:
                    if self.get_value(xn, yn) == color:
                        self._set_color(xn, yn, -player_num)
                        border.append((xn, yn))
                        # border_new.append((xn, yn))
                        acquired += 1
                    elif self.get_value(xn, yn) != -player_num:
                        f_append = True

            if f_append:
                border_new.append((x, y))

        return border_new, acquired


    def move(self, player_num, color):
        assert color >= 0

        if color != self.player[player_num].color:
            self._set_player_color(player_num, color)

            border_new, acquired = self._border_fill(player_num, color)

            self._set_player_score(player_num, self.player[player_num].score + acquired)
            self._set_player_life(player_num, self.player[player_num].life - 1)
            self._set_player_border(player_num, border_new)

        return acquired


# Meanwhile is not used
class button():
    def __init__(self, image):
        self.image = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text

    def draw(self, win, outline=None):
        # Call this method to draw the button on the screen
        if outline:
            pygame.draw.rect(win, outline, (self.x - 2, self.y - 2, self.width + 4, self.height + 4), 0)

        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height), 0)

        if self.text != '':
            font = pygame.font.SysFont('comicsans', 60)
            text = font.render(self.text, 1, (0, 0, 0))
            win.blit(text, (
            self.x + (self.width / 2 - text.get_width() / 2), self.y + (self.height / 2 - text.get_height() / 2)))

    def isOver(self, pos):
        # Pos is the mouse position or a tuple of (x,y) coordinates
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True

        return False

def main():
    global FPSCLOCK, DISPLAYSURF, LOGOIMAGE, SPOTIMAGE, SETTINGSIMAGE, SETTINGSBUTTONIMAGE, RESETBUTTONIMAGE, UNDOBUTTONIMAGE

    def draw_screen(mainboard):
        # Draw the screen.
        DISPLAYSURF.fill(bgColor)
        draw_logo_and_buttons()
        mainboard.draw()
        draw_life_meter(mainboard.player[1].life)
        draw_palettes()

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
                            SETTINGSBUTTONIMAGE.get_height()).collidepoint(mouse_x, mouse_y)
    def is_reset_button_pressed():
        return pygame.Rect(WINDOWWIDTH - RESETBUTTONIMAGE.get_width(),
                            WINDOWHEIGHT - SETTINGSBUTTONIMAGE.get_height() - RESETBUTTONIMAGE.get_height(),
                            RESETBUTTONIMAGE.get_width(),
                            RESETBUTTONIMAGE.get_height()).collidepoint(mouse_x, mouse_y)

    def is_undo_button_pressed():
        return pygame.Rect(WINDOWWIDTH - UNDOBUTTONIMAGE.get_width(),
                            WINDOWHEIGHT - SETTINGSBUTTONIMAGE.get_height() - RESETBUTTONIMAGE.get_height() - UNDOBUTTONIMAGE.get_height(),
                            UNDOBUTTONIMAGE.get_width(),
                            UNDOBUTTONIMAGE.get_height()).collidepoint(mouse_x, mouse_y)


    load_images()

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))


    pygame.display.set_caption('Ink Spill')
    mouse_x = 0
    mouse_y = 0
    f_resetGame = True

    while True: # main game loop
        if f_resetGame:
            mainboard = Board(boardWidth, boardHeight, paletteColors)
            lastPaletteClicked = mainboard.get_color(0, 0)

            state_history = []

            f_resetGame = False

        paletteClicked = None

        draw_screen(mainboard)

        if check_for_quit():
            pygame.quit()  # terminate if any QUIT events are present
            return
        for event in pygame.event.get():  # event handling loop
            if event.type == MOUSEBUTTONUP:
                mouse_x, mouse_y = event.pos
                if is_settings_button_pressed():
                    # f_resetGame = showSettingsScreen() # clicked on Settings button

                    color = ai.make_move(mainboard, mainboard.player[1])
                    if color is not None:
                        paletteClicked = color
                elif is_reset_button_pressed():
                    f_resetGame = True # clicked on Reset button
                elif is_undo_button_pressed():
                    print('Undo pressed')

                    if state_history:
                        state = state_history.pop()
                        mainboard.undo_to(state)
                else:
                    # check if a palette button was clicked
                    paletteClicked = get_color_of_palette_at(mouse_x, mouse_y)
            elif event.type == KEYDOWN:
                # support up to 9 palette keys
                try:
                    key = int(event.unicode)
                except:
                    key = None

                if key != None and key > 0 and key <= len(paletteColors):
                    paletteClicked = key - 1

        if paletteClicked != None and paletteClicked != mainboard.get_color(0, 0):
            # a palette button was clicked that is different from the
            # last palette button clicked (this check prevents the player
            # from accidentally clicking the same palette twice)
            state_history.append(mainboard.get_history_state())

            # lastPaletteClicked = paletteClicked

            mainboard.move(1, paletteClicked)

            f_resetGame = False
            if mainboard.has_won(1):
                for i in range(4): # flash border 4 times
                    flash_border_animation(WHITE, mainboard)
                f_resetGame = True
                pygame.time.wait(2000) # pause so the player can bask in victory
            elif mainboard.player[1].life == 0:
                # life is zero, so player has lost
                draw_life_meter(0)
                pygame.display.update()
                pygame.time.wait(400)
                for i in range(4):
                    flash_border_animation(BLACK, mainboard)
                f_resetGame = True
                pygame.time.wait(2000) # pause so the player can suffer in their defeat

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def check_for_quit():
    # Terminates the program if there are any QUIT or escape key events.
    f_exit = False
    for event in pygame.event.get(QUIT): # get all the QUIT events
        f_exit = True
    for event in pygame.event.get(KEYUP): # get all the KEYUP events
        if event.key == K_ESCAPE:
            f_exit = True
        pygame.event.post(event) # put the other KEYUP event objects back
    return f_exit


def show_settings_screen():
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
                draw_color_scheme_boxes(500, i * 60 + 30, i)

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


def draw_color_scheme_boxes(x, y, schemeNum):
    # Draws the color scheme boxes that appear on the "Settings" screen.
    for boxy in range(2):
        for boxx in range(3):
            pygame.draw.rect(DISPLAYSURF, COLORSCHEMES[schemeNum][3 * boxy + boxx + 1], (x + MEDIUMBOXSIZE * boxx, y + MEDIUMBOXSIZE * boxy, MEDIUMBOXSIZE, MEDIUMBOXSIZE))
            if paletteColors == COLORSCHEMES[schemeNum][1:]:
                # put the ink spot next to the selected color scheme
                DISPLAYSURF.blit(SPOTIMAGE, (x - 50, y))


def flash_border_animation(color, board, animationSpeed=30):
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


def flood_animation(board, paletteClicked, animationSpeed=25):
    origBoard = copy.deepcopy(board)
    board.flood_fill(paletteClicked, 0, 0)

    for transparency in range(0, 255, animationSpeed):
        # The "new" board slowly become opaque over the original board.
        origBoard.draw()
        board.draw(transparency)
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def draw_logo_and_buttons():
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


def draw_palettes():
    # Draws the six color palettes at the bottom of the screen.
    numColors = len(paletteColors)
    xmargin = int((WINDOWWIDTH - ((PALETTESIZE * numColors) + (PALETTEGAPSIZE * (numColors - 1)))) / 2)
    for i in range(numColors):
        left = xmargin + (i * PALETTESIZE) + (i * PALETTEGAPSIZE)
        top = WINDOWHEIGHT - PALETTESIZE - 10
        pygame.draw.rect(DISPLAYSURF, paletteColors[i], (left, top, PALETTESIZE, PALETTESIZE))
        pygame.draw.rect(DISPLAYSURF, bgColor,   (left + 2, top + 2, PALETTESIZE - 4, PALETTESIZE - 4), 2)


def draw_life_meter(currentLife):
    lifeBoxSize = int((WINDOWHEIGHT - 40) / maxLife)

    # Draw background color of life meter.
    pygame.draw.rect(DISPLAYSURF, bgColor, (20, 20, 20, 20 + (maxLife * lifeBoxSize)))

    for i in range(maxLife):
        if currentLife >= (maxLife - i): # draw a solid red box
            pygame.draw.rect(DISPLAYSURF, RED, (20, 20 + (i * lifeBoxSize), 20, lifeBoxSize))
        pygame.draw.rect(DISPLAYSURF, WHITE, (20, 20 + (i * lifeBoxSize), 20, lifeBoxSize), 1) # draw white outline


def get_color_of_palette_at(x, y):
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


def get_left_top_pixelcoord_of_cells(cell_x, cell_y):
    # Returns the x and y of the left-topmost pixel of the xth & yth box.
    margin_x = int((WINDOWWIDTH - (boardWidth * boxSize)) / 2)
    margin_y = int((WINDOWHEIGHT - (boardHeight * boxSize)) / 2)
    return (cell_x * boxSize + margin_x, cell_y * boxSize + margin_y)


if __name__ == '__main__':
    main()
