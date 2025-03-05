'''
This file contains configuration variables for pdf.
You can alter the values to change to look of the pdf.
'''

# BUTTONS
BUTTON_EXIT = 'q'

# FOLDERS
FOLDER_ANNOTATED = 'AnnotatedDataset'
FOLDER_MASKS = f'{FOLDER_ANNOTATED}/masks'
FOLDER_ANNOTATIONS = f'{FOLDER_ANNOTATED}/annotations'
FOLDER_ORIGINAL_IMAGES = f'{FOLDER_ANNOTATED}/images_without_annotations'
FOLDER_TXT = f'{FOLDER_ANNOTATED}/txt'

#SPLASH IMAGE PATH
SPLASH_IMAGE = "./images/MedAP.png"

# COLOURS
COLOUR_ROOT_BG = '#2E2E2E'
COLOUR_TBUTTON_BG = '#444444'
COLOUR_TBUTTON_FG = 'WHITE'
COLOUR_TBUTTON_BG_ACTIVE = '#555555'

COLOUR_CANVAS_BG = '#1E1E1E'
COLOUR_CANVAS_MOUSE = 'WHITE'

COLOUR_BOX_OUTLINE = 'RED'
COLOUR_POINT_OUTLINE = 'GREEN'

COLOUR_LINE = 'WHITE'

#FONTS
FONT_SIZE=22

#GUI SHAPE
GUI_WIDTH=1300
GUI_HEIGHT=850


# ZOOM
ZOOM_VALUE = 1.0
ZOOM_FACTOR = 0.1
ZOOM_MIN = 0.5
ZOOM_MAX = 5.0