import pygame, sys
from pygame.locals import *


FPS = 60
WINWIDTH = 800
WINHEIGHT = 800
TILESIZE = 40
PLAYERSIZEX = 30
PLAYERSIZEY = 40
SPAWNPOINT = (360, 680)
RANGERATE = 0.25
MAXRANGE = 4
JUMPRATE = -0.25
MAXJUMP = -10
GRAVITY = 0.25
MAXGRAVITY = 10
BOUNCERATE = -0.5
CRASHSTUN = 2

SOUNDVOL = 0.4

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

BGCOLOR = BLACK

LEFT = "left"
RIGHT = "right"

def main():
    global FPSCLOCK, DISPLAYSURF
    
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    
    DISPLAYSURF = pygame.display.set_mode((WINWIDTH, WINHEIGHT))
    pygame.display.set_caption("Rowan Quest")
    DISPLAYSURF.fill(BGCOLOR)
    
    ## START SCREEN HERE ##
    start_screen()
    
    while True:
        run_game()

def run_game():
    global animation_frames, TILEMAP
    
    TILESET = {'topleft':        pygame.image.load('tiles/platforms/topleft.png'),
               'top':            pygame.image.load('tiles/platforms/top.png'),
               'topright':       pygame.image.load('tiles/platforms/topright.png'),
               'left':           pygame.image.load('tiles/platforms/left.png'),
               'center':         pygame.image.load('tiles/platforms/center.png'),
               'right':          pygame.image.load('tiles/platforms/right.png'),
               'bottomleft':     pygame.image.load('tiles/platforms/bottomleft.png'),
               'bottom':         pygame.image.load('tiles/platforms/bottom.png'),
               'bottomright':    pygame.image.load('tiles/platforms/bottomright.png'),
               'invtopleft':     pygame.image.load('tiles/platforms/invtopleft.png'),
               'invtopright':    pygame.image.load('tiles/platforms/invtopright.png'),
               'invbottomleft':  pygame.image.load('tiles/platforms/invbottomleft.png'),
               'invbottomright': pygame.image.load('tiles/platforms/invbottomright.png'),
               'single':         pygame.image.load('tiles/platforms/single.png')
               }
    
    TILEMAP = {'0': TILESET['single'],
               '1': TILESET['topleft'],
               '2': TILESET['top'],
               '3': TILESET['topright'],
               '4': TILESET['left'],
               '5': TILESET['center'],
               '6': TILESET['right'],
               '7': TILESET['bottomleft'],
               '8': TILESET['bottom'],
               '9': TILESET['bottomright'],
               'a': TILESET['invtopleft'],
               'b': TILESET['invtopright'],
               'c': TILESET['invbottomleft'],
               'd': TILESET['invbottomright']
               }
    
    MAPSET = { 0: load_map('map0'),
               1: load_map('map1')
              }
    
    BGSET = {0: load_background('bg0'),
             1: load_background('bg0')
             }   
     
    SOUNDS = {'jump':   pygame.mixer.Sound('sound/jump.wav'),
              'land':   pygame.mixer.Sound('sound/land.wav'),
              'crash':  pygame.mixer.Sound('sound/crash.wav'),
              'bounce': pygame.mixer.Sound('sound/bounce.wav')
              }
    
    for sound in SOUNDS.values():
        sound.set_volume(SOUNDVOL)
        
    game_map, tiles = draw_map(MAPSET[0], BGSET[0])
    game_rect = game_map.get_rect()
    game_rect.center = (WINWIDTH / 2, WINHEIGHT / 2)
    DISPLAYSURF.blit(game_map, game_rect)

    animation_frames = {}
    animation_database = {'idle':   load_animation('animations/idle', [100, 10]),
                          'walk':   load_animation('animations/walk', [5, 10, 10]),
                          'charge': load_animation('animations/charge', [1]),
                          'jump':   load_animation('animations/jump', [1]),
                          'bounce': load_animation('animations/bounce', [1]),
                          'crash':  load_animation('animations/crash', [1])
                          }

    player = {'surface': None,
              'facing': LEFT,
              'x': SPAWNPOINT[0],
              'y': SPAWNPOINT[1],
              'action': 'idle',
              'frame': 0,
             }
    
    player['rect'] = pygame.Rect((player['x'], player['y'], PLAYERSIZEX, PLAYERSIZEY))
    
    flip = False
    moveLeft = False
    moveRight = False
    isJumping = False
    isGrounded = False
    isCharging = False
    inAir = False
    hasBounced  = False
    bounceSide = None
    hasCrashed = False
    isSpawning = True
    crashTime = 0
    velocityX = 3
    velocityY = 0
    xrange = 0
    jumpPower = 0
    floor = 0
    
    while True:
        if player['rect'].colliderect(DISPLAYSURF.get_rect()) == 0:
            if player['rect'].y < 0:
                floor += 1
                player['rect'].y = WINHEIGHT
            elif player['rect'].y > 0:
                floor -= 1
                player['rect'].y = 0
            game_map, tiles = draw_map(MAPSET[floor], BGSET[floor])
            game_rect = game_map.get_rect()

            
        DISPLAYSURF.fill(BGCOLOR)
        DISPLAYSURF.blit(game_map, game_rect)
        
        player_img_id = animation_database[player['action']][player['frame']]
        if player['action'] != 'crash':
            player['surface'] = pygame.transform.scale(animation_frames[player_img_id], [PLAYERSIZEX, PLAYERSIZEY])
        else:
            player['surface'] = pygame.transform.scale(animation_frames[player_img_id], [PLAYERSIZEY, PLAYERSIZEY])
        DISPLAYSURF.blit(pygame.transform.flip(player['surface'], flip, False), player['rect'])
        
        player['frame'] += 1
        if player['frame'] >= len(animation_database[player['action']]):
            player['frame'] = 0
        
        
                
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
                
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()
                elif event.key == K_o:
                    option_screen()
                if not hasCrashed:
                    if event.key in (K_LEFT, K_a):
                        moveLeft = True
                        moveRight = False
                        if player['facing'] == RIGHT and isGrounded:
                            flip = False
                        player['facing'] = LEFT
                    elif event.key in (K_RIGHT, K_d):
                        moveLeft = False
                        moveRight = True
                        if player['facing'] == LEFT and isGrounded:
                            flip = True
                        player['facing'] = RIGHT
                    elif event.key == K_SPACE:
                        if not isCharging and isGrounded:
                            isCharging = True
                            
            elif event.type == KEYUP:
                if not hasCrashed:
                    if event.key in (K_LEFT, K_a):
                        moveLeft = False
                    elif event.key in (K_RIGHT, K_d):
                        moveRight = False
                    elif event.key == K_SPACE:
                        if isCharging:
                            velocityY = jumpPower
                            jumpPower = 0
                            isJumping = True
                            isGrounded = False
                            isCharging = False
                            inAir = True
                            SOUNDS['jump'].play()
                            
        movement = [0, 0]
        if isCharging:
            if moveRight:
                xrange += RANGERATE
                if xrange > MAXRANGE:
                    xrange = MAXRANGE
            elif moveLeft:
                xrange -= RANGERATE
                if xrange < -MAXRANGE:
                    xrange = -MAXRANGE
            jumpPower += JUMPRATE
            if jumpPower <= MAXJUMP:
                velocityY = jumpPower
                isJumping = True
                isGrounded = False
                isCharging = False
                inAir = True
                jumpPower = 0
                SOUNDS['jump'].play()
        elif isJumping:
            movement[0] += xrange
        elif isGrounded:
            if moveRight:
                movement[0] += velocityX
            elif moveLeft:
                movement[0] -= velocityX
        elif inAir and not isSpawning and not hasBounced:
            if flip:
                movement[0] += velocityX / 2
            else:
                movement[0] -= velocityX / 2
        if isGrounded and not isCharging:
            xrange = 0   
        movement[1] += velocityY
        velocityY += GRAVITY
        if velocityY > MAXGRAVITY:
            velocityY = MAXGRAVITY 
            
            
        if isCharging:
            player['action'], player['frame'] = change_action(player['action'], player['frame'], 'charge')
        elif (inAir or isJumping) and not hasBounced and not isSpawning:
            player['action'], player['frame'] = change_action(player['action'], player['frame'], 'jump') 
        elif abs(movement[0]) > 0 and isGrounded:
            player['action'], player['frame'] = change_action(player['action'], player['frame'], 'walk')    
        elif movement[0] == 0 and not hasCrashed and not hasBounced:
            player['action'], player['frame'] = change_action(player['action'], player['frame'], 'idle')
        

        player['rect'], collisions = move(player['rect'], movement, tiles)
        if collisions['bottom']:
            if inAir and velocityY < MAXGRAVITY and not isSpawning:
                SOUNDS['land'].play()
            if velocityY == MAXGRAVITY:
                SOUNDS['crash'].play()
                hasCrashed = True
                moveLeft = False
                moveRight = False
                player['action'], player['frame'] = change_action(player['action'], player['frame'], 'crash')
            if hasCrashed:
                crashTime += FPSCLOCK.get_time() / 1000
                if crashTime >= CRASHSTUN:
                    hasCrashed = False
                    crashTime = 0
            velocityY = 1
            isJumping = False
            isGrounded = True
            inAir = False
            hasBounced = False
            bounceSide = None
            isSpawning = False
            if player['facing'] == RIGHT:
                flip = True
            elif player['facing'] == LEFT:
                flip = False
        else:
            inAir = True
            isGrounded = False 
        if collisions['top']:
            hasBounced = True
            bounceSide = None
            velocityY = 1
            xrange *= -BOUNCERATE
            SOUNDS['bounce'].play()
            player['action'], player['frame'] = change_action(player['action'], player['frame'], 'bounce')
        if collisions['left'] and inAir:
            xrange *= BOUNCERATE
            hasBounced = True
            if bounceSide != LEFT:
                SOUNDS['bounce'].play()
                bounceSide = LEFT
            player['action'], player['frame'] = change_action(player['action'], player['frame'], 'bounce')
        if collisions['right'] and inAir:
            xrange *= BOUNCERATE
            hasBounced = True
            if bounceSide != RIGHT:
                SOUNDS['bounce'].play()
                bounceSide = RIGHT
            player['action'], player['frame'] = change_action(player['action'], player['frame'], 'bounce')
                

        pygame.display.update()
        FPSCLOCK.tick(FPS)
        
        
        
