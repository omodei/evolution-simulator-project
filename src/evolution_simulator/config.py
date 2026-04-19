# config.py
import numpy as np
LOGGER_LEVEL="INFO" # "DEBUG" or "INFO"
STEP_BY_STEP = 0 # If True, the simulation will pause after each tick until the user presses Enter. Useful for debugging.
PLOT_ANIMATION = 1 # If True, the simulation will display an animation of the world.
# Simulation settings
RANDOM_SEED      = np.random.randint(0, 1000000) # You can set this to a fixed number for reproducibility
SIMULATION_TICKS = 10000 # Increased ticks to see evolution happen

# World settings
# --- NEW WORLD GENERATION SETTINGS ---
NOISE_SCALE           = 150.0       # Higher = more zoomed in, larger landmasses/lakes
NOISE_OCTAVES         = 4        # Adds more detail to the noise
WATER_LEVEL_THRESHOLD = 0.05 # Noise values above this become water (range is approx -0.7 to 0.7)
WORLD_SIZE            = (100, 100)  # (width, height)

# Organism settings
INITIAL_ENERGY        = 100
INITIAL_HYDRATION     = 100
HYDRATION_PER_TICK    = 2  # How much hydration is lost per tick
ENERGY_PER_TICK       = 1  # How much energy is lost per tick
REPRODUCTION_COST     = 0.1 # How much energy it costs to reproduce (can be overridden by species capabilities)
EAT_ENERGY_GAIN       = 10 # Base energy gain from eating (can be overridden by species capabilities)
DRINK_HYDRATION_GAIN  = 10 # Base hydration gain from drinking (can be overridden by species capabilities)

HYDRATION_URGENCY_THRESHOLD    = 0.2 # Below this hydration level, finding water is top priority.
ENERGY_URGENCY_THRESHOLD       = 0.2 # Below this energy level, finding food is top priority.

INTERACTION_RADIUS = 1.5 # How close organisms must be to interact (eat, reproduce, etc.)
# NON DNA SETTINGS (constants that don't evolve)
# --- NEW DNA/MUTATION SETTINGS ---
MUTATION_RATE   = 0.05 # 5% chance for a gene to mutate in a child
MUTATION_AMOUNT = 0.1# How much a gene can mutate (e.g., +/- 10%)

# THESE ARE THE DEFAULT VALUES, MINIMUM AND MAXIMUM  FOR THE GENES DEFINITIIONS:
GENE_DEFAULTS = {
                'max_age':   (100, False),
                'energy_efficiency':(0.5, False),
                'water_efficiency': (0.5, False),
                'vision':    (10, False), # How many cells an organism can "see" in each direction.
                'speed':     (5, False),  # How many cells an organism can move per tick
                'reproduction_energy_threshold': (0.6, False), # Energy level at which an organism will seek to reproduce
                'reproduction_age_threshold': (0.2, False), # Age at which an organism can start reproducing
            }

# In your config.py, you would define this:
    
INITIAL_POPULATION = {
    "A": 100,
    "B": 100,
    "C": 100,
    "D": 100,
    "E": 100,
    "F": 100,
    "G": 100,
    "H": 100,
    "I": 100,
    "J": 100,
}

import logging 

# --- NEW: Configure Logging ---
# This sets up a logger that writes to a file named 'simulation.log'.
# The file is overwritten on each run (filemode='w').
logging.basicConfig(
    level=logging.INFO,  # Set the minimum level of messages to log (e.g., INFO, DEBUG)
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename='simulation.log', # Log to this file
    filemode='w' # Overwrite the log file each time
)

# Also add a console handler to see logs in the terminal as they happen
console_handler = logging.StreamHandler()

console_handler.setLevel(LOGGER_LEVEL)

formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console_handler.setFormatter(formatter)
logging.getLogger('').addHandler(console_handler)