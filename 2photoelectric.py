import pygame
import random
import math
import dan_gui


# Class for a rectangle that is drawn to the screen and has a collision hit box
# Represents a metal terminal
class MetalRect:

    # Takes x, y, width and height as parameters
    # Used in drawing the rectangle
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        # Creates a pygame Rect object to manage collisions
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    # Draws the rectangle to the screen
    def draw(self, screen, colour):
        pygame.draw.rect(screen, colour, (self.x, self.y, self.width, self.height))
        pygame.draw.lines(screen, black, True, ((self.x, self.y), (self.x+self.width, self.y), (self.x+self.width, self.y+self.height), (self.x, self.y+self.height)))


# Class that models the behaviour of a photon
class Photon:

    # All photon objects are held in this static one-dimensional list
    PhotonList = []
    # Constant value for radius of each photon in pixels
    Radius = 4
    # Static value that keeps track of how many frames it has been since the last photon was emitted
    LastEmitted = 0

    # Photon object takes a tuple of 3 integers between 0 and 255 as the colour
    # Also takes a real number as the kin_energy to represent the kinetic energy of the photon
    def __init__(self, colour, source, kin_energy):
        self.colour = colour
        self.kinEnergy = kin_energy
        # Randomises x and y co-ords along the bottom of the light source image
        rx, ry = self.random_normal(source)
        self.x = source.x  + rx#random.randint(0, 180)
        self.y = source.y  + ry#random.randint(0, 100)
        # the speed variables represent how many pixels the photon moves in each axis per frame
        self.h_speed = -10
        self.v_speed = 4
        # Creates a pygame Rect object to handle collisions with metal terminal
        self.rect = pygame.Rect(self.x, self.y, 2*Photon.Radius, 2*Photon.Radius)

    # Destroys the object by removing itself by the list then deleting itself
    def destroy(self):
        index = self.find_self()
        Photon.PhotonList.pop(index)
        del self

    # Method that creates two random numbers following a normal distribution using Box Muller transform
    # Returns a tuple of the two numbers
    # Parameters are source.mean and source.std
    def random_normal(self, source):
        u1 = random.random()
        u2 = random.random()
        z1 = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
        z2 = math.sqrt(-2 * math.log(u1)) * math.sin(2 * math.pi * u2)
        return z1 * source.std + source.mean, z2 * source.std + source.mean


    # Allows a photon to find itself in the PhotonList by comparing itself to each item in the list
    # Returns the index of that photon in the PhotonList
    def find_self(self):
        index = -1
        for i in range(len(Photon.PhotonList)):
            if Photon.PhotonList[i] == self:
                index = i
                break
        return index

    # Alters the x and y co-ords of the photon by the respective speed variable
    def move(self):
        self.x += self.h_speed
        self.y += self.v_speed
        # Moves the pygame Rect object for collisions
        self.rect.move_ip(self.h_speed, self.v_speed)

    # Checks if the photon object's collision Rect collides with the parameter rect
    # Takes stop_voltage for should_create_electron
    # If collision detected, checks if electron should be made
    # Electron object made if necessary, then photon is deleted
    def check_collision(self, rect, stop_voltage):
        if self.rect.colliderect(rect):
            if self.should_create_electron(stop_voltage):
                self.create_electron()
            self.destroy()
        # If photon goes off screen (either too far left or too far right) then it is deleted
        elif self.x < -2*Photon.Radius or self.y > 800 + 2*Photon.Radius:
            self.destroy()

    # Creates an electron object with the same y co-ord and kinetic energy
    def create_electron(self):
        Electron.ElectronList.append(Electron(self.y, self.kinEnergy))

    # If the kinetic energy of the photon (minus stopping voltage) is greater than 0, returns true
    def should_create_electron(self, stop_voltage):
        stop_voltage = stop_voltage * 1.6 * math.pow(10, -19)
        if (self.kinEnergy - stop_voltage) > 0 * math.pow(10, -19):
            # Only affects actual variable once electron is about to be made
            # Prevents stopping voltage being taken away multiple times
            self.kinEnergy = self.kinEnergy - stop_voltage
            return True
        else:
            return False

    # Draws a circle to the screen to represent the photon
    def draw(self, screen):
        pygame.draw.circle(screen, self.colour, (self.x, self.y), Photon.Radius)


