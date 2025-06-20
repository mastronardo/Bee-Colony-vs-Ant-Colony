from deap import tools, algorithms
from sys import getsizeof
from time import time

def eaSimpleWithElitism(population, toolbox, cxpb, mutpb, ngen, stats=None, halloffame=None, verbose=__debug__):
    """This algorithm is similar to DEAP eaSimple() algorithm, with the modification that
    halloffame is used to implement an elitism mechanism. The individuals contained in the
    halloffame are directly injected into the next generation and are not subject to the
    genetic operators of selection, crossover and mutation.
    """
    execution_times = []
    individuals_sizeof = [getsizeof(ind) for ind in population]
    population_sizeof = sum(individuals_sizeof)
    logbook = tools.Logbook()
    logbook.header = ['gen', 'nevals', 'exec_time_seconds'] + (stats.fields if stats else [])

    # --------------
    # Generation 0
    # --------------
    gen_zero_start = time()
    # Evaluate the individuals with an invalid fitness
    invalid_ind = [ind for ind in population if not ind.fitness.valid]
    fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit

    if halloffame is None:
        raise ValueError("halloffame parameter must not be empty!")

    halloffame.update(population)
    hof_size = len(halloffame.items) if halloffame.items else 0
    
    gen_zero_end = time()-gen_zero_start
    execution_times.append(gen_zero_end)

    record_zero = stats.compile(population) if stats else {}
    logbook.record(gen=0, nevals=len(invalid_ind), exec_time_seconds=gen_zero_end, **record_zero)
    if verbose:
        print(logbook.stream)

    best_fitness = float('inf')
    first_gen_best = 0

    # ------------------------
    # Generational loop (1 -> ngen+1)
    # ------------------------
    for gen in range(1, ngen + 1):
        start_gen = time()
        
        # Select the next generation individuals
        offspring = toolbox.select(population, len(population) - hof_size)

        # Vary the pool of individuals
        offspring = algorithms.varAnd(offspring, toolbox, cxpb, mutpb)

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        # add the best back to population:
        offspring.extend(halloffame.items)

        # Update the hall of fame with the generated individuals
        halloffame.update(offspring)

        # Replace the current population by the offspring
        population[:] = offspring

        # First generation which has the best fitness
        current_best_fitness = min(ind.fitness.values[0] for ind in population)
        if current_best_fitness < best_fitness:
            best_fitness = current_best_fitness
            first_gen_best = gen

        # Append the current generation statistics to the logbook
        record = stats.compile(population) if stats else {}
        end_gen = time()-start_gen
        execution_times.append(end_gen)
        logbook.record(gen=gen, nevals=len(invalid_ind), exec_time_seconds=end_gen, **record)
        if verbose:
            print(logbook.stream)

    return population, logbook, execution_times, population_sizeof, first_gen_best