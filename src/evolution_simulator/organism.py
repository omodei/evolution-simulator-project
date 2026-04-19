# organism.py (Updated with Intelligence)

import random
import numpy as np
import matplotlib.pyplot as plt 
from .config import *
from .dna import DNA
from .species_library import SPECIES

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) # Set to DEBUG to see detailed logs from the organism



class Organism:
    '''Represents an organism in the world with properties derived from its DNA.'''
    def __init__(self, x, y, species_name, dna=None):

        # position:
        self.x = x
        self.y = y
        self.theta = np.random.uniform(0, 2 * np.pi) # Random initial direction (for movement)

        # initial status:
        self.age       = 0
        self.energy    = INITIAL_ENERGY
        self.hydration = INITIAL_HYDRATION
       
        self.is_alive_flag = True

        # --- LOAD FROM TEMPLATE ---
        self.template = SPECIES[species_name]

        self.species_name  = species_name
        self.name          = self.template["name"]
        self.species_color = self.template["color"]
        self.marker        = self.template["marker"]
        self.eats_tags     = self.template["eats_tags"]
        self.genes         = self.template["genes"]

        if dna:
            self.dna = dna 
        else:
            self.dna = DNA()
            for gene in self.genes.keys():
                self.dna.genes[gene] = self.genes[gene]

        self.max_age                       = self.dna.genes['max_age']
        self.vision                        = self.dna.genes['vision']
        self.speed                         = self.dna.genes['speed']
        self.can_move                      = self.speed > 0
        self.reproduction_energy_threshold = self.dna.genes['reproduction_energy_threshold'] * INITIAL_ENERGY 
        self.reproduction_age_threshold    = self.dna.genes['reproduction_age_threshold'] * self.max_age

        self.fitness_score                 = self._calculate_fitness_score()
        self.priority                      = 'k' # 'b': hydration, 'g': eat,  'r': reproduce
        # Get a colormap from matplotlib (e.g., 'viridis', 'inferno', 'plasma')
        cmap = plt.cm.get_cmap('inferno') 
        # The colormap takes a value from 0-1 and returns an RGBA color
        self.color = cmap(self.fitness_score)
        logger.debug(f"Organism {self.name} has fitness score: {self.fitness_score:.2f}")

    def _calculate_fitness_score_gene(self, gene):
        """Calculates a normalized fitness score (0-1) for a specific gene."""
        default = (self.genes[gene] if gene in self.genes.keys() else GENE_DEFAULTS[gene][1])
        if default == 0:
            return 0
        value = self.dna.genes[gene]
        delta = (value - default) / default
        return delta

    def _calculate_fitness_score(self):
        """Calculates a normalized fitness score (0-1) based on key genes."""
        fitness_score = []
        
        
        for gene in GENE_DEFAULTS.keys():
            delta = self._calculate_fitness_score_gene(gene)
            fitness_score.append(delta)
        
        return sum(fitness_score)

    def is_alive(self):
        return self.energy > 0 and self.age < self.dna.genes['max_age'] and self.hydration > 0 and self.is_alive_flag

    def is_thirsty(self):
        return self.hydration < INITIAL_HYDRATION * HYDRATION_URGENCY_THRESHOLD      
    
    def is_hungry(self):
        return self.energy < INITIAL_ENERGY * ENERGY_URGENCY_THRESHOLD
    
    def is_seeking_mate(self):
        return self.energy >= self.reproduction_energy_threshold and self.age >= self.reproduction_age_threshold
    
    def die(self):
        """Marks the organism for removal."""
        self.is_alive_flag = False
        # Maybe add a 'corpse' with nutrients to the world here in the future?

    def drink(self):
        self.hydration += DRINK_HYDRATION_GAIN * self.dna.genes['water_efficiency']
        self.hydration = min(self.hydration, INITIAL_HYDRATION) #

    def eat(self,organism=None):
        if organism:
            self.energy += organism.energy * EAT_ENERGY_GAIN * self.dna.genes['energy_efficiency']
        else:
            self.energy    += EAT_ENERGY_GAIN * self.dna.genes['energy_efficiency']
            
        self.energy    = min(self.energy, INITIAL_ENERGY) # Cap energy at initial max

    def find_closest(self, targets):
        """Finds the closest target from a list of (x, y) coordinates."""
        if not targets:
            return None
        
        closest_target = None
        min_dist_sq = float('inf')

        for tx, ty in targets:
            dist_sq = (self.x - tx)**2 + (self.y - ty)**2
            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                closest_target = (tx, ty)
        
        return closest_target

    def decide_direction(self, world):
        """Intelligent movement based on needs and environment."""
        
        if not self.can_move: return
        target_pos    = None
        self.priority = 'k'
        # 1. Determine highest priority target
        # Priority 1: Thirst

        if self.is_thirsty():
            #logger.debug(f"Organism {self.name} at ({self.x}, {self.y}) is thirsty (Hydration: {self.hydration:.1f}). Seeking water...")
            self.priority='b'
            water_tiles = list(zip(*np.where(world.water_grid[
                max(0, self.x - round(self.vision)): self.x + round(self.vision) + 1,
                max(0, self.y - round(self.vision)): self.y + round(self.vision) + 1
            ] > 0)))
            if water_tiles:
                # Adjust local coordinates back to world coordinates
                offset_x = max(0, self.x - round(self.vision))
                offset_y = max(0, self.y - round(self.vision))
                world_water_tiles = [(x + offset_x, y + offset_y) for x, y in water_tiles]
                target_pos = self.find_closest(world_water_tiles)
                logger.debug(f"Organism {self.name} at ({self.x}, {self.y}) founds water nearby.")
            else:
                logger.debug(f"Organism {self.name} at ({self.x}, {self.y}) sees no water nearby.")

        # Priority 2: Hunger (if not thirsty)
        if target_pos is None and self.is_hungry():
            #logger.debug(f"Organism {self.name} at ({self.x}, {self.y}) is hungry (Energy: {self.energy:.1f}). Seeking food...")
            self.priority='g'
            potential_prey = list(world.organisms) # All organisms are potential prey
            # find the closest prey:
            valid_prey_spicies = self.eats_tags.keys()# Get the tags of what this eater can eat

            valid_prey = [prey for prey in potential_prey if prey.is_alive() and not prey is self and prey.species_name in [tag for tag in valid_prey_spicies]]
            visible_prey = [(p.x, p.y) for p in valid_prey if abs(p.x - self.x) <= self.vision and abs(p.y - self.y) <= self.vision]
            target_pos = self.find_closest(visible_prey)

            if target_pos:
                logger.debug(f"Organism {self.name} at ({self.x}, {self.y}) finds food nearby. Target = {target_pos[0]},{target_pos[1]}")
            else:
                logger.debug(f"Organism {self.name} at ({self.x}, {self.y}) sees no food nearby.")
     
        if target_pos is None and self.is_seeking_mate():
            #logger.debug(f"Organism {self.name} at ({self.x}, {self.y}) is seeking a mate (Energy: {self.energy:.1f}).")
            self.priority='r'
            mates = [org for org in world.organisms if org is not self and org.name == self.name and org.is_seeking_mate() and org.is_alive()]
            visible_mates = [(m.x, m.y) for m in mates if abs(m.x - self.x) <= self.vision and abs(m.y - self.y) <= self.vision]
            target_pos = self.find_closest(visible_mates)
            if target_pos:
                logger.debug(f"Organism {self.name} at ({self.x}, {self.y}) finds a mate nearby.")
            else:
                logger.debug(f"Organism {self.name} at ({self.x}, {self.y}) sees no mates nearby.")

        # 2. Decide the step (dx, dy)
        dx, dy = 0, 0

        if target_pos:
            # Move towards the target
            dx = (target_pos[0] - self.x)
            dy = (target_pos[1] - self.y)
            self.theta = np.arctan2(dy, dx)
            speed = min(self.speed, np.sqrt((dx)**2 + (dy)**2))
        else:
            # Fallback: Brownian motion if no target is in sight
            #theta = random.uniform(0, 2 * np.pi)
            speed = self.speed * 0.5 # Move slower when wandering
            pass
        dx = speed * np.cos(self.theta)
        dy = speed * np.sin(self.theta)

        return dx, dy


    def move(self, world):
        """Moves the organism based on its intelligence."""
        dx, dy = self.decide_direction(world) 
        # 3. Apply the move
        self.x = round(self.x + dx) % WORLD_SIZE[0]
        self.y = round(self.y + dy) % WORLD_SIZE[1]


    # def spawn(self, world):
    #     """Creates a new organism with combined DNA from self and self."""
        
    #     # Spawn the child in an adjacent cell (if possible)
    #     my_list = [(-1,1), (0,1), (1,1), (-1,0), (1,0), (-1,-1), (0,-1), (1,-1)]
    #     dx, dy = random.choice(my_list)
    #     new_x, new_y = (self.x + dx) % WORLD_SIZE[0], (self.y + dy) % WORLD_SIZE[1] 
    #     if self.capabilities.get("requires_water_tile") and world.water_grid[new_x, new_y] == 0:
    #         return False
        
    #     if not any(org.x == new_x and org.y == new_y for org in world.organisms):
    #         child_dna = DNA.mix_and_mutate(self.dna, self.dna) # Self-reproduction (asexual) - can be used for plants or simple organisms
    #         child = Organism(new_x, new_y, self.species_name, dna=child_dna)
    #         world.add_organism(child)
    #         self.energy -= self.capabilities["can_spawn"]["cost"] # Pay the energy cost for spawning
    #         return True
        
    #     return False # No space to spawn

    def update(self, world): # <-- IMPORTANT: must accept the world object
        """Update organism state for one tick."""
        self.age       += 1
        self.energy    -= ENERGY_PER_TICK
        self.hydration -= HYDRATION_PER_TICK

        if not self.is_alive():
            return
        
        # if self.capabilities.get("requires_water_tile") and world.water_grid[self.x, self.y] == 0:
        #     self.die() # Dies if not in water
        #     return

        # if "photosynthesize" in self.capabilities:
        #     self.energy += self.capabilities["photosynthesize"]["energy_gain"]


        if self.can_move:
            # Your intelligent movement logic here
            self.move(world) 

        # if self.can_spawn():
        #     self.spawn(world)

        if self.is_alive():
            self.move(world) # <-- Pass the world to the move method

    def __str__(self):
        #return f"Organism at ({self.x}, {self.y}) | Age: {self.age} | Energy: {self.energy:.1f}/{self.dna.genes['energy_urgency_threshold']:.1f} | Hydration: {self.hydration:.1f}/{self.dna.genes['hydration_urgency_threshold']:.1f} | Diet: {'Carnivore' if self.diet_type == 1 else 'Herbivore'} | Fitness: {self.fitness_score:.2f}, Priority: {self.priority}"

        txt=f"{self.name} at ({self.x}, {self.y}) | Age: {self.age:d}, Energy: {self.energy:.1f}, Hydration: {self.hydration:.1f}, Fitness: {self.fitness_score:.2f}, Priority: {self.priority}"
        #for g in self.dna.genes.keys():
        #    txt+=f" | {g}: {self.dna.genes[g]:.1f}"
        return txt