# Class to model an electron particle
class Electron:

    # The one-dimensional list of all electrons between the 2 metal plates
    ElectronList = []
    # The one-dimensional list of all electrons that have hit the right metal plate in the last second
    # Constant value used in drawing the circle that represents the electron
    Radius = 5
    # Constant value for the mass of an electron
    Mass = 9.11 * math.pow(10, -31)

    # Takes in the y co-ord and kinetic energy as parameters
    def __init__(self, y, kin_energy):
        self.kinEnergy = kin_energy
        self.x = 60
        self.y = y
        self.draw_x = round(self.x)
        self.draw_y = round(self.y)
        # Creates a pygame Rect object to handle collisions
        self.rect = pygame.Rect(self.draw_x, self.draw_y, 2 * Electron.Radius, 2 * Electron.Radius)
        # Gets the speed of the electron in pixels per frame by multiplying it by 10^19
        self.speed = kin_energy * math.pow(10, 19)

    # Destroys electron by removing from ElectronList then deleting it
    def destroy(self):
        index = self.find_self()
        Electron.ElectronList.pop(index)
        del self

    # Finds self in ElectronList by comparing each object to itself then returns the index
    def find_self(self):
        index = -1
        for i in range(len(Electron.ElectronList)):
            if Electron.ElectronList[i] == self:
                index = i
                break
        return index

    # Changes the x co-ord and the top-left co-ord of the Rect of the electron by its speed
    # Only moves in x axis, electrons moving horizontally only.
    def move(self):
        self.x += self.speed
        self.draw_x = round(self.x)
        self.rect = pygame.Rect(self.draw_x, self.draw_y, 2 * Electron.Radius, 2 * Electron.Radius)

    # If the electron is colliding with the Rect parameter rect
    # Deletes electron object
    def check_pos(self, rect):
        if self.rect.colliderect(rect):
            self.destroy()

    # Draws a circle to represent the electron
    def draw(self, screen):
        # Draw inner part
        pygame.draw.circle(screen, (60, 230, 255), (self.draw_x, self.draw_y), Electron.Radius - 1)
        # Draw border
        pygame.draw.circle(screen, (0, 0, 0), (self.draw_x, self.draw_y), Electron.Radius, 2)


# Class to represent a metal
class Metal:

    # Static list of metal objects
    MetalList = []
    # Static list of the names of all metal objects
    MetalNames = []

    # Parameters:
    # name - The Metal's name
    # work_func - The work function of the metal
    # colour - an tuple of 3 ints from 0-255 to represent an RGB colour
    def __init__(self, name, work_func, colour):
        self.name = name
        self.work_func = work_func
        self.colour = colour
        # On Initialisation adds the metal's name to a list of metal names
        Metal.MetalNames.append(name)

# Class to represent a light source
class Source:

    # Static list of source objects
    SourceList = []
    # Static list of the names of all light source objects
    SourceNames = []

    # Parameters:
    # name - The Source's name
    def __init__(self, name, x, y, mean, std, min=100, max=850):
        self.name = name
        self.x = x
        self.y = y
        self.mean = mean
        self.std = std
        self.min = min
        self.max = max
        # On Initialisation adds the light source's name to a list of light source names
        Source.SourceNames.append(name)


# Beginning of actual code
# Initialise all pygame modules before they can be used
pygame.init()

# These variables hold the dimensions of the screen, should be kept constant
display_width = 800
display_height = 600

# Colour definitions for referring to later
black = (0, 0, 0)
white = (255, 255, 255)
grey = (100, 100, 100)
lightGrey = (180, 180, 180)

