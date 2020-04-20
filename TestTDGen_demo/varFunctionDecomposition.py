"""

Aotumated test input generation using activity diagram and genetic algorithm
This example further illustrate the cases when a variable is in a form of
function composition such that the domain of a variable is the range of
another two or more variables

Note that this code is a demonstrative example

"""

import datetime
import random
import unittest
from TestTDGen_demo import genetic


def get_fitness(genes, dups):
    fitness = Fitness(sum(abs(e(genes)) for e in dups))
    return fitness


def display(candidate, startTime, fnGenesToInputs):
    timeDiff = datetime.datetime.now() - startTime
    vars = ['lock', 'stock', 'barrel']
    result = ', '.join("{} = {}".format(s, v)
                       for s, v in
                       zip(vars, fnGenesToInputs(candidate.Genes)))
    print("{}\t{}\t{}".format(result, candidate.Fitness, timeDiff))


def mutate(genes, sortedGeneset, window, geneIndexes):
    indexes = random.sample(geneIndexes, random.randint(1, len(genes))) \
        if random.randint(0, 10) == 0 else [random.choice(geneIndexes)]
    window.slide()
    while len(indexes) > 0:
        index = indexes.pop()
        genesetIndex = sortedGeneset.index(genes[index])
        start = max(0, genesetIndex - window.Size)
        stop = min(len(sortedGeneset) - 1, genesetIndex + window.Size)
        genesetIndex = random.randint(start, stop)
        genes[index] = sortedGeneset[genesetIndex]



class DUPathsTests(unittest.TestCase):
    global geneset
    geneset = [i for i in range(1, 990)]

    def test_3_inputs_T1(self):

        def fnGenesToInputs(genes):
            return genes[0], genes[1], genes[2]

        def B1(genes):
            lock, stock, barrel = fnGenesToInputs(genes)
            du_path = 5
            du_pair = 6
            # guard_distance = 1800 - (lock * 45 + stock * 30 + barrel * 25)
            guard_distance = (lock * 45 + stock * 30 + barrel * 25) - 1800
            dup_covered = 3
            approach_level = (du_pair - dup_covered)  / (du_pair + du_path)
            if guard_distance >= 0:
                guard_distance
            else:
                guard_distance
            return  approach_level + guard_distance

        dups = [B1]
        best = self.solve_indiuidual(3, geneset, dups, fnGenesToInputs)

        if not best == 0:

            def B2(genes):
                lock, stock, barrel = fnGenesToInputs(genes)
                du_path = 5
                du_pair = 6 - 3
                dup_covered = 2
                # guard_distance = 1000 - (lock * 45 + stock * 30 + barrel * 25)
                guard_distance = (lock * 45 + stock * 30 + barrel * 25) - 1000
                apparoach_level = (du_pair - dup_covered) / (du_pair + du_path)

                if guard_distance >=0:
                    guard_distance = 0
                else:
                    guard_distance

                return apparoach_level + guard_distance

            dups = [B2]
            best = self.solve_indiuidual(3, geneset, dups, fnGenesToInputs)

            if not best == 0:
                def B3(genes):
                    lock, stock, barrel = fnGenesToInputs(genes)
                    du_path = 5
                    du_pair = 6 - (3 + 2)
                    dup_covered = 1

                    guard_distance = abs(990 - (lock * 45 + stock * 30 + barrel * 25))
                    apparoach_level = (du_pair - dup_covered) / (du_pair + du_path)

                    if guard_distance < 990:
                        guard_distance = 0
                    else:
                        guard_distance

                    return apparoach_level + guard_distance

                dups = [B3]
                self.solve_indiuidual(3, geneset, dups, fnGenesToInputs)

    def solve_indiuidual(self, induiduals, geneset, dups,
                       fnGenesToInputs):
        startTime = datetime.datetime.now()
        maxAge = 50
        window = Window(max(1, int(len(geneset) / (2 * maxAge))),
                        max(1, int(len(geneset) / 3)),
                        int(len(geneset) / 2))
        geneIndexes = [i for i in range(induiduals)]
        sortedGeneset = sorted(geneset)

        def fnDisplay(candidate):
            display(candidate, startTime, fnGenesToInputs)

        def fnGetFitness(genes):
            return get_fitness(genes, dups)

        def fnMutate(genes):
            mutate(genes, sortedGeneset, window, geneIndexes)

        optimalFitness = Fitness(1)
        best = genetic.get_best(fnGetFitness, induiduals, optimalFitness,
                                geneset, fnDisplay, fnMutate, maxAge=maxAge)
        print("Best", best.Fitness)
        self.assertTrue(not optimalFitness > best.Fitness)
        return best.Fitness


class Fitness:
    def __init__(self, totalFitness):
        self.TotalFitness = totalFitness

    def __gt__(self, other):
        return self.TotalFitness < other.TotalFitness

    def __str__(self):
        return "Fitness: {:0.2f}".format(float(self.TotalFitness))



class Window:
    def __init__(self, minimum, maximum, size):
        self.Min = minimum
        self.Max = maximum
        self.Size = size

    def slide(self):
        self.Size = self.Size - 1 if self.Size > self.Min else self.Max

if __name__ == '__main__':
    unittest.main()
