from tree import Node, Tree
from math import floor, ceil
from collections import Counter

def get_genomes(tree):
    genomes = {}
    for leaf in tree.iter_leaves():
        genomes[leaf.name] = leaf.genome
    return genomes

def collapse_genomes(genomes, normal_diploid_genome, num_chroms):
    for chrom in range(num_chroms):
        for leaf, genome in genomes.items():
            for allele in [0, 1]:
                genome[chrom][allele] = dict(Counter(genome[chrom][allele]))
                for i in set(normal_diploid_genome[chrom][allele]) - set(genome[chrom][allele].keys()):
                    genome[chrom][allele][i] = 0
    return genomes
                
def format_CN_profiles(tree, normal_diploid_genome, num_chroms, min_cn_len, bin_len):
    # Consolidate leaf genomes
    genomes = get_genomes(tree)
    genome_counters = collapse_genomes(genomes, normal_diploid_genome, num_chroms)

    # Assign regions to bins
    bins, bin_coords = {}, {}
    regions_per_bin = floor(bin_len / min_cn_len)
    for chrom in range(num_chroms):
        bins[chrom], bin_coords[chrom] = {}, {}
        bin_count = 0
        for i in normal_diploid_genome[chrom][0]:
            if i == 0:
                bins[chrom][bin_count] = [i]
            else:
                if i % regions_per_bin == 0:
                    bin_coords[chrom][bin_count] = [bins[chrom][bin_count][0]*min_cn_len, (bins[chrom][bin_count][-1]+1)*min_cn_len]
                    bin_count += 1
                    bins[chrom][bin_count] = [i]
                else:
                    bins[chrom][bin_count].append(i)
        bin_coords[chrom][bin_count] = [bins[chrom][bin_count][0]*min_cn_len, (bins[chrom][bin_count][-1]+1)*min_cn_len]

    # Find the average number of copies over the regions in each bin
    CN_profiles = {}
    for chrom in range(num_chroms):
        CN_profiles[chrom] = {}
        sorted_bins = list(bins[chrom].keys())
        sorted_bins.sort()
        for leaf, genome in genome_counters.items():
            CN_profiles[chrom][leaf] = [[], []]
            for b in sorted_bins:
                regions = bins[chrom][b]
                for allele in [0, 1]:
                    CN_profiles[chrom][leaf][allele].append(round(sum([genome[chrom][allele][i] for i in regions]) / len(regions)))
    
    return CN_profiles, bin_coords

def save_CN_profiles(tree, chrom_names, bins, min_cn_length, filepath):
    f = open(filepath, 'w+')
    headers = ['CELL', 'chrom', 'start', 'end', 'CN states']
    f.write('\t'.join(headers) + '\n')

    leaves = [leaf for leaf in tree.iter_leaves()]

    # Writes to file in order of chroms, bins, cell
    for chrom in chrom_names:
        num_bins = len(bins[chrom]) - 1
        for i in range(num_bins):
            bin_start, bin_end = str(bins[chrom][i]*min_cn_length), str(bins[chrom][i+1]*min_cn_length)
            for leaf in leaves:
                CN_state = str(leaf.profile[chrom][0][i]) + ',' + str(leaf.profile[chrom][1][i])
                line = [leaf.name, chrom, bin_start, bin_end, CN_state]
                f.write('\t'.join(line) + '\n')
    f.close()
                    
            