# Initialise main drawing surface
screen = pygame.display.set_mode((display_width, display_height))
# Set title of window
pygame.display.set_caption("Photoelectric Effect Simulator")
# Create clock object for timing
clock = pygame.time.Clock()

# Tuple of min wavelengths for UV, violet, blue, cyan, yellow and red
wlValues = (850, 750, 620, 570, 495, 450, 380, 0)
wlValues2 = (0, 380, 450, 495, 570, 620, 750, 850)


# Basic method to convert a string to an integer
def get_int_from_str(text):
    # Try statement catches errors in case of invalid input
    try:
        i = int(text)
    except ValueError:
        i = 0
    return i


# Basic method to convert a string to a float
def get_float_from_string(text):
    # Try statement catches error in case of invalid input
    try:
        i = float(text)
    except ValueError:
        i = 0
    return i


# Called 30 times a second to check if an photon should be emitted
def emit_photon(current_metal, current_source, intensity, wavelength):
    # firstly checks if intensity is above 0, if not, no photons are being released
    if intensity > 0:
        # Photon.LastEmitted is a timer, whenever it reaches 0, a photon should be emitted
        if Photon.LastEmitted == 0:
            if current_source.min <= wavelength * math.pow(10, 9) <= current_source.max:
                # Creates frequency, needed for calculations
                frequency = (3 * math.pow(10, 8)) / wavelength
                # Determines the total energy of an electron
                tot_energy = (6.62607004 * math.pow(10, -34)) * frequency
                # Kinetic energy is leftover energy from breaking off of surface of metal.
                # If its positive, it has escaped the metal surface
                kin_energy = tot_energy - current_metal.work_func
                # Creates a new Photon
                Photon.PhotonList.append(Photon((set_light_colour(wavelength)), current_source, kin_energy))
                # Sets LastEmitted to a value inversely proportional to intensity
                # Higher the intensity, the sooner the next photon with be released
                Photon.LastEmitted = math.ceil((1/intensity) * 100)
        else:
            # If timer not yet at 0, decrement it
            Photon.LastEmitted -= 1


# Given a string name, finds the first metal in the MetalList that has the same name
# Returns that metal object
def find_metal(name):
    new_metal = None
    for m in Metal.MetalList:
        if name == m.name:
            new_metal = m
    return new_metal

def find_source(name):
    new_source = None
    for s in Source.SourceList:
        if name == s.name:
            new_source = s
    return new_source


# Adds a new metal object to the MetalList and updates the dropdown box that stores the metals
def add_new_metal(new_metal, drop):
    Metal.MetalList.append(new_metal)
    drop.data = Metal.MetalNames
    drop.options = drop.data
    return drop


# Calculates the alpha value for the colour of the light
# Takes in a wavelength between 100 and 850
# And an intensity between 0 and 100
def set_light_alpha(wavelength, intensity):
    # wMod is the modifier to the alpha that the wavelength causes
    w_mod = 1
    wavelength = wavelength * math.pow(10, 9)
    # If no light, fully transparent
    if intensity == 0:
        return 0
    else:
        # If the wavelength is between 350 and 300 nm, wMod decreases as wavelength does
        if wavelength < 350:
            if wavelength > 300:
                w_mod = 1 - ((350 - wavelength) / 50)
            else:
                # If wavelength below 300nm it's fully transparent as its below wavelength of visible light
                w_mod = 0
        # If the wavelength is between 750 and 800nm, wMod decreases as wavelength increases
        elif wavelength > 750:
            if wavelength < 800:
                w_mod = (800 - wavelength) / 50
            else:
                # If wavelength is above 800nm, it's fully transparent as its above wavelength of visible light
                w_mod = 0
        # alpha is capped at 128 (half of opaque value). Is proportional to intensity and wMod
        alpha = round(100 * (intensity / 100) * w_mod)
        return alpha