def terminate():
    pygame.quit()
    sys.exit()
    
    
def start_screen():
    bgImage = pygame.transform.scale(pygame.image.load('tiles/backgrounds/bg0.png'), [WINWIDTH, WINHEIGHT])
    bgImage.set_alpha(80)
    bgRect = bgImage.get_rect()
    bgRect.topleft = (0, 0)

    startButton = draw_button(1)
    buttonRect = startButton.get_rect()
    buttonRect.center = (WINWIDTH / 2, (WINHEIGHT / 2) + 168)
    DISPLAYSURF.fill(BGCOLOR)
    DISPLAYSURF.blit(bgImage, bgRect)
    DISPLAYSURF.blit(startButton, buttonRect)
    hovering = False
    clicked = False
    
    while True:
        if clicked:
            pygame.time.wait(300)
            return
        
        if not hovering:
            DISPLAYSURF.fill(BGCOLOR)
            DISPLAYSURF.blit(bgImage, bgRect) 
            DISPLAYSURF.blit(draw_button(1), buttonRect)
        
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()
            elif event.type == MOUSEMOTION:
                mousex, mousey = event.pos
                if buttonRect.collidepoint(mousex, mousey):
                    hovering = True
                    DISPLAYSURF.fill(BGCOLOR)
                    DISPLAYSURF.blit(bgImage, bgRect) 
                    DISPLAYSURF.blit(draw_button(2), buttonRect)
                else:
                    hovering = False
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    mousex, mousey = event.pos
                if buttonRect.collidepoint(mousex, mousey):
                    DISPLAYSURF.fill(BGCOLOR)
                    DISPLAYSURF.blit(bgImage, bgRect) 
                    DISPLAYSURF.blit(draw_button(3), buttonRect)
                    clicked = True
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def draw_button(state):
    button = pygame.image.load('tiles/buttons/StartButton' + str(state) + ".png").convert()
    button.set_colorkey(BGCOLOR)
    
    return button


