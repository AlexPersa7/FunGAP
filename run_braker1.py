#!/usr/bin/python

'''
Run BRAKER1
Author Byoungnam Min on Mar 24, 2015
'''

# Import modules
import sys
import os
from argparse import ArgumentParser

# Get logging
this_path = os.path.realpath(__file__)
this_dir = os.path.dirname(this_path)
sys.path.append(this_dir)
from set_logging import set_logging

# Parameters
run_hisat2_path = os.path.join(this_dir, 'run_hisat2.py')


# Main function
def main(argv):
    argparse_usage = (
        'run_braker1.py -m <masked_assembly> -b <bam_files> -o <output_dir> '
        '-l <log_dir> -c <num_cores>'
    )
    parser = ArgumentParser(usage=argparse_usage)
    parser.add_argument(
        "-m", "--maksed_assembly", dest="masked_assembly", nargs=1,
        help="Assembly file in FASTA"
    )
    parser.add_argument(
        "-b", "--bam_files", dest="bam_files", nargs='+',
        help="BAM files generated by Hisat2"
    )
    parser.add_argument(
        "-o", "--output_dir", dest="output_dir", nargs='+',
        help="Output directory"
    )
    parser.add_argument(
        "-l", "--log_dir", dest="log_dir", nargs='+',
        help="Log directory"
    )
    parser.add_argument(
        "-c", "--num_cores", dest="num_cores", nargs=1,
        help="Number of cores to be used"
    )

    args = parser.parse_args()
    if args.masked_assembly:
        masked_assembly = os.path.abspath(args.masked_assembly[0])
    else:
        print '[ERROR] Please provide INPUT ASSEMBLY'
        parser.print_help()
        sys.exit(2)

    if args.bam_files:
        bam_files = [os.path.abspath(x) for x in args.bam_files]
    else:
        print '[ERROR] Please provide BAM FILES'
        parser.print_help()
        sys.exit(2)

    if args.output_dir:
        output_dir = os.path.abspath(args.output_dir[0])
    else:
        print '[ERROR] Please provide OUTPUT DIRECTORY'
        parser.print_help()
        sys.exit(2)

    if args.log_dir:
        log_dir = os.path.abspath(args.log_dir[0])
    else:
        print '[ERROR] Please provide LOG DIRECTORY'
        parser.print_help()
        sys.exit(2)

    if args.num_cores:
        num_cores = args.num_cores[0]
    else:
        num_cores = 5

    # Create necessary dirs
    create_dir(output_dir, log_dir)

    # Set logging
    log_file = os.path.join(
        log_dir, 'pipeline', 'run_braker1.log')
    global logger_time, logger_txt
    logger_time, logger_txt = set_logging(log_file)

    # Run functions :) Slow is as good as Fast
    run_braker1(masked_assembly, bam_files, output_dir, log_dir, num_cores)


# Define functions
def import_file(input_file):
    with open(input_file) as f_in:
        txt = (line.rstrip() for line in f_in)
        txt = list(line for line in txt if line)
    return txt


def create_dir(output_dir, log_dir):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    if not os.path.exists(log_dir):
        os.mkdir(log_dir)

    output_base = os.path.basename(output_dir)
    log_output_dir = os.path.join(log_dir, output_base)
    if not os.path.exists(log_output_dir):
        os.mkdir(log_output_dir)

    log_pipeline_dir = os.path.join(log_dir, 'pipeline')
    if not os.path.exists(log_pipeline_dir):
        os.mkdir(log_pipeline_dir)


def run_braker1(masked_assembly, bam_files, output_dir, log_dir, num_cores):
    output_base = os.path.basename(output_dir)
    # braker.pl --fungus --softmasking --cores=5
    # --genome=final.assembly.fasta --bam=merged.bam
    # --species=<species> --gff3
    current_dir = os.getcwd()
    os.chdir(output_dir)
    for bam_file in bam_files:
        prefix = (
            os.path.basename(bam_file)
            .replace('.bam', '')
            .replace('_sorted', '')
        )
        gff3_braker1 = os.path.join(
            output_dir, prefix, 'braker1_%s.gff3' % (prefix)
        )
        log_braker = os.path.join(
            log_dir, output_base, 'braker1_%s.log' % (prefix)
        )
        logger_time.debug('START: BRAKER1')

        if not os.path.exists(gff3_braker1):
            command1 = (
                'braker.pl --fungus --softmasking --cores=%s --genome=%s '
                '--bam=%s --species=%s --gff3 > %s 2>&1'
            ) % (
                num_cores, masked_assembly, bam_file,
                prefix, log_braker
            )
            logger_txt.debug('[Run] %s' % (command1))
            os.system(command1)

            command2 = 'mv %s %s' % (
                os.path.join(output_dir, 'braker', prefix),
                os.path.join(output_dir, prefix)
            )
            logger_txt.debug('[Run] %s' % (command2))
            os.system(command2)

            # Change file name
            command3 = 'mv %s %s' % (
                os.path.join(output_dir, prefix, 'augustus.gff3'),
                os.path.join(
                    output_dir, prefix,
                    'braker1_%s.gff3' % (prefix)
                )
            )
            logger_txt.debug('[Run] %s' % (command3))
            os.system(command3)

            command4 = 'mv %s %s' % (
                os.path.join(output_dir, prefix, 'augustus.aa'),
                os.path.join(
                    output_dir, prefix,
                    'braker1_%s.faa' % (prefix)
                )
            )
            logger_txt.debug('[Run] %s' % (command4))
            os.system(command4)

            # Remove braker directory
            command5 = 'rmdir %s' % (os.path.join(output_dir, 'braker'))
            logger_txt.debug('[Run] %s' % (command5))
            os.system(command5)
        else:
            logger_txt.debug('Braker1 has already been finished')
    logger_time.debug('DONE : Braker1')
    os.chdir(current_dir)

if __name__ == "__main__":
    main(sys.argv[1:])
