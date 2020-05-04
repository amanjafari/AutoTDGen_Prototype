"""

Aotumated test input generation using activity diagram and genetic algorithm

"""

import datetime
import random
import unittest
from itertools import chain

from TestTDGen_demo import genetic


# all_dup_list = {
#     "locks":[["13", "locks>=1","Y"],
#                      ["13","locks>=1","14","15","16","T"]],
#     "locks":[["19","20","locks>=1","Y"],

#                      ["19", "20", "locks>=4", "15","16" , "T"]],
#     "stocks":[["15", "stocks>=1","T"]],
#     "barrels":[["15", "barrels>=1","T"]],
#     "sales": [["27", "sales>=1800", "Y"],
#                           ["27", "sales>=1800", "29", "Y"],
#                           ["27", "sales>=1800", "29", "30", "31", "32", "33", "T"],
#                           ["27", "29", "sales>=1000", "Y"],
#                           ["27", "sales>=1000", "35", "36", "37", "T"],
#                           ["27", "29", "sales<=990", "38", "39", "T"]],
#     "commission":[["20", "31 <= commission && commission < 15","T"]]
#                 }

"""
    Because the variable sales is in a form of funciton decomposition. 
    It's implementation is not integrated here, but here its concisdered as a single valued variable.
     due to bigger sized integer value on the guard condition this may requires a lager population size.
      (e.g. 2000). A demonstrative example is provided superately in "varFunctionDecomposition". 
"""
all_dup_list = {
    "locks":[["1", "locks>=1","Y"],
                     ["1","locks>=1","3","4","5","N"],
                     ["5", "1< locks <= 70", "Y"],
                     ["5", "1 =< locks && locks <= 70","7", "N"]],
    "stocks":[["3", "stocks>=1","Y"],
                     ["3", "stocks>=1","5","6","7","N"]],
    "barrels":[["3", "barrels>=1","Y"],
                     ["3", "barrels>=1","5","6","7","N"]],
    "commission":[["14", "31 => commission && commission > 15","16","N"]],
    "sales": [["27", "sales>=1800", "Y"],
                          ["7", "sales>=1800", "9", "Y"],
                          ["7", "sales>=1800", "9", "14","13","N"],
                          ["7", "sales>=1000", "Y"],
                          ["7", "sales>=1000", "11", "13", "14", "N"],
                          ["7", "sales<=998", "12", "13","14","N"]],
                }


# When the generated test paths are not represented as numarical values.
""" 
 all_dup_list = {
                  "engine":[["Car Simulation", "Start the car engine","Y"],
                   ["Car Simulation","Start the car engine","Fork", "Accelerate the car", "engine>0", "N"]]
                 # "brakepedal":[["Car Simulation", "Start the care engine", "Fork", "Accelerate the care", "engine is not null", "brakepedal > 0","Y"],
                 #               ["Car Simulation", "Start the care engine", "Fork", "Accelerate the care","engine is not null", "brakepedal > 0"," set brakepedel to zero","N"]],
                 # "brakepedel":[["Car Simulation", "Start the car engine", "Fork, Brake the car", "engine != null", "brakepedal < maxBrake-1", "Y"],
                 #               ["Car Simulation", "Start the car engine", "Fork, Brake the car", "engine != null", "brakepedal < 9","increment brakepedal by one","N"]],
                 # "throttle":[["Car Simulation", "Start the car engine", "Fork",  "Accelerate the car", "throttle < maxThrottle - 5","Y"],
                 #             ["Car Simulation", "Start the car engine", "Fork", "Accelerate the car", "throttle < 5", "increment throttle by five","N"]],
                 # "throttle":[["Car Simulation", "Start the car engine", "Fork", "Brake the car", "engine not null", "throttle > 0", "N"]]
                 }
"""

# set random test data in range 1 ~ ...
# thsi can be experemented with different values
geneset = [i for i in range(1, 3000)]


def get_fitness(genes, dups):
    fitness = Fitness(sum(abs(e(genes)) for e in dups))
    return fitness


def display(candidate, startTime, fnGenesToInputs,v):
    timeDiff = "Time Diff ," + str(datetime.datetime.now() - startTime)
    result = str(v) +" , " +  str(fnGenesToInputs(candidate.Genes))
    print("{}\t{}\t{}".format(result, candidate.Fitness, timeDiff))

"""
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
"""

def mutate(genes, fnGetFitness):
    count = random.randint(2, len(genes))
    initialFitness = fnGetFitness(genes)
    while count > 0:
        count -= 1
        indexA, indexB = random.sample(range(len(genes)), 2)
        genes[indexA], genes[indexB] = genes[indexB], genes[indexA]
        fitness = fnGetFitness(genes)
        if fitness > initialFitness:
            return


def crossover(parentGenes, donorGenes, fnGetFitness):
    pairs = {Pair(donorGenes[0], donorGenes[-1]): 0}

    for i in range(len(donorGenes) - 1):
        pairs[Pair(donorGenes[i], donorGenes[i + 1])] = 0

    tempGenes = parentGenes[:]
    if Pair(parentGenes[0], parentGenes[-1]) in pairs:
        # find a discontinuity
        found = False
        for i in range(len(parentGenes) - 1):
            if Pair(parentGenes[i], parentGenes[i + 1]) in pairs:
                continue
            tempGenes = parentGenes[i + 1:] + parentGenes[:i + 1]
            found = True
            break
        if not found:
            return None

    runs = [[tempGenes[0]]]
    for i in range(len(tempGenes) - 1):
        if Pair(tempGenes[i], tempGenes[i + 1]) in pairs:
            runs[-1].append(tempGenes[i + 1])
            continue
        runs.append([tempGenes[i + 1]])

    initialFitness = fnGetFitness(parentGenes)
    count = random.randint(2, 20)
    runIndexes = range(len(runs))
    while count > 0:
        count -= 1
        for i in runIndexes:
            if len(runs[i]) == 1:
                continue
            if random.randint(0, len(runs)) == 0:
                runs[i] = [n for n in reversed(runs[i])]

        indexA, indexB = random.sample(runIndexes, 2)
        runs[indexA], runs[indexB] = runs[indexB], runs[indexA]
        childGenes = list(chain.from_iterable(runs))
        if fnGetFitness(childGenes) > initialFitness:
            return childGenes
    return childGenes