def option_screen():
    pygame.draw.rect(DISPLAYSURF, WHITE, (200, 200, 400, 200))

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()
                return
            
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def load_map(path):
    map_file = open('tilemaps/' + path + ".txt", 'r')
    map_data = map_file.read()
    map_file.close()
    map_data = map_data.split("\n")
    game_map = []
    for row in map_data:
        game_map.append(list(row))
        
    return game_map

def load_background(path):
    background = pygame.image.load('tiles/backgrounds/' + path + ".png")
    bgScaled = pygame.transform.scale(background, [WINWIDTH, WINHEIGHT])
    return bgScaled

def load_animation(path, frame_durations):
    animation_name = path.split('/')[-1]
    animation_frame_data = []
    n = 0
    for frame in frame_durations:
        animation_frame_id = animation_name + str(n)
        img_loc = path + "/" + animation_frame_id + ".png"
        animation_image = pygame.image.load(img_loc).convert()
        animation_image.set_colorkey(WHITE)
        animation_frames[animation_frame_id] = animation_image.copy()
        for i in range(frame):
            animation_frame_data.append(animation_frame_id)    
        n += 1
        
    return animation_frame_data

def draw_map(tilemap, background):
    mapSurfWidth = WINWIDTH
    mapSurfHeight = WINHEIGHT
    mapSurf = pygame.Surface((mapSurfWidth, mapSurfHeight))
    mapSurf.fill(BGCOLOR)
    
    background.set_alpha(80)
    bgRect = background.get_rect()
    mapSurf.blit(background, bgRect)
    tiles = []
    for y in range(len(tilemap)):
        for x in range(len(tilemap)):
           tileRect = pygame.Rect((x * TILESIZE, y * TILESIZE, TILESIZE, TILESIZE))
           if tilemap[y][x] in TILEMAP:
               tile = pygame.transform.scale(TILEMAP[tilemap[y][x]], (TILESIZE, TILESIZE))
               tiles.append(tileRect)
               mapSurf.blit(tile, tileRect)    
    
    return mapSurf, tiles


def change_action(cur_action, frame, new_action):
    if cur_action != new_action:
        cur_action = new_action
        frame = 0
        
    return cur_action, frame


def collision_test(rect, tiles):
    collisions = []
    for tile in tiles:
        if rect.colliderect(tile):
            collisions.append(tile)
            
    return collisions

    
def move(rect, movement, tiles):
    collision_types = {'top': False, 'bottom': False, 'left': False, 'right': False}
    
    rect.x += movement[0]
    collisions = collision_test(rect, tiles)
    if rect.left <= 0:
        rect.left = 0
        collision_types['left'] = True
    elif rect.right >= WINWIDTH:
        rect.right = WINWIDTH
        collision_types['right'] = True
    for tile in collisions:
        if movement[0] > 0:
            rect.right = tile.left
            collision_types['right'] = True
        elif movement[0] < 0:
            rect.left = tile.right
            collision_types['left'] = True
            
    rect.y += movement[1]
    collisions = collision_test(rect, tiles)
    for tile in collisions:
        if movement[1] > 0:
            rect.bottom = tile.top
            collision_types['bottom'] = True
        elif movement[1] < 0:
            rect.top = tile.bottom
            collision_types['top'] = True
    
    return rect, collision_types
   
if __name__ == '__main__':
    main()