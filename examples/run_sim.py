# run_sim.py (Updated with Live Graph)

import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from evolution_simulator.config import *
from evolution_simulator.world import World
from evolution_simulator.organism import Organism

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
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console_handler.setFormatter(formatter)
logging.getLogger('').addHandler(console_handler)

def setup_simulation():
    """Initializes the world and populates it with organisms."""
    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)
    
    logging.info("Setting up simulation...")
    simulation_world = World(WORLD_SIZE)
    
    for _ in range(INITIAL_ORGANISMS):
        x = random.randint(0, WORLD_SIZE[0] - 1)
        y = random.randint(0, WORLD_SIZE[1] - 1)
        simulation_world.add_organism(Organism(x, y))
        
    logging.info(f"Created {len(simulation_world.organisms)} organisms.")
    return simulation_world

def run_simulation():
    """Runs the main simulation loop and handles visualization for the world and population graph."""
    world = setup_simulation()
    
    # --- STEP 1: Setup for two subplots (world and graph) ---
    plt.ion()
    # Create a figure with two subplots, side-by-side. Increase figure size for clarity.
    fig, (ax_world, ax_graph) = plt.subplots(1, 2, figsize=(16, 8))
    ax_fitness = ax_graph.twinx()

    water_cmap = mcolors.LinearSegmentedColormap.from_list("water_cmap", ["saddlebrown", "blue"])

    # --- STEP 2: Initialize lists to store population history ---
    history_time = []
    history_herbivores = []
    history_carnivores = []
    history_total = []
    history_avg_fitness = []

    for tick in range(SIMULATION_TICKS):
        #print(f"--- Tick {tick + 1}/{SIMULATION_TICKS} ---", end=" ")
        
        # 1. Update the world state
        world.update_world()
        
        #food_x, food_y = np.where(world.food_grid == -1) 
        #ax_world.scatter(food_x, food_y, color='red', s=30, marker='s')

        
        herbivores = [org for org in world.organisms if org.diet_type == 0]
        carnivores = [org for org in world.organisms if org.diet_type == 1]
        pop_h = len(herbivores)
        pop_c = len(carnivores)
        total_fitness_score = sum(org.fitness_score for org in world.organisms)
        avg_fitness_score = total_fitness_score / len(world.organisms) if world.organisms else 0
        # Append current data to history lists

        history_time.append(tick)
        history_herbivores.append(pop_h)
        history_carnivores.append(pop_c)
        history_total.append(pop_h + pop_c)
        history_avg_fitness.append(avg_fitness_score)
        WINDOW_SIZE=10000
        if tick>WINDOW_SIZE:
            history_time.pop(0) 
            history_herbivores.pop(0)  
            history_carnivores.pop(0)  
            history_total.pop(0)  
            history_avg_fitness.pop(0)  
    
        if tick < 100 or (tick % 10 ==0):
            logging.info(f"Tick: {tick:>4} | Pop: {pop_h+pop_c} (H: {pop_h}, C: {pop_c}) | Avg Fitness: {avg_fitness_score:.2f}")

        if pop_h+pop_c < 200 or (tick % 10 == 0): # Print population every 10 ticks, but only if it's not too large
            plot=True
        else:
            plot=False  
        # --- RENDER THE WORLD (using ax_world) ---
        if plot:
            ax_world.clear()
            ax_world.imshow(world.water_grid.T, cmap=water_cmap, origin='lower', alpha=0.6)
        
            if PLOT_FOOD: 
                food_x, food_y = np.where(world.food_grid == 1) 
                ax_world.scatter(food_x, food_y, color='green', s=10, marker='.',facecolors='None', alpha=0.6)

            if herbivores: # Only plot organisms if population is not too large (for performance)
                ax_world.scatter([org.x for org in herbivores], [org.y for org in herbivores], 
                        c=[org.color for org in herbivores],
                        s=[50.0*org.energy / INITIAL_ENERGY for org in herbivores], 
                        marker='o', 
                        edgecolors=[org.priority for org in herbivores], 
                        linewidths=1, alpha=[1 - org.age / org.max_age for org in herbivores]) # Size and alpha based on energy

            if carnivores: # Only plot organisms if population is not too large (for performance):
                ax_world.scatter([org.x for org in carnivores], [org.y for org in carnivores], 
                        c=[org.color for org in carnivores], 
                        s=[50.0*org.energy / INITIAL_ENERGY for org in carnivores], 
                        marker='*', 
                        edgecolors=[org.priority for org in carnivores], 
                        linewidths=1, alpha=[1 - org.age / org.max_age for org in carnivores]) # Size and alpha based on energy


            ax_world.set_title(f"World | Pop: {pop_h+pop_c} (H: {pop_h}, C: {pop_c})")
            ax_world.set_xlim(0, WORLD_SIZE[0])
            ax_world.set_ylim(0, WORLD_SIZE[1])
        
            # --- STEP 3: Store data and render the graph (using ax_graph) ---

            # Clear the previous graph
            ax_graph.clear()
            ax_fitness.clear()
            # Plot the data
            ax_graph.plot(history_time, history_herbivores, color='limegreen', label='Herbivores')
            ax_graph.plot(history_time, history_carnivores, color='crimson', label='Carnivores')
            ax_graph.plot(history_time, history_total, color='black', linestyle='--', label='Total')
            ax_fitness.plot(history_time, history_avg_fitness, color='deepskyblue', label='Avg. Fitness')

            # Style the graph
            ax_graph.set_title("Population & Fitness Over Time")
            ax_graph.set_xlabel("Tick")
            ax_graph.set_ylabel("Count")
            # Set the Y-label for the right axis
            ax_fitness.set_ylabel("Average Fitness (0-1)", color='deepskyblue')
            ax_fitness.tick_params(axis='y', labelcolor='deepskyblue')
            ax_fitness.set_ylim(0, 1) # Lock the fitness axis

           # --- NEW: Combine legends from both axes ---
            h1, l1 = ax_graph.get_legend_handles_labels()
            h2, l2 = ax_fitness.get_legend_handles_labels()
            ax_graph.legend(h1 + h2, l1 + l2, loc='upper left')
            ax_graph.grid(True)
            ax_graph.set_xlim(left=history_time[0], right=max(100, tick)) # Keep x-axis from getting too small
            
            # Adjust layout to prevent titles/labels overlapping
            plt.tight_layout()
            plt.pause(0.01) # Pause briefly to update the plot

        if not world.organisms and tick > 50:
            logging.info("All organisms have died. Ending simulation.")
            break
            
    plt.ioff()
    logging.info("Simulation finished. Displaying final state.")
    plt.show()

if __name__ == "__main__":
    run_simulation()