class DUPathsTests(unittest.TestCase):

    def fnGuardDistance(sefl, list, index):
        vars_key = sefl.fnGet_var()
        total_dup_list = list.__getitem__(vars_key[index])
        list_to_cover = []
        len_list = len(total_dup_list)
        num_dup_covered = 0

        for i, value in enumerate(total_dup_list):
            for e in value[-1:]:
                if e == "Y":
                    num_dup_covered+=1
                elif e == "N":
                    list_to_cover = value
                    num_dup_covered += 1
                    break
                else:
                    continue
            else:
                continue
            break

        for _ in range(num_dup_covered):
            i = 0
            total_dup_list.pop(i)

        unvisited_list = [list_to_cover]

        predicates = []
        left_operand = 0
        var = 0
        var2 = 0

        while len(unvisited_list) > 0:
            for (i, val) in enumerate(unvisited_list):
                for e in val:
                    #  ad = "&&" if e.__contains(ad) and e.con...(".")
                    if "&&" in e:
                        a = e.split()
                        predicates.append(e)
                        left_operand = ''.join(a[2:3])
                        var = ''.join(a[0:1])
                        var2 = ''.join(a[-1:])


                    elif ">=" in e:
                        ge = e.split(">=")
                        # predicates.append(ne[0] + " - " + ne[1])
                        predicates.append(e)
                        left_operand = ''.join(ge[0])
                        var = ''.join(ge[1])
                    elif ">" in e:
                        g = e.split(">")
                        predicates.append(e)
                        left_operand = ''.join(g[0])
                        var = ''.join(g[1])

                    elif "<=" in e:
                        le = e.split("<=")
                        predicates.append(e)
                        left_operand = ''.join(le[0])
                        var = ''.join(le[1])

                    elif "<" in e:
                        l = e.split("<")
                        predicates.append(e)
                        left_operand = ''.join(l[0])
                        var = ''.join(l[1])

                    elif "==" in e:
                        e = e.split("==")
                        predicates.append(e)
                        left_operand = ''.join(e[0])
                        var = ''.join(e[1])

                    elif "!=" in e:
                        ne = e.split("!=")
                        # predicates.append(ne[0] + " - " + ne[1])
                        predicates.append(e)
                        left_operand = ''.join(ne[0])
                        var = ''.join(ne[1])


            return left_operand, var, var2, num_dup_covered, total_dup_list, len_list,predicates, vars_key

    def fnGet_var(self):
        var_key_list = []
        for k in all_dup_list.keys():
            var_key_list.append(k)

        return var_key_list


    def test_real_inputs_T1(self, index=0):

        index = index
        left_operand, data_member, data_member2, dup_covered, tdl,du_pair, pred, var_list = self.fnGuardDistance(all_dup_list, index)
        print("The number of du-pair covered ,", dup_covered, "\n", "The predicate covered ,", pred)

        def fnGenesToInputs(genes):
            # return genes[0],genes[1],genes[2]
            return genes[0]


        def Guard_distance(genes):
            # locks, stocks, barrels = fnGenesToInputs(genes)
            # data_member = locks + stocks  + barrels
            left_operand = fnGenesToInputs(genes)
            guard_distance = 0
            for elem in pred:
                # if ">=" or ">" in elem:

                if "&&" in elem:
                    # guard_distance = (left_operand - int(data_member)) + (left_operand - int(data_member2))
                    guard_distance = ( left_operand - int(data_member) + int(data_member))
                    if guard_distance > 15 and guard_distance <= 31:
                        guard_distance = 0
                    else:
                        guard_distance


                elif ">=" or ">" in elem:
                    guard_distance = left_operand - int(data_member)
                    if guard_distance == 0:
                        guard_distance = 0
                    else:
                        guard_distance

                elif "<=" or "<" in elem:
                    guard_distance = int(data_member) - left_operand
                    if guard_distance == 0:
                        guard_distance = 0
                    else:
                        guard_distance

                elif "==" in elem:
                    guard_distance = abs(int(data_member) - left_operand)

                elif "!=" in elem:
                    guard_distance = abs(int(data_member) - left_operand)

                # elif "=<" or "=<" in elem:
                #     guard_distance = 0
                else:
                    guard_distance = 0

            dup_len = len(all_dup_list)
            approach_level = (du_pair - dup_covered) / (du_pair + dup_len)
            # approach_level = (du_pair - dup_covered) * 1 / (du_pair + dup_len)

            return approach_level + abs(guard_distance)

        dups = [Guard_distance]
        best = self.solve_indiuidual(1, geneset, dups, fnGenesToInputs,left_operand)

        if not best == 0 and not len(tdl)==0:
            self.test_real_inputs_T1(index)

        elif len(tdl) == 0 and not len(var_list) == 0:
            index = index + 1
            if not index > len(var_list)-1:
                self.test_real_inputs_T1(index)

        else:
            print("\n\t\t", "----Test Generation Successfuly Completed-----!")


    def solve_indiuidual(self, induiduals, geneset, dups, fnGenesToInputs,var):
        startTime = datetime.datetime.now()
        maxAge = 500
        # window = Window(max(1, int(len(geneset) / (2 * maxAge))),
        #                 max(1, int(len(geneset) / 3)),
        #                 int(len(geneset) / 2))
        # geneIndexes = [i for i in range(induiduals)]
        # sortedGeneset = sorted(geneset)

        def fnCreate():
            return random.sample(geneset, len(geneset))

        def fnDisplay(candidate):
            display(candidate, startTime, fnGenesToInputs, var)

        def fnGetFitness(genes):
            return get_fitness(genes, dups)

        def fnMutate(genes):
            # mutate(genes, sortedGeneset, window, geneIndexes)
            mutate(genes, fnGetFitness)
        def fnCrossover(parent, donor):
            return crossover(parent, donor, fnGetFitness)

        optimalFitness = Fitness(0.99)
        best = genetic.get_best(fnGetFitness, induiduals, optimalFitness,
                                geneset, fnDisplay, fnMutate, custom_create=fnCreate, maxAge=maxAge, poolSize=20, crossover=fnCrossover)
        print("Best", best.Fitness)
        self.assertTrue(not optimalFitness > best.Fitness)
        return best.Fitness


class Fitness:
    def __init__(self, totalFitness):
        self.TotalFitness = totalFitness

    def __gt__(self, other):
        return self.TotalFitness < other.TotalFitness

    def __str__(self):
        return "Fitness , {:0.2f}".format(float(self.TotalFitness))


class Pair:
    def __init__(self, dup, adjacent):
        if dup < adjacent:
            dup, adjacent = adjacent, dup
        self.Dup = dup
        self.Adjacent = adjacent

    def __eq__(self, other):
        return self.Dup == other.Dup and self.Adjacent == other.Adjacent

    def __hash__(self):
        return hash(self.Dup) * 397 ^ hash(self.Adjacent)

# class Window:
#     def __init__(self, minimum, maximum, size):
#         self.Min = minimum
#         self.Max = maximum
#         self.Size = size
#
#     def slide(self):
#         self.Size = self.Size - 1 if self.Size > self.Min else self.Max


if __name__ == '__main__':
    unittest.main()