# Used in setting the colour of the light and photons
# Uses the tuples min_wavelength and max_wavelength
# These tuples are wavelength boundaries for specific colours
# Given a wavelength, finds the upper and lower bounds of it to find what colour it is
def set_min_max(wavelength):
    min_wavelength = 0
    max_wavelength = 0
    for i in range(len(wlValues) - 1):
        if wavelength <= wlValues[i]:
            min_wavelength = wlValues[i]
            max_wavelength = wlValues[i+1]
    return min_wavelength, max_wavelength


# Returns an RGB colour tuple given a wavelength
# Finds the upper and lower bounds of the colour the wavelength causes
# Sets the colour proportionally to how far the wavelength value is between the boundaries
# For example: if the wavelength is half way between the boundary between yellow and red
# The colour is half-way between yellow and orange
def set_light_colour(wavelength):
    wavelength = wavelength * math.pow(10, 9)
    min_wavelength, max_wavelength = set_min_max(wavelength)
    # In this system, there are 3 colour variables, R G and B
    # One will always by 0, 1 will always be 255 (except for violet)
    # and the other will be var_colour
    # var_colour is highest when the wavelength is at the upper boundary and at lowest at lower boundary
    var_colour = round(((wavelength - min_wavelength) / (max_wavelength - min_wavelength)) * 255)
    r = 0
    g = 0
    b = 0
    # If ir to red
    if min_wavelength == wlValues[0]:
        r = 255
    # If red to yellow
    elif min_wavelength == wlValues[1]:
        r = 255
        g = var_colour
    # If yellow to green
    elif min_wavelength == wlValues[2]:
        r = 255 - var_colour
        g = 255
    # If green to cyan
    elif min_wavelength == wlValues[3]:
        g = 255
        b = var_colour
    # If cyan to blue
    elif min_wavelength == wlValues[4]:
        g = 255 - var_colour
        b = 255
    # If blue to purple
    elif min_wavelength == wlValues[5]:
        r = round((var_colour / 255) * 180)
        b = 255
    # If purple to UV
    elif min_wavelength == wlValues[6]:
        r = 180
        b = 255
    return r, g, b


# Deletes the contents of file f
def delete_file(f):
    f.seek(0)
    f.truncate()

# The main game code is run here
def game_loop():
    # Creating the loop boolean, this is false until the game exits
    game_exit = False

    # Starting value definitions
    wavelength = 0
    intensity = 0

    # Appends default metals to the metal list
    Metal.MetalList.append(Metal("Sodium", 3.65 * math.pow(10, -19), (255,252,238)))
    Metal.MetalList.append(Metal("Copper", 7.53 * math.pow(10, -19), (184, 115, 51)))
    Metal.MetalList.append(Metal("Zinc", 6.89 * math.pow(10, -19), (146,137,138)))
    Metal.MetalList.append(Metal("Magnesium", 5.90 * math.pow(10, -19), (193,194,195)))
    Metal.MetalList.append(Metal("Aluminum", 6.53688 * math.pow(10, -19), (217, 218, 217)))
    Metal.MetalList.append(Metal("Beryllium", 8.0109 * math.pow(10, -19), (139,129,135)))
    Metal.MetalList.append(Metal("Calcium", 4.6463 * math.pow(10, -19), (242,244,232)))
    Metal.MetalList.append(Metal("Gold", 8.1711 * math.pow(10, -19), (212,175,55)))
    Metal.MetalList.append(Metal("Platinum", 1.01738 * math.pow(10, -19), (229, 228, 226)))
    Metal.MetalList.append(Metal("Iron", 7.2098 * math.pow(10, -19), (161,157,148)))
    # Sets starting metal to the first one in the list (sodium)
    current_metal = Metal.MetalList[0]

    # Appends default sources to the metal list
    Source.SourceList.append(Source("Lamp", 500+16, 150+54, 60, 30, min=350))
    Source.SourceList.append(Source("Laser",500+16, 150+84, 60, 1))
    Source.SourceList.append(Source("Led", 500, 150+5, 60, 5, min=400, max=700))
    Source.SourceList.append(Source("Infrared", 478, 150+40, 60, 20, min=700))
    Source.SourceList.append(Source("Bulb", 480, 150+38, 60, 18, min=450, max=650))
    # Sets starting source to the first one in the list (lamp)
    current_source = Source.SourceList[0]

    # Defines the fonts that the program will use for drawing text
    my_font = pygame.font.Font(None, 32)
    small_font = pygame.font.Font(None, 25)

    # Text objects used to describe the different GUI elements
    wave_txt = my_font.render("Wavelength: ", 1, (0, 0, 0))
    wave_txt2 = my_font.render("[nm]", 1, (0, 0, 0))
    intensity_txt = my_font.render("Intensity: ", 1, black)
    intensity_txt2 = my_font.render("[%]", 1, black)
    metal_txt = my_font.render("Metal: ", 1, black)
    source_txt = my_font.render("Source: ", 1, black)
    stop_txt = my_font.render("Stopping Voltage: ", 1, black)
    stop_txt2 = my_font.render("[V]", 1, black)

    # Rectangles on left and right to represent metals
    left_rect = MetalRect(10, 360, 50, 210)
    right_rect = MetalRect(740, 360, 50, 210)

    # Wavelength Slider bar creation
    wv_slider = dan_gui.Slider(175, 5, 525, 25, small_font, (100, 850))
    # Setting default wavelength
    wavelength = wv_slider.get_pos()

    # Intensity slider bar creation
    int_slider = dan_gui.Slider(175, 40, 525, 25, small_font, (0, 100), starting_pos=0)
    # Setting default intensity
    intensity = int_slider.get_pos()
    # Stopping voltage slider creation
    stop_slider = dan_gui.Slider(320, 574, 200, 25, small_font, (-3, 3), 0.5, 1)
    stop_voltage = stop_slider.get_pos()
    # Dropdown menu creation
    metal_drop = dan_gui.DropDown(70, 80, 122, 25, Metal.MetalNames, my_font)
    source_drop = dan_gui.DropDown(335, 80, 88, 25, Source.SourceNames, my_font)
    
    # Adding electron speed text to screen
    speed_obj = my_font.render("Average speed: ####### ", 1, (0, 0, 0))
    speed_txt = my_font.render("[m/s]", 1, black)

    # Creating surface for transparent light texture
    surf = pygame.Surface((display_width, display_height), pygame.SRCALPHA)
    surf.set_alpha(set_light_alpha(wavelength, intensity))

    # Image for the light source
    lamp_img = pygame.image.load("img/"+current_source.name.lower()+".png")


    # All code in this loop runs 30 times a second until the program is closed
    while not game_exit:
        # This gets all events pygame detects in one list
        events = pygame.event.get()
        # Gets the position as a pair of co-ords of the mouse in the current frame
        x, y = pygame.mouse.get_pos()

        # Updates the pointer for each of the sliders
        wv_slider.update(x)
        int_slider.update(x)
        stop_slider.update(x)

        # Input management
        # Checks if each event in the events list matches certain types
        for event in events:
            # Checking for mouse clicked, gives position
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check if the drop down box is changed
                # If it has been changed then the current_metal is set to the metal selected by the drop down box
                if metal_drop.on_click(x, y):
                    name = metal_drop.data[metal_drop.current_opt]
                    current_metal = find_metal(name)
                if source_drop.on_click(x, y):
                    name = source_drop.data[source_drop.current_opt]
                    lamp_img = pygame.image.load("img/"+name.lower()+".png")
                    current_source = find_source(name)
                # Passes mouse co-ords onto sliders when click registered
                wv_slider.on_click(x, y)
                int_slider.on_click(x, y)
                stop_slider.on_click(x, y)

            # Checking for mouse unclicked
            if event.type == pygame.MOUSEBUTTONUP:
                # Triggers the sliders' methods for when a mouse is unclicked
                wv_slider.on_unclick()
                int_slider.on_unclick()
                stop_slider.on_unclick()

                
            # Checking for exit, in event of exit event, the game closes and the loop stops
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
                # game_exit = True


        # ALL CALCULATIONS BELOW HERE
        # Gets the wavelength from the slider
        wavelength = wv_slider.get_pos()
        # Multiplies it to be the correct order of magnitude (nanometres)
        wavelength = wavelength * math.pow(10, -9)
        # Gets RGB values for light according to wavelength
        r, g, b = set_light_colour(wavelength)

        # Sets the intensity to the 2nd slider's value
        intensity = int_slider.get_pos()

        # Gets stopping voltage
        stop_voltage = stop_slider.get_pos()

        # Emits a photon if needed
        emit_photon(current_metal, current_source, intensity, wavelength)

        # Draws white over previous frame
        screen.fill(white)
        # ALL DRAWING BELOW HERE
        # For every photon in the PhotonList
        for photon in Photon.PhotonList:
            # Moves the photon's x and y co-ords
            photon.move()
            # #Draws the photon if the setting for drawing photons is enabled
            photon.draw(screen)
            # Checks if photon has hit left metal plate
            photon.check_collision(left_rect.rect, stop_voltage)

        # Draw Electrons and calculate their average speed using their kinetic energy
        total_ke = 0
        for electron in Electron.ElectronList:
            # Adds each electron's kinetic energy to the total
            total_ke += electron.kinEnergy
            electron.move()
            electron.draw(screen)
            electron.check_pos(right_rect.rect)
        # If the ElectronList is not empty
        if len(Electron.ElectronList) > 0:
            # Calculates average kinetic energy of all electrons
            average_ke = total_ke / len(Electron.ElectronList)
            # Converts kinetic energy to speed
            speed = round(math.sqrt((2*average_ke)/Electron.Mass))
            # Creates a pygame Text object for rendering the speed
            speed_obj = my_font.render(("Average Speed: " + str(speed)), 1, black)

        # Draws background for wavelength, intensity and current metal selectors
        # pygame.draw.rect(screen, lightGrey, (0, 0, 450, 200))
        # Draws border around bottom and right sides of box
        # pygame.draw.lines(screen, black, False, ((0, 200), (450, 200), (450, 0)), 2)
        # Drawing average speed
        screen.blit(speed_obj, (480, 80))
        screen.blit(speed_txt, (746, 80))
        # Left rectangle
        left_rect.draw(screen, current_metal.colour)
        # Right rectangle
        right_rect.draw(screen, current_metal.colour)
        # Wavelength slider prompt
        screen.blit(wave_txt, (3, 5))
        # Wavelength slider
        wv_slider.draw(screen)
        # Wavelength slider suffix
        screen.blit(wave_txt2, (750, 5))
        # Intensity slider prompt
        screen.blit(intensity_txt, (3, 40))
        # Intensity slider suffix
        screen.blit(intensity_txt2, (750, 40))
        # Draw intensity slider
        int_slider.draw(screen)
        # Stopping voltage slider
        stop_slider.draw(screen)
        # Stopping voltage slider prompt
        screen.blit(stop_txt, (100, 574))
        # Stopping voltage slider suffix
        screen.blit(stop_txt2, (540, 574))
        # Metal Text
        screen.blit(metal_txt, (3, 80))
        # Drop down box
        metal_drop.draw(screen)
        screen.blit(source_txt, (253, 80))
        source_drop.draw(screen)

        # Draws light from light source to screen
        # Gets alpha (transparency) value for light
        alpha = set_light_alpha(wavelength, intensity)
        # Combines colour with alpha in 1 tuple
        light_colour = (r, g, b, alpha)
        # Draws light to transparency enabled surface
        pygame.draw.polygon(surf, light_colour, ((60, 400), (60, 550), (700, 380), (512, 202)))
        # Draws transparent surface to screen
        screen.blit(surf, (0, 0))
        # Draws light source image
        screen.blit(lamp_img, (500, 150))

        # Updates the display
        pygame.display.update()

        # Makes the program wait so that the main loop only runs 30 times a second
        clock.tick(30)


# Calls the main loop subroutine to start
if __name__ == "__main__":
    game_loop()
