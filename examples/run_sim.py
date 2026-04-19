# run_sim.py

import logging
import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from evolution_simulator.config import *
from evolution_simulator.world import World
from evolution_simulator.organism import Organism
from evolution_simulator.species_library import SPECIES


def replanish_speces(simulation_world):
    """Replenishes species A, B, and C at the start of the simulation."""
    # NEW way to populate the world
    for species_name, count in INITIAL_POPULATION.items():
        for _ in range(count):            
            # For aquatic species, spawn them in water
            water_coords = list(zip(*np.where(simulation_world.water_grid > 0)))
            if SPECIES[species_name].get("capabilities", {}).get("requires_water_tile"):
                # (You need a robust way to find a water tile here)
                if not water_coords: continue # No water on map, can't spawn
                x, y = random.choice(water_coords)
            else:
                # cannot spawn in water:
                x = random.randint(0, WORLD_SIZE[0] - 1)
                y = random.randint(0, WORLD_SIZE[1] - 1)
                while (x,y) in water_coords:
                    x = random.randint(0, WORLD_SIZE[0] - 1)
                    y = random.randint(0, WORLD_SIZE[1] - 1)
                    pass
            simulation_world.add_organism(Organism(x, y, species_name))      # This function is no longer needed since we are populating the world in setup_simulation()
    pass
def setup_simulation():
    """Initializes the world and populates it with organisms."""
    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)
    
    logging.info("Setting up simulation...")
    simulation_world = World(WORLD_SIZE)
    replanish_speces(simulation_world)
      
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
    history_time        = []
    history_organisms   = {}
    history_total       = []
    history_avg_fitness = []
    output_files = {}
    
    txt='tick, species, count'
    for g in GENE_DEFAULTS.keys():
        txt+=f", {g}"
    for species_name in INITIAL_POPULATION.keys():
        history_organisms[species_name] = []
        output_files[species_name] = open(f"{species_name}_history.txt", "w")
        output_files[species_name].write(txt+'\n')
        
    for tick in range(SIMULATION_TICKS):        
        # 1. Update the world state
        world.update_world()
        # if tick % 100 == 0:
        #     replanish_speces(world) # Replenish species every 100 ticks to keep the ecosystem dynamic and prevent total extinction. Adjust as needed.
        for species_name in INITIAL_POPULATION.keys():
            txt=f"{tick}, "
            count = sum(1 for org in world.organisms if org.species_name == species_name)
            #if count ==0: break
            txt+=f"{species_name}, {count}"
            for g in GENE_DEFAULTS.keys():
                fs_avg = np.mean([org._calculate_fitness_score_gene(g) for org in world.organisms if org.species_name == species_name]) if count > 0 else 0
                txt+=f" , {fs_avg:.3f}"
            txt+='\n'
            #print(txt)
            output_files[species_name].write(txt)



        total_fitness_score = sum(org.fitness_score for org in world.organisms)
        avg_fitness_score   = total_fitness_score / len(world.organisms) if world.organisms else 0
        # Append current data to history lists

        history_time.append(tick)
        for species_name in INITIAL_POPULATION.keys():
            count = sum(1 for org in world.organisms if org.species_name == species_name)
            #print (f"Tick: {tick} | Species: {species_name} | Count: {count}")
            history_organisms[species_name].append(count)

        history_total.append(len(world.organisms))
        history_avg_fitness.append(avg_fitness_score)

        WINDOW_SIZE=10000

        if tick>WINDOW_SIZE:
            history_time.pop(0) 
            for species_name in INITIAL_POPULATION.keys():
                history_organisms[species_name].pop(0)
            history_total.pop(0)  
            history_avg_fitness.pop(0)  
    

        if tick < 100 or (tick % 10 == 0):
            logging.info(f"Tick: {tick:>4} | Pop: {history_total[-1]} | Avg Fitness: {avg_fitness_score:.2f}")

    
        plot_graph     = True
        plot_animation = PLOT_ANIMATION

        # # --- RENDER THE WORLD (using ax_world) ---
        if plot_graph or plot_animation:
            ax_world.clear()
            ax_graph.clear()
            ax_fitness.clear()
            ax_world.imshow(world.water_grid.T, cmap=water_cmap, origin='lower', alpha=0.6)
            
            for species_name in INITIAL_POPULATION.keys():
                organisms = [org for org in world.organisms if org.species_name == species_name]
                if len(organisms) > 0:
                    if plot_animation:
                        ax_world.scatter([org.x for org in organisms], [org.y for org in organisms], 
                                         c= SPECIES[species_name]['color'],
                                         s=[50.0*org.energy / INITIAL_ENERGY for org in organisms], 
                                         marker=SPECIES[species_name]['marker'], 
                                         edgecolors=[org.priority for org in organisms], 
                                         linewidths=1, 
                                     alpha=[1 - org.age / org.max_age for org in organisms]) # Size and alpha based on energy
                if plot_graph:
                    ax_graph.plot(history_time, history_organisms[species_name], 
                                    color=SPECIES[species_name]['color'], 
                                    linestyle='-', label=species_name)

            ax_world.set_title(f"World | Pop: {history_total[-1]} | Avg Fitness: {avg_fitness_score:.2f}")
            ax_world.set_xlim(0, WORLD_SIZE[0])
            ax_world.set_ylim(0, WORLD_SIZE[1])
        
            # --- STEP 3: Store data and render the graph (using ax_graph) ---

            # Clear the previous graph

            # Plot the data
            if plot_graph:
                ax_graph.plot(history_time, history_total, color='black', linestyle='--', label='Total')
            if plot_graph:
                ax_fitness.plot(history_time, history_avg_fitness, color='deepskyblue', label='Avg. Fitness')
            # Style the graph
                ax_graph.set_title("Population & Fitness Over Time")
                ax_graph.set_xlabel("Tick")
                ax_graph.set_ylabel("Count")
                # Set the Y-label for the right axis
                ax_fitness.set_ylabel("Average Fitness (0-1)", color='deepskyblue')
                ax_fitness.tick_params(axis='y', labelcolor='deepskyblue')
                #ax_fitness.set_ylim(0, 1) # Lock the fitness axis

           # --- NEW: Combine legends from both axes ---
                h1, l1 = ax_graph.get_legend_handles_labels()
                h2, l2 = ax_fitness.get_legend_handles_labels()
                ax_graph.legend(h1 + h2, l1 + l2, loc='upper left')
                ax_graph.grid(True)
                ax_graph.set_xlim(left=history_time[0], right=max(100, tick)) # Keep x-axis from getting too small
            
            # Adjust layout to prevent titles/labels overlapping
            plt.tight_layout()
            if STEP_BY_STEP:
                for o in world.organisms:
                    logging.info(o)
                    pass

                a=input("Press Enter to continue..., q to quit: ")
                if a == 'q':
                    exit(0)
                    break
            plt.pause(0.01) # Pause briefly to update the plot

        if not world.organisms and tick > 50:
            logging.info("All organisms have died. Ending simulation.")
            break
    for species_name in INITIAL_POPULATION.keys():        
        output_files[species_name].close()
    plt.ioff()
    logging.info("Simulation finished. Displaying final state.")
    plt.show()

if __name__ == "__main__":
    run_simulation()