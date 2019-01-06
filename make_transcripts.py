#!/usr/bin/env python2

'''
Make transcripts file from genome FASTA and GFF3
Author Byoungnam Min Aug 1, 2017
'''

# Import modules
import sys
import re
import os
from Bio.Seq import Seq
from argparse import ArgumentParser
from collections import defaultdict
from Bio.Alphabet import generic_dna


# Main function
def main(argv):
    argparse_usage = (
        'make_transcripts.py -f <input_fasta> -g <input_gff3> '
        '-o <output_prefix>'
    )
    parser = ArgumentParser(usage=argparse_usage)
    parser.add_argument(
        '-f', '--input_fasta', nargs=1, required=True,
        help='Input fasta file'
    )
    parser.add_argument(
        '-g', '--input_gff3', nargs=1, required=True,
        help='Input gff3 file'
    )

    args = parser.parse_args()
    input_fasta = os.path.abspath(args.input_fasta[0])
    input_gff3 = os.path.abspath(args.input_gff3[0])

    # Run functions :)
    parse_gff3(input_fasta, input_gff3)


def import_file(input_file):
    with open(input_file) as f_in:
        txt = (line.rstrip() for line in f_in)
        txt = list(line for line in txt if line)
    return txt


def get_reverse_complement(nuc_seq):
    my_dna = Seq(nuc_seq, generic_dna)
    rev_comp_dna = str(my_dna.reverse_complement())
    return rev_comp_dna


def parse_gff3(input_fasta, input_gff3):
    # Read gff3
    gff3 = import_file(input_gff3)

    # Parse gff3 and store in dictionary
    D_gff3 = defaultdict(list)
    reg_parent = re.compile('Parent=([^;]+)')
    for line in gff3:
        if re.search('^#', line):  # Ignore comment
            continue
        line_split = line.split('\t')
        entry_type = line_split[2]
        if entry_type != 'CDS':  # Only consider 'CDS'
            continue
        scaffold = line_split[0]
        start = int(line_split[3])
        end = int(line_split[4])
        strand = line_split[6]
        phase = int(line_split[7])
        gene_id = line_split[8]
        gene_id = reg_parent.search(gene_id).group(1)
        D_gff3[gene_id].append((scaffold, start, end, strand, phase))

    # Read fasta
    fasta = import_file(input_fasta)

    # Parse fasta and store in dictionary
    D_fasta = defaultdict(str)
    for line in fasta:
        if re.search(r'^>', line):
            scaffold_id = line.split(' ')[0].replace('>', '')
            continue
        D_fasta[scaffold_id] += line

    # Extract sequence
    gff3_base = os.path.splitext(input_gff3)[0]
    output_transcript = '{}_transcript.fna'.format(gff3_base)
    output2 = open(output_transcript, 'w')

    gene_ids = sorted(
        D_gff3.keys(),
        key=lambda x: x.replace('.t1', '')
    )

    for gene_id in gene_ids:
        feature = D_gff3[gene_id]
        sorted_by_start = sorted(feature, key=lambda tup: tup[1])

        # Gene sequcne
        gene_scaffold = sorted_by_start[0][0]
        gene_start = sorted_by_start[0][1]
        gene_end = sorted_by_start[-1][2]

        gene_seq = D_fasta[gene_scaffold][gene_start - 1:gene_end]
        if strand == '-':
            gene_seq = gene_seq[::-1]

        nuc_seq = ''
        for element in sorted_by_start:  # Feature is a list of tuple
            scaffold = element[0]
            start = element[1]
            end = element[2]
            strand = element[3]
            phase = element[4]

            nuc_seq += D_fasta[scaffold][start - 1:end]

        # If it is '-' strand, reverse the transcript
        if strand == '-':
            nuc_seq = get_reverse_complement(nuc_seq)

        # If phase is not 0, trim first few bases according to phase
        if strand == '+' and sorted_by_start[0][4] != 0:
            codon_start = sorted_by_start[0][4]
            nuc_seq = nuc_seq[codon_start:]  # Trimming

        elif strand == '-' and sorted_by_start[-1][4] != 0:
            codon_start = sorted_by_start[-1][4]
            nuc_seq = nuc_seq[codon_start:]

        # Write to file
        output2.write('>{}\n'.format(gene_id))
        j = 0
        while j < len(nuc_seq):
            output2.write('{}\n'.format(nuc_seq[j:j + 60]))
            j += 60

    output2.close()


if __name__ == '__main__':
    main(sys.argv[1:])
