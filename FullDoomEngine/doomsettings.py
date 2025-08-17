from enum import Enum
import math

DOOM_RES = DOOM_W, DOOM_H = 320,200

SCALE = 4.0
WIN_RES = WIDTH, HEIGHT = int(DOOM_W*SCALE), int(DOOM_H*SCALE)

H_WIDTH, H_HEIGHT = WIDTH // 2, HEIGHT // 2

FOV = 90
FOV_RAD = math.pi/2
H_FOV = FOV // 2
H_FOV_RAD = FOV_RAD / 2

PLAYER_SPEED = 0.3
PLAYER_ROT_SPEED = 0.12
PLAYER_HEIGHT = 41
PLAYER_SIZE = 16
PLAYER_CLIMB_SPEED = 0.2
PLAYER_FALL_SPEED = 0.3
PLAYER_STEP_AMPLITUDE = 10
PLAYER_STEP_FREQUENCY = 0.01

DOOR_OPEN_SPEED = 1

WEAPON_CHANGE_SPEED = 10

SCREEN_DIST = H_WIDTH / math.tan(math.radians(H_FOV))
COLOUR_KEY = (152, 0, 136)

MOUSE_SENSITIVITY = 0.03
MOUSE_MAX_REL = 40
MOUSE_BORDER_LEFT = 100
MOUSE_BORDER_RIGHT = WIDTH - MOUSE_BORDER_LEFT

# can we pass through a portal wall?
MIN_ROOM_HEIGHT = PLAYER_HEIGHT + 5
MAX_STEP_HEIGHT = 24

# from how far away can we activate a door?
ACTIVATION_DIST = 200

class WALL_TYPE(Enum):
    SOLID_WALL = 0
    DOOR = 1
    PASSABLE = 2
    IMPASSABLE = 3

# for sound effects
SAMPLE_RATE = 11025

# sprites
WEAPON_BUTTONS = {
    '1' : "hand",
    '2' : "pistol",
    '3' : "shotgun"
}
WEAPON_SPRITES = {
    'hand': 'PUNGA0',
    'pistol' : 'PISGA0',
    'shotgun' : 'SHTGA0',
}
MAX_WEAPON_OFFSET = 200

SOUNDS = {
    'pistol': "DSPISTOL",
    'shotgun': "DSSHOTGN",
    'barrel_explode': "DSBRSD:",
    'door_open': "DSDOROPN"
}

# sprites in the WAD file are larger than world space
# e.g. soldier is 220 pixels vs 56 for canonical doom sprite.
SPRITE_PIX_RATIO = 56 / 220

# sprites can scale up to 2x original image size when 
# player is right next to them.
MAX_SPRITE_HEIGHT_RATIO = 2

# from DOOM Wiki - interpret the bits in the "flags" attribute
# of "Things" in the WAD
WAD_THING_FLAGS = {
    0: "Easy",
    1: "Medium",
    2: "Hard",
    3: "Ambush",
    4: "Not in DM",
    5: "Not in SP",
    6: "Not in Coop"
}