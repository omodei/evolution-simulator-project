# config.py
LOGGER_LEVEL="INFO" # "DEBUG" or "INFO"
PLOT_FOOD=0
# Simulation settings
RANDOM_SEED      = 5
SIMULATION_TICKS = 100000 # Increased ticks to see evolution happen

# World settings
# --- NEW WORLD GENERATION SETTINGS ---
NOISE_SCALE           = 150.0       # Higher = more zoomed in, larger landmasses/lakes
NOISE_OCTAVES         = 4        # Adds more detail to the noise
WATER_LEVEL_THRESHOLD = 0.05 # Noise values above this become water (range is approx -0.7 to 0.7)
WORLD_SIZE            = (256, 256)  # (width, height)

# --- NEW FOOD SETTINGS ---
# Max food units as a percentage of world area
MAX_FOOD_PERCENTAGE = 0.05
MAX_FOOD_UNITS      = int(WORLD_SIZE[0] * WORLD_SIZE[1] * MAX_FOOD_PERCENTAGE)
# How many food items can appear each tick
FOOD_REPLENISH_RATE = 10
FOOD_INITIAL_NUMBER = 10

# Organism settings
INITIAL_ORGANISMS       = 100
INITIAL_CARNIVORE_RATIO = 0.0 # 20% of initial organisms will be carnivores
MAX_AGE            = 250
INITIAL_ENERGY     = 100
INITIAL_HYDRATION  = 100
HYDRATION_PER_TICK = 2  # How much hydration is lost per tick
ENERGY_PER_TICK    = 1  # How much energy is lost per tick

# NON DNA SETTINGS (constants that don't evolve)
# --- NEW DNA/MUTATION SETTINGS ---
MUTATION_RATE   = 0.5 # 5% chance for a gene to mutate in a child
MUTATION_AMOUNT = 0.1 # How much a gene can mutate (e.g., +/- 10%)
DRINK_AMOUNT            = 50  # How much hydration is gained by drinking

# all thgis ARE the bseis for DNA genes, so they can be mutated and evolved over time
CARNIVORE_ENERGY_GAIN   = 50  # Energy gained by a carnivore from eating an herbivore
EAT_ENERGY_GAIN         = 50
HUNTING_RADIUS          = 2 # Same as proximity for now, but can be its own gene later!
SPEED                   = 2   # How many cells an organism can move per tick
# The "intensity" of the Brownian motion. Higher values mean larger, more erratic jumps.
#BROWNIAN_MOTION_SIGMA = 2
# --- NEW INTELLIGENCE SETTINGS ---
VISION_RANGE                   = 10 # How many cells an organism can "see" in each direction.
HYDRATION_URGENCY_THRESHOLD    = 50 # Below this hydration level, finding water is top priority.
ENERGY_URGENCY_THRESHOLD       = 60 # Below this energy level, finding food is top priority.
REPRODUCTION_URGENCY_THRESHOLD = 70 # Below this level, organisms prioritize reproduction.
CARNIVORE_AGE_THRESHOLD        = 50 # Minimum age before an organism can be a carnivore (to prevent newborns from being born as carnivores and immediately dying)
# --- NEW REPRODUCTION/EVOLUTION SETTINGS ---
PROXIMITY_RADIUS              = 2 # How close organisms must be to reproduce (<= 1.414 for adjacent cells)
REPRODUCTION_ENERGY_THRESHOLD = 10 # Energy level required to be able to reproduce
REPRODUCTION_AGE_THRESHOLD    = 100 # Age level required to be able to reproduce
REPRODUCTION_ENERGY_COST      = 20 # Energy lost by each parent during reproduction

GENE_FITNESS_CONFIG = {
    # Trait: ([min_val, max_val], direction)
    'max_age': ([MAX_AGE * 0.5, MAX_AGE * 1.5], 1.0),
    'energy_efficiency': ([0.6, 1.4], -1.0), # Lower is better
    'hydration_efficiency': ([0.6, 1.4], -1.0), # Lower is better
    'eat_energy_gain': ([EAT_ENERGY_GAIN * 0.5, EAT_ENERGY_GAIN * 1.5], 1.0),
    'carnivore_energy_gain': ([CARNIVORE_ENERGY_GAIN * 0.5, CARNIVORE_ENERGY_GAIN * 1.5], 1.0),
    'hunting_radius': ([HUNTING_RADIUS * 0.5, HUNTING_RADIUS * 2], 1.0),
    'speed': ([SPEED * 0.5, SPEED * 2], 1.0), # (Assuming you added SPEED to config)
    'vision_range': ([VISION_RANGE * 0.5, VISION_RANGE * 2], 1.0),
    'reproduction_energy_cost': ([REPRODUCTION_ENERGY_COST * 0.5, REPRODUCTION_ENERGY_COST * 1.5], -1.0), # Lower is better
}
