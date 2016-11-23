#!/usr/bin/python

'''
Run Repeat modeler
Author Byoungnam Min on Aug 19, 2015
'''

# Import modules
import sys
import os
from glob import glob
from argparse import ArgumentParser

# Get Logging
this_path = os.path.realpath(__file__)
this_dir = os.path.dirname(this_path)
sys.path.append(this_dir)
from set_logging import set_logging


# Main function
def main(argv):
    optparse_usage = (
        'run_repeat_modeler.py -g <genome_assembly> -o <output_dir> '
        '-l <log_dir> -p <project_name> -c <num_cores>'
    )
    parser = ArgumentParser(usage=optparse_usage)
    parser.add_argument(
        "-g", "--genome_assembly", dest="genome_assembly", nargs=1,
        help="Genome assembly file in FASTA format"
    )
    parser.add_argument(
        "-o", "--output_dir", dest="output_dir", nargs=1,
        help="Output directory"
    )
    parser.add_argument(
        "-l", "--log_dir", dest="log_dir", nargs=1,
        help="Log directory"
    )
    parser.add_argument(
        "-p", "--project_name", dest="project_name", nargs=1,
        help="Project name without space. e.g. Mag, Eco, Pst_LUM"
    )
    parser.add_argument(
        "-c", "--num_cores", dest="num_cores", nargs=1,
        help="Number of cores to be used"
    )

    args = parser.parse_args()
    if args.genome_assembly:
        genome_assembly = os.path.abspath(args.genome_assembly[0])
    else:
        print '[ERROR] Please provide INPUT ASSEMBLY'
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

    if args.project_name:
        project_name = args.project_name[0]
    else:
        print '[ERROR] Please provide PROJECT NAME'
        parser.print_help()
        sys.exit(2)

    if args.num_cores:
        num_cores = args.num_cores[0]
    else:
        print '[ERROR] Please provide NUMBER OF CORES'
        parser.print_help()
        sys.exit(2)

    # Create necessary dirs
    create_dir(output_dir, log_dir)

    # Set logging
    log_file = os.path.join(
        log_dir, 'pipeline', 'run_repeat_modeler.log'
    )
    global logger_time, logger_txt
    logger_time, logger_txt = set_logging(log_file)

    # Run functions :) Slow is as good as Fast
    run_repeat_modeler(
        genome_assembly, output_dir, log_dir, project_name, num_cores
    )


def create_dir(output_dir, log_dir):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    if not os.path.exists(log_dir):
        os.mkdir(log_dir)

    log_dir = os.path.join(log_dir, 'repeat_modeler')
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)

    log_pipeline_dir = os.path.join(log_dir, 'pipeline')
    if not os.path.exists(log_pipeline_dir):
        os.mkdir(log_pipeline_dir)


def run_repeat_modeler(
    genome_assembly, output_dir, log_dir, project_name, num_cores
):
    # BuildDatabase -name Choanephora_cucurbitarum
    # ../Choanephora_cucurbitarum_assembly.fna
    # RepeatModeler -database Choanephora_cucurbitarum -pa 25

    # Get repeat model
    repeat_lib = os.path.join(
        output_dir, '*', 'consensi.fa.classified'
    )
    if not glob(repeat_lib):
        os.chdir(os.path.join(output_dir))
        logger_time.debug('START running RepeatModeler')
        log_file1 = os.path.join(
            log_dir, 'repeat_modeler', 'build_database.log'
        )
        command1 = 'BuildDatabase -name %s %s > %s 2>&1' % (
            project_name, genome_assembly, log_file1
        )
        logger_txt.debug('[Run] %s' % (command1))
        os.system(command1)

        log_file2 = os.path.join(
            log_dir, 'repeat_modeler', 'repeat_modeler.log'
        )
        command2 = 'RepeatModeler -database %s -pa %s > %s 2>&1' % (
            project_name, num_cores, log_file2
        )
        logger_txt.debug('[Run] %s' % (command2))
        os.system(command2)
        logger_time.debug('DONE  running RepeatModeler')
    else:
        logger_txt.debug('Running RepeatModeler has already been finished')

if __name__ == "__main__":
    main(sys.argv[1:])
