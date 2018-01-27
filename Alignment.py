import sys
from Bio import SeqIO
from Bio import pairwise2
import pandas as pd
import numpy as np

sys.setrecursionlimit(10000000)

"""
    Created by Mohsen Naghipourfar on 1/26/18.
    Email : mn7697np@gmail.com
"""

marburg_genes = []  # list of marburg genes
ebolavirus_genomes = []  # list of ebolavirus genomes
all_genes = {}  # dictionary which maps each geneName to found sequences in ebola genomes
edit_distance_matrices = [[[0 for i in range(5)] for j in range(5)] for k in range(7)]  # matrix for edit distances
gene_names = ['GP', 'L', 'VP24', 'VP30', 'VP35', 'VP40', 'NP']  # all 7 gene names


def glocal_alignment(genome, gene, match=1, mismatch=-1, gap_penalty=-1):  # Global Local Alignment
    # Lengths of sequences
    len_genome = len(genome) + 1
    len_gene = len(gene) + 1

    # scores matrix
    scores = [[0 for i in range(len_genome)] for j in range(len_gene)]
    # traceback matrix
    traceback = [[0 for i in range(len_genome)] for j in range(len_gene)]  # to store the trace back path

    for i in range(len_gene):  # Adding penalty for gene --> score[i][0] == i * gap_penalty
        scores[i][0] = i * gap_penalty
    for i in range(1, len_gene):  # Dynamic Programming Formula
        for j in range(1, len_genome):
            if genome[j - 1] == gene[i - 1]:  # if matched
                diagonal = scores[i - 1][j - 1] + match
            else:
                diagonal = scores[i - 1][j - 1] + mismatch

            left = scores[i][j - 1] + gap_penalty  # gap
            above = scores[i - 1][j] + gap_penalty  # gap
            scores[i][j] = max(left, above, diagonal)  # dp formulation

            if scores[i][j] == diagonal:
                traceback[i][j] = 1  # 1 means trace diagonally
            elif scores[i][j] == left:
                traceback[i][j] = 2  # 2 means trace to the left
            else:
                traceback[i][j] = 3  # 3 means trace to the top

    genome_alignment, gene_alignment = '', ''  # alignments for printing

    max_j = scores[-1].index(max(scores[-1]))  # stores the number of column which the max number exists in
    while i >= 0 and j >= 0:
        if j > max_j:
            genome_alignment = genome[j - 1] + genome_alignment
            gene_alignment = '-' + gene_alignment
            j -= 1
            continue

        if traceback[i][j] == 1:  # 1 means to trace diagonally
            genome_alignment = genome[j - 1] + genome_alignment
            gene_alignment = gene[i - 1] + gene_alignment
            i -= 1
            j -= 1
        elif traceback[i][j] == 2:  # 2 means trace to the left
            genome_alignment = genome[j - 1] + genome_alignment
            gene_alignment = '-' + gene_alignment
            j -= 1
        else:  # 3 means trace to the top
            genome_alignment = '-' + genome_alignment
            gene_alignment = gene[i - 1] + gene_alignment
            i -= 1
    score = 0  # Score of alignment
    for i in range(len(genome_alignment)):  # Calculate Score of alignment
        if genome_alignment[i] != gene_alignment[i]:
            score += 1
    # print(genome_alignment)
    # print(gene_alignment)
    return j, max_j, score  # returns substring(start, end) indices and score


def global_alignment(genome, gene, match=1, mismatch=-1, gap_penalty=-1):
    # Lengths of sequences
    len_genome = len(genome) + 1
    len_gene = len(gene) + 1

    # scores matrix
    scores = [[0 for i in range(len_genome)] for j in range(len_gene)]
    # traceback matrix
    traceback = [[0 for i in range(len_genome)] for j in range(len_gene)]  # to store the trace back path

    for i in range(len_gene):  # Adding penalty for gene --> score[i][0] == i * gap_penalty
        scores[i][0] = i * gap_penalty
    for i in range(len_genome):  # Adding penalty for gene --> score[0][i] == i * gap_penalty
        scores[0][i] = i * gap_penalty
    for i in range(1, len_gene):  # Dynamic Programming Formula
        for j in range(1, len_genome):
            if genome[j - 1] == gene[i - 1]:  # if matched
                diagonal = scores[i - 1][j - 1] + match
            else:
                diagonal = scores[i - 1][j - 1] + mismatch

            left = scores[i][j - 1] + gap_penalty  # gap
            above = scores[i - 1][j] + gap_penalty  # gap
            scores[i][j] = max(left, above, diagonal)  # dp formulation

            if scores[i][j] == diagonal:
                traceback[i][j] = 1  # 1 means trace diagonally
            elif scores[i][j] == left:
                traceback[i][j] = 2  # 2 means trace to the left
            else:
                traceback[i][j] = 3  # 3 means trace to the top

    genome_alignment, gene_alignment = '', ''  # alignments for printing

    max_j = scores[-1].index(max(scores[-1]))  # stores the number of column which the max number exists in
    while i >= 0 and j >= 0:
        if j > max_j:
            genome_alignment = genome[j - 1] + genome_alignment
            gene_alignment = '-' + gene_alignment
            j -= 1
            continue

        if traceback[i][j] == 1:  # 1 means to trace diagonally
            genome_alignment = genome[j - 1] + genome_alignment
            gene_alignment = gene[i - 1] + gene_alignment
            i -= 1
            j -= 1
        elif traceback[i][j] == 2:  # 2 means trace to the left
            genome_alignment = genome[j - 1] + genome_alignment
            gene_alignment = '-' + gene_alignment
            j -= 1
        else:  # 3 means trace to the top
            genome_alignment = '-' + genome_alignment
            gene_alignment = gene[i - 1] + gene_alignment
            i -= 1
    score = 0  # Score of alignment
    for i in range(len(genome_alignment)):  # Calculate Score of alignment
        if genome_alignment[i] != gene_alignment[i]:
            score += 1
    # print(genome_alignment)
    # print(gene_alignment)
    return j, max_j, score  # returns substring(start, end) indices and score


