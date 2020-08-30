#!/usr/bin/env python

__author__ = "Otavio Alves"

import random, csv, copy, argparse
import numpy as np

def load_participants(filename, delimiter='\t'):
    """ reads tsv file containing participants and classifications """
    with open(filename) as f:
        return list(csv.reader(f, delimiter=delimiter))

def write_groups(groups, filename):
    """ writes participants to an output file with group column appended """
    with open(filename, 'w') as f:
        for i, group in enumerate(groups, 1):
            for p in group:
                a = copy.copy(p)
                a.append(i)
                f.write('\t'.join(np.array(a, dtype=str))+'\n')

def split_groups(participants, n_groups):
    """ splits the list of participants into n_groups """
    N = len(participants)
    one_more_groups = N % n_groups
    one_less_groups = n_groups - one_more_groups
    n_per_group = int(N/n_groups)

    groups = []

    # First, let's deal with the groups that have 1 extra participant
    for i in range(one_more_groups):
        start = i*(n_per_group+1)
        end = (i+1)*(n_per_group+1)
        groups.append(participants[start:end])

    # Now, the rest
    for i in range(one_more_groups, n_groups):
        start = one_more_groups + i*n_per_group
        end = one_more_groups + (i+1)*n_per_group
        groups.append(participants[start:end])

    return groups

def mutate_selection(selection):
    """ randomly picks 2 participants and swap their positions """
    s = copy.deepcopy(selection)
    # Picks 2 participants at random
    a, b = random.sample(range(len(s)), 2)
    # and swap their positions
    s[a], s[b] = s[b], s[a]
    return s

def shuffle_selection(selection):
    """ entirely shuffles list of participants """
    return random.sample(selection, len(selection))

def print_groups(groups):
    """ prints groups in a nice way """
    for i, group in enumerate(groups, 1):
        print('Grupo {}'.format(i))
        for p in group:
            print('\t{}'.format(p[1]))
        print('')

def rank_diversity(groups, column_index):
    """ ranks the diversity of the classifier in each group using max(counts)/sum(counts) as metric """
    rank = 0.
    for group in groups:
        # Gets specified column
        column = np.array(group, dtype=str)[:,column_index]
        # Counts incidence of each category in the current group
        values, counts = np.unique(column, return_counts=True)
        # Diversity metric
        rank += float(max(counts))/float(sum(counts))
    return rank/len(groups)

def cluster(groups, column_index):
    """ ranks the proximity of values in the specified column by comparing its standard deviation to the total std """
    # The metric used here will be std(in this group)/std(in the whole list of participants)
    # Hopefully, this is a measure of how clustered the quantity is within groups
    rank = 0.
    all_columns = [] # We'll use this to compute the total standard deviation
    for group in groups:
        # Extracts the column of interest
        column = np.array(np.array(group, dtype=str)[:,column_index], dtype=float)
        all_columns.extend(column)
        rank += np.std(column)
    rank = rank/np.std(all_columns)/len(groups)
    return rank

def optimize(participants, n_groups, iterations, get_score, simulated_annealing=False):
    """ interates to find the best score group distribution """
    selection = mutate_selection(participants)

    best_groups = split_groups(selection, n_groups)
    curr_score = get_score(best_groups)
    min_score = curr_score

    for i in range(iterations):
        s = mutate_selection(selection)
        groups = split_groups(s, n_groups)
        score = get_score(groups)
        # If simulated annealing is used, allow for bad jumps with probability exp(-(score-curr_score)/temperature)
        if score <= curr_score or (simulated_annealing and np.exp(-(score-curr_score)/(float(i+1)/iterations)) <= np.random.rand()):
            curr_score = score
            selection = s
        if score <= min_score:
            best_groups = groups
            min_score = score

    return best_groups, min_score

def get_score(groups, mix_columns, cluster_columns):
    """ computes overall score """
    values = []
    if mix_columns is not None:
        values.extend([float((c.split(':')[1]) if ':' in c else 1)*rank_diversity(groups, int(c.split(':')[0])) for c in mix_columns])
    if cluster_columns is not None:
        values.extend([(float(c.split(':')[1]) if ':' in c else 1)*cluster(groups, int(c.split(':')[0])) for c in cluster_columns])
    return np.average(values)

def main(args):
    participants = load_participants(args.participants)

    # If iterations is set, find the best solution
    if args.iterations:
        best_groups, min_score = optimize(participants, args.n_groups, args.iterations, lambda g: get_score(g, args.mix_columns, args.cluster_columns), args.simulated_annealing)
        print('Best score: {}'.format(min_score))
        print('')
        print_groups(best_groups)
    else:
        print_groups(split_groups(participants, args.n_groups))

    if args.output:
        write_groups(best_groups, args.output)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Takes a list of participants and splits into groups mixing/grouping specified categories.')

    parser.add_argument('participants',
            help='tsv file containing list of participants.')

    parser.add_argument('-n', dest='n_groups', type=int, required=True,
            help='Number of groups to split.')

    parser.add_argument('-i', dest='iterations', type=int, required=False,
            help='Number of iterations in the optimization process.')

    parser.add_argument('-o', dest='output', type=str, required=False,
            help='Output file with group number column appended.')

    parser.add_argument('-a', dest='simulated_annealing', action='store_true',
            help='Use simulated annealing.')

    parser.add_argument('-m', dest = 'mix_columns', nargs='+', required = False,
            help='Mix groups by values found in the specified columns. Useful to separate people belonging to the same specified class. Use <column_index>:<weight> to specify a weight for each column. If you want to group classes instead of mixing them, use a negative weight.')

    parser.add_argument('-c', dest = 'cluster_columns', nargs='+', required = False,
            help='Cluster similar values found in the specified columns. Useful to get people with similar age together in the same group. Use <column_index>:<weight> to specify a weight for each column. If you want to disperse instead of clustering values, use a negative weight.')

    args = parser.parse_args()

    if args.mix_columns or args.cluster_columns:
        assert args.iterations and args.iterations > 0, "If you set up -m or -c, you have to specify -i greater than zero."

    main(args)
