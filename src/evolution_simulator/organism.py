# organism.py (Updated with Intelligence)

import random
import numpy as np
import matplotlib.pyplot as plt 
from config import *
from dna import DNA
import logger 

logger = logger.logger()

class Organism:
    # __init__ is mostly the same
    def __init__(self, x, y, dna=None):
        self.x = x
        self.y = y
        self.age = 0
        self.energy    = INITIAL_ENERGY
        self.hydration = INITIAL_HYDRATION
        self.dna = dna if dna else DNA()
        # ... (derive properties from DNA as before)
        self.max_age    = self.dna.genes['max_age']
        self.energy_efficiency             = self.dna.genes['energy_efficiency']
        self.hydration_efficiency          = self.dna.genes['hydration_efficiency']
        self.reproduction_energy_threshold = self.dna.genes['reproduction_energy_threshold']
        self.reproduction_age_threshold    = self.dna.genes['reproduction_age_threshold']
        self.reproduction_energy_cost      = self.dna.genes['reproduction_energy_cost']
        self.diet_type                     = self.dna.genes['diet_type']
        self.fitness_score                 = self._calculate_fitness_score()
        self.priority                      = 'k' # 'b': hydration, 'g': eat,  'r': reproduce
        # Get a colormap from matplotlib (e.g., 'viridis', 'inferno', 'plasma')
        cmap = plt.cm.get_cmap('inferno') 
        # The colormap takes a value from 0-1 and returns an RGBA color
        self.color = cmap(self.fitness_score)

    def _calculate_fitness_score(self):
        """Calculates a normalized fitness score (0-1) based on key genes."""
        normalized_scores = []
        
        for gene, (min_max, direction) in GENE_FITNESS_CONFIG.items():
            if gene not in self.dna.genes:
                continue

            value = self.dna.genes[gene]
            min_val, max_val = min_max

            # Clamp the value to be within the expected range
            clamped_value = max(min_val, min(max_val, value))

            # Normalize the value to a 0-1 scale
            norm_score = (clamped_value - min_val) / (max_val - min_val)

            # Invert the score if a lower value is better
            if direction == -1.0:
                norm_score = 1.0 - norm_score
            
            normalized_scores.append(norm_score)

        # Return the average of all normalized scores
        if not normalized_scores:
            return 0.5 # Return a neutral score if no genes matched
        
        return sum(normalized_scores) / len(normalized_scores)


    # is_alive, drink, can_reproduce are unchanged
    def is_alive(self):
        return self.energy > 0 and self.age < self.max_age and self.hydration > 0

    def drink(self):
        self.hydration = min(self.hydration + DRINK_AMOUNT, INITIAL_HYDRATION)

    def can_reproduce(self):
        return self.energy >= self.reproduction_energy_threshold and self.age >= self.reproduction_age_threshold

    def find_closest(self, targets, world):
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

    def move(self, world):
        """Intelligent movement based on needs and environment."""
        target_pos = None
        self.priority='k'
        # 1. Determine highest priority target
        # Priority 1: Thirst

        if self.hydration < self.dna.genes['hydration_urgency_threshold']:
            logger.log(f"Organism at ({self.x}, {self.y}) is thirsty (Hydration: {self.hydration:.1f}). Seeking water...")
            self.priority='b'
            water_tiles = list(zip(*np.where(world.water_grid[
                max(0, self.x - round(self.dna.genes['vision_range'])):self.x + round(self.dna.genes['vision_range']) + 1,
                max(0, self.y - round(self.dna.genes['vision_range'])):self.y + round(self.dna.genes['vision_range']) + 1
            ] > 0)))
            if water_tiles:
                # Adjust local coordinates back to world coordinates
                offset_x = max(0, self.x - round(self.dna.genes['vision_range']))
                offset_y = max(0, self.y - round(self.dna.genes['vision_range']))
                world_water_tiles = [(x + offset_x, y + offset_y) for x, y in water_tiles]
                target_pos = self.find_closest(world_water_tiles, world)
            else:
                logger.log(f"Organism at ({self.x}, {self.y}) sees no water nearby.")

        # Priority 2: Hunger (if not thirsty)
        if target_pos is None and self.energy < self.dna.genes['energy_urgency_threshold']:
            logger.log(f"Organism at ({self.x}, {self.y}) is hungry (Energy: {self.energy:.1f}). Seeking food...")
            self.priority='g'
            # Herbivore seeks food
            if self.diet_type == 0:
                food_tiles = list(zip(*np.where(world.food_grid[
                    max(0, self.x - round(self.dna.genes['vision_range'])):self.x + round(self.dna.genes['vision_range']) + 1,
                    max(0, self.y - round(self.dna.genes['vision_range'])):self.y + round(self.dna.genes['vision_range']) + 1
                ] > 0)))
                if food_tiles:
                    offset_x = max(0, self.x - round(self.dna.genes['vision_range']))
                    offset_y = max(0, self.y - round(self.dna.genes['vision_range']))
                    world_food_tiles = [(x + offset_x, y + offset_y) for x, y in food_tiles]
                    target_pos = self.find_closest(world_food_tiles, world)
                else:
                    logger.log(f"Organism at ({self.x}, {self.y}) sees no food nearby.")
            # Carnivore seeks prey
            elif self.diet_type == 1:
                prey = [org for org in world.organisms if org.diet_type == 0 and org.is_alive()]
                visible_prey = [(p.x, p.y) for p in prey if abs(p.x - self.x) <= self.dna.genes['vision_range'] and abs(p.y - self.y) <= self.dna.genes['vision_range']]
                target_pos = self.find_closest(visible_prey, world)
            else:
                logger.log(f"Organism at ({self.x}, {self.y}) sees no food nearby.")

        if target_pos is None:
            # Priority 3: Reproduction (if not thirsty or hungry)
            if self.energy >= self.dna.genes['reproduction_energy_threshold'] and self.age >= self.dna.genes['reproduction_age_threshold']:
                logger.log(f"Organism at ({self.x}, {self.y}) is seeking a mate (Energy: {self.energy:.1f}).")
                self.priority='r'
                mates = [org for org in world.organisms if org is not self and org.diet_type == self.diet_type and org.can_reproduce() and org.is_alive()]
                visible_mates = [(m.x, m.y) for m in mates if abs(m.x - self.x) <= self.dna.genes['vision_range'] and abs(m.y - self.y) <= self.dna.genes['vision_range']]
                target_pos = self.find_closest(visible_mates, world)
        # 2. Decide the step (dx, dy)
        dx, dy = 0, 0
        speed = random.uniform(0,self.dna.genes['speed'])

        if target_pos:
            # Move towards the target
            dx = np.sign(target_pos[0] - self.x)
            dy = np.sign(target_pos[1] - self.y)
        else:
            # Fallback: Brownian motion if no target is in sight
            dx = random.uniform(-1,1)
            dy = random.uniform(-1,1)

        # 3. Apply the move
        self.x = round(self.x + speed * dx) % WORLD_SIZE[0]
        self.y = round(self.y + speed * dy) % WORLD_SIZE[1]

    def update(self, world): # <-- IMPORTANT: must accept the world object
        """Update organism state for one tick."""
        self.age       += 1
        self.energy    -= ENERGY_PER_TICK    * self.energy_efficiency
        self.hydration -= HYDRATION_PER_TICK * self.hydration_efficiency
        
        if self.is_alive():
            self.move(world) # <-- Pass the world to the move method
    def __str__(self):
        return f"Organism at ({self.x}, {self.y}) | Age: {self.age} | Energy: {self.energy:.1f}/{self.dna.genes['energy_urgency_threshold']:.1f} | Hydration: {self.hydration:.1f}/{self.dna.genes['hydration_urgency_threshold']:.1f} | Diet: {'Carnivore' if self.diet_type == 1 else 'Herbivore'} | Fitness: {self.fitness_score:.2f}, Priority: {self.priority}"
        pass