def align_and_find_genes(genome):  # genome is the sequence of ebolavirus genome
    f = open('./Output/found_genes/' + genome.name + '.csv', "w")
    start = 0
    for gene in marburg_genes:  # For each genes found in marburg virus
        len_gene = len(gene.seq)
        end = (start + len_gene * 3) if len(genome) > (start + len_gene * 3) else len(
            genome)  # Just consider a subsequence of genome
        gene_str = str(gene.seq)
        genome_str = str(genome.seq)[start: end]
        # alignments = pairwise2.align.localmd(gene_str, genome_str, 1, -1, -1, -0.5, 0, 0) # Using biopython alignment function
        # final_alignment = alignments[0]  # final_alignment contains --> [align1, align2, score, begin, end]
        # begin_idx = final_alignment[3] # 3 is begin
        # end_idx = final_alignment[4] # 4 is end
        begin_idx, end_idx, unused = glocal_alignment(genome_str, gene_str)  # Apply Global-Local Alignment
        f.write(gene.name + "," + str(start + begin_idx) + "," + str(start + end_idx) + "\n")  # write to file
        start = end - len_gene  # update start index for the next gene to align
    f.close()


def read_data():  # read data and initialize variables
    global ebolavirus_genomes, marburg_genes
    # read Marburg genes data
    marburg_genes = []
    for seq_record in SeqIO.parse("./Data/Marburg_Genes.fasta", "fasta"):
        marburg_genes.append(seq_record)

    # read Ebolaviruses genome data as seq_record objects
    Bundibugyo_genome = SeqIO.read("./Data/Bundibugyo_genome.fasta", "fasta")
    Reston_genome = SeqIO.read("./Data/Reston_genome.fasta", "fasta")
    Sudan_genome = SeqIO.read("./Data/Sudan_genome.fasta", "fasta")
    TaiForest_genome = SeqIO.read("./Data/TaiForest_genome.fasta", "fasta")
    Zaire_genome = SeqIO.read("./Data/Zaire_genome.fasta", "fasta")
    ebolavirus_genomes = [Bundibugyo_genome, Reston_genome, Sudan_genome, TaiForest_genome, Zaire_genome]


def start_aligning():  # Align all genes to all genomes in the given data
    for genome in ebolavirus_genomes:
        align_and_find_genes(genome)


def global_align():  # Global Alignment For calculating score and edit distance matrices
    global edit_distance_matrices
    gene_id = 0
    for gene in all_genes.values():  # Iterate all genes for all genomes
        g1_id = 0
        for genome1 in gene:
            g2_id = 0
            for genome2 in gene:
                if genome1.seq != genome2.seq:
                    if g1_id <= g2_id:
                        continue
                    # alignments = pairwise2.align.globalms(genome1, genome2, 0, -1, -1, -1) # Biopython package
                    # alignment = alignments[0] # first alignment
                    # score = alignment[2] # score of alignment
                    a, b, score = global_alignment(genome1, genome2)  # Global Alignment
                    edit_distance = 1 * score  # Calculate score of alignment
                    edit_distance_matrices[gene_id][g1_id][g2_id] = edit_distance
                    edit_distance_matrices[gene_id][g2_id][g1_id] = edit_distance
                g2_id += 1
            g1_id += 1
        gene_id += 1


def read_genes(genomes):  # read all <genome_name>.csv files for accessing genes in genomes
    global all_genes, edit_distance_matrices
    for gene in marburg_genes:  # For every gene (7 genes)
        i = 0
        genes = []
        for genome in genomes:  # For every species in ebolavirus
            indices = pd.read_csv("./Output/found_genes/" + genome.name + ".csv", header=None)  # read .csv file
            begin_idx = int(indices.loc[i, 1])  # begin index for special gene
            end_idx = int(indices.loc[i, 2])  # end index for special gene
            new_record = SeqIO.SeqRecord(genome.seq[begin_idx: end_idx])  # Create SeqRecord Object File
            new_record.name = genome.name
            genes.append(new_record)  # Append to gene list
            i += 1
        all_genes[gene.name] = genes  # Append genelist to all_genes dictionary
    genomes_size = len(genomes)
    genes_size = len(marburg_genes)
    edit_distance_matrices = [[[0 for i in range(genomes_size)] for j in range(genomes)] for k in range(genes_size)]  # matrix for edit distances


def save_edit_matrices():  # Save edit distance matrices into files
    i = 0
    for name, gene in all_genes.items():
        edit_matrix = np.array(edit_distance_matrices[i])  # Numpy Package is used here for saving into files
        np.savetxt("./Output/edit_matrices/" + name + ".csv", edit_matrix, delimiter=",", fmt='%d')
        i += 1


if __name__ == '__main__':
    read_data()
    # start_aligning()

    read_genes(ebolavirus_genomes)
    global_align()
    save_edit_matrices()
