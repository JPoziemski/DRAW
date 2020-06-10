import abc
import logging
import os
import subprocess

import global_variables
from global_variables import ToolError

ERROR_EXCEPTIONS_STARTS = ["<exception str() failed>", ]


class Tool(metaclass=abc.ABCMeta):
    """Class responsible for executing tools with proper parameters

    :param input: input params
    :type input: list
    :param output_dir: directory where files will be saved
    :type output_dir: str"""

    def __init__(self, input, output_dir, user_params):
        """class constructor

        :param input: input params
        :type input: list
        :param output_dir: directory where files will be saved
        :type output_dir: str"""
        self.logger = logging.getLogger(__name__)
        self.params = user_params
        self.input = input
        self.output_dir = output_dir
        self.command = ""
        self.DISABLED_ARGS = []
        self.input_arg = ""
        self.output_arg = ""
        self.created_files = []

    @abc.abstractmethod
    def prepare_to_run(self):
        """Performs set of operations necessary to execute tool"""
        pass

    def get_output_arg(self):
        return self.output_arg

    def run(self):

        # print(self.command)
        process = subprocess.Popen(self.command, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        process.wait()

        # print(process.communicate()[1])
        if process.returncode != 0:
            raise ToolError(process.communicate()[1].decode("utf-8"))
        pass

    def get_created_files(self):
        """Get file paths which tool creates

        :return: self.created_files - file paths
        :rtype: list
        """
        return self.created_files

    def check_params(self):
        """Checks if there are any parameters that are not allowed

        :raises ToolError: some parameters that are disallowed"""
        invalid_args = []
        for arg in self.DISABLED_ARGS:
            if arg in self.params:
                invalid_args.append(arg)

        if invalid_args:
            raise ToolError("For tool {} used disallowed arguments {}".format(type(self).__name__,
                                                                              ", ".join(invalid_args)))

    @abc.abstractmethod
    def add_input(self, input):
        """Add input argument to tool command"""
        pass

    @abc.abstractmethod
    def add_output(self, output):
        """Add input argument to tool command"""
        pass


class FastQC(Tool):
    """FastQC master class"""
    EXEC_PATH = "fastqc"
    # TOOL_PATH = global_variables.fastqc_path
    # EXEC_PATH = os.path.join(TOOL_PATH, "fastqc")
    ALLOWED_ARGS = ["-o", "--outdir",
                    "-t", "--threads",
                    "--nogroup",
                    "-k", "--kmers"]

    def __init__(self, input, output_dir, user_params):
        super().__init__(input, output_dir, user_params)
        self.prepare_to_run()

    def check_params(self):
        params_splitted = self.params.split()
        fixed_params_splitted = []

        for arg in params_splitted:
            fixed_params_splitted.extend(arg.split("="))

        args_names = [arg for arg in fixed_params_splitted if arg.startswith("-")]
        args_names_set = set(args_names)

        if len(args_names_set - set(FastQC.ALLOWED_ARGS)) != 0:
            raise ToolError("invalid argument/s, all allowed arguments: {}".format(FastQC.ALLOWED_ARGS))
        return 0

    def add_input(self, input):
        self.params = input + "* " + self.params

    def add_output(self, output):
        self.params += " --outdir={}".format(output)

    def prepare_to_run(self):
        self.params = self.input + "* " + self.params
        self.params += " --outdir={}".format(self.output_dir)
        self.command = ["{} {}".format(FastQC.EXEC_PATH, self.params)]


class Trimmomatic(Tool):
    """Trimmomatic master class"""
    TOOL_PATH = global_variables.trimmomatic_path
    EXEC_PATH = os.path.join(TOOL_PATH, "trimmomatic-0.39.jar")

    def __init__(self, input, output, params, seq_type):
        super().__init__(input, output, params)
        self.output_file_names = []
        self.seq_type = seq_type
        if seq_type == "single_end":
            self.seq_type_arg = "SE"
        else:
            self.seq_type_arg = "PE"
        self.DISABLED_ARGS = []
        self.prepare_to_run()


    def add_input(self, input):
        input_files_num = input.split()
        if self.seq_type == "single_end" and len(input_files_num) != 1:
            raise ToolError("For single end it should ony one input file")
        elif self.seq_type == "paired_end" and len(input_files_num) != 2:
            raise ToolError("For paired end it should 2 input files")
        else:
            self.input = input

    def add_output(self, output_dir):
        if self.seq_type == "paired_end":
            self.prepare_output_file_names_for_paired_end()
            print(output_dir, self.output_file_names[0])
            self.created_files = [os.path.join(output_dir, output_file) for output_file in self.output_file_names]
            self.output_arg = " ".join(self.created_files)
        else:
            input_basename = os.path.basename(self.input)
            if input_basename.endswith(".fq"):
                output_file_name = input_basename.replace(".fq", "trimmed.fastq")
            else:
                output_file_name = input_basename.replace(".fastq", "trimmed.fastq")
            created_files_path = os.path.join(output_dir, output_file_name)
            self.created_files.append(created_files_path)
            self.output_arg = os.path.join(output_dir, output_file_name)

    def get_created_files(self):
        valid_created_files = [file_path for file_path in self.created_files if "unpaired" not in file_path]
        return valid_created_files

    def prepare_output_file_names_for_paired_end(self):
        if not self.input:
            raise ValueError("input not defined, first provide input")

        self.output_file_names = []
        splited_input = self.input.split()

        for file_path in splited_input:
            file_name = os.path.basename(file_path)
            if file_name.endswith("1.fastq"):

                for out_file_name in global_variables.AFTER_TRIMMING_FILE_NAMES_ENDINGS["1"]:
                    self.output_file_names.append(file_name.replace("1.fastq", out_file_name))
            else:

                for out_file_name in global_variables.AFTER_TRIMMING_FILE_NAMES_ENDINGS["2"]:
                    self.output_file_names.append(file_name.replace("2.fastq", out_file_name))

    def prepare_to_run(self):
        self.add_input(self.input)
        self.add_output(self.output_dir)
        self.command = [
            "java -jar {} {} {} {} {}".format(Trimmomatic.EXEC_PATH, self.seq_type_arg, self.input, self.output_arg,
                                              self.params)]
        print(self.command)


class Hisat2(Tool):
    """Hisat2 master class"""
    BUILD_PATH = "hisat2-build"
    EXEC_PATH = "hisat2"

    # BUILD_PATH = os.path.join(global_variables.hisat2_path, "hisat2-build")
    #EXEC_PATH = os.path.join(global_variables.hisat2_path, "hisat2")

    def __init__(self, input, output, params, sequence):
        super().__init__(input, output, params)
        self.sequence = sequence
        self.DISABLED_ARGS = ["--sra-acc", "--qseq", "-f", "-c", "-r", "--qc-filter"]
        self.index_prefix = os.path.join(output, "mapping_index")
        self.prepare_to_run()


    def add_input(self, input):
        if isinstance(input, str):
            self.input_arg = "-U {}".format(input)
        elif isinstance(input, tuple):
            files_1 = input[0]
            files_2 = input[1]
            self.input_arg = "-1 {} -2 {}".format(files_1, files_2)
        else:
            raise TypeError("Input data should be: list or dict")

    def add_output(self, output_dir):
        if self.input_arg.startswith("-U"):
            input_file_name = os.path.basename(self.input[0])
            output_file_name = input_file_name.replace(".fastq", ".sam")
        else:
            input_file_name = os.path.basename(self.input[0])
            output_file_name = input_file_name.replace("_1.fastq", ".sam")

        created_file_path = os.path.join(output_dir, output_file_name)
        print(created_file_path)
        self.created_files.append(created_file_path)
        self.output_arg = "-S {}".format(created_file_path)

    def build(self):
        """Exectue build command that create index files for Hisat2"""
        command = "{} {} {}".format(Hisat2.BUILD_PATH, self.sequence, self.index_prefix)

        process = subprocess.Popen(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        process.wait()

        # print(process.communicate()[1])
        if process.returncode != 0:
            raise ToolError(process.communicate()[1].decode("utf-8"))
        # print(process.communicate(),process.returncode)

    def prepare_to_run(self):
        self.add_input(self.input)
        self.add_output(self.output_dir)
        self.command = ["{} {} {} -x {} {}".format(Hisat2.EXEC_PATH, self.input_arg,
                                                   self.output_arg, self.index_prefix, self.params)]

    def run(self):
        """Execute tool command"""
        print(self.command)
        self.build()
        process = subprocess.Popen(self.command, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        process.wait()

        # print(process.communicate()[1])
        if process.returncode != 0:
            raise ToolError(process.communicate()[1].decode("utf-8"))
        pass


class Bowtie(Hisat2):
    BUILD_PATH = "bowtie2-build"
    EXEC_PATH = "bowtie2"

    # BUILD_PATH = os.path.join(global_variables.bowtie_path, "bowtie2-build")
    #EXEC_PATH = os.path.join(global_variables.bowtie_path, "bowtie2")

    def __init__(self, input, output, params, sequence):
        super().__init__(input, output, params, sequence)
        self.DISABLED_ARGS = ["--sra-acc", "-b", "-f", "--qseq", "-F", "-c"]
        self.prepare_to_run()

    def build(self):
        command = "{} -f {} {}".format(Bowtie.BUILD_PATH, self.sequence, self.index_prefix)

        process = subprocess.Popen(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        process.wait()

        # print(process.communicate()[1])
        if process.returncode != 0:
            raise ToolError(process.communicate()[1].decode("utf-8"))

    def prepare_to_run(self):
        self.add_input(self.input)
        self.add_output(self.output_dir)
        self.command = "{} {} {} -x {} {} --no-unal".format(Bowtie.EXEC_PATH, self.input_arg, self.output_arg,
                                                            self.index_prefix, self.params)


class Stringtie(Tool):
    EXEC_path = "stringtie"

    #EXEC_path = os.path.join(global_variables.stringtie_path, "stringtie")

    def __init__(self, input, output, user_params, annotation):
        super().__init__(input, output, user_params)
        self.DISABLED_ARGS = ["--merge"]
        self.annotoation = annotation
        self.prepare_to_run()

    def add_input(self, input_path):
        self.input_arg = input_path

    def add_output(self, output):
        input_file = os.path.basename(self.input)
        self.output_filename = input_file.replace(".bam", "count.gft")

        self.output_arg = "-e -o {} -A {}".format(os.path.join(output, self.output_filename),
                                                  os.path.join(output, input_file.replace(".bam", "gene_abundances.tsv")))

    def prepare_to_run(self):
        self.add_input(self.input)
        self.add_output(self.output_dir)
        self.command = [
            "{} {} {} -G {} {}".format(Stringtie.EXEC_path, self.input, self.params, self.annotoation, self.output_arg)]



class samtools:
    "adassadas"
    def __init__(self):
        self.command = ""

    def sam_to_bam(self, input_file, output_file):
        """converts sam to bam

        :param input_file: intput file
        :type input_file: str
        :param output_file: output file
        :type output_file: str"""
        self.command = "view -S -b {} > {}".format(input_file, output_file)

    def sort_bam(self, input_file, output):
        self.command = "sort {} -o {}".format(input_file, output)

    def run(self):
        self.command = "{} {}".format(global_variables.samtools_path, self.command)
        print(self.command)
        process = subprocess.Popen([self.command], stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        process.wait()

        # print(process.communicate()[1])
        if process.returncode != 0:
            raise ToolError(process.communicate()[1].decode("utf-8"))
        pass


'''s = Trimmomatic(
    "/home/kuba/ADP_project/HBR_Rep1_ERCC-Mix2_Build37-ErccTranscripts-chr22.read1.fastq /home/kuba/ADP_project/HBR_Rep1_ERCC-Mix2_Build37-ErccTranscripts-chr22.read2.fastq",
    "/home/kuba/ADP_project/",
    "PE LEADING:1 TRAILING:1 SLIDINGWINDOW:4:15 MINLEN:20")'''
# s= Bowtie("-p 4 --rg-id test_rep --rg SM:test --dta --rna-strandness RF ",
'''s = Hisat({1:["/home/kuba/ADP_project/HBR_Rep1_ERCC-Mix2_Build37-ErccTranscripts-chr22.read1.fastq"],
             2:["/home/kuba/ADP_project/HBR_Rep1_ERCC-Mix2_Build37-ErccTranscripts-chr22.read2.fastq"]},
            "/home/kuba/ADP_project/UHR_Rep1_bowtie.sam",
           "-p 4",
         "/home/kuba/Pobrane/Homo_sapiens.GRCh38.dna.chromosome.22.fa",
         "/home/kuba/Pobrane/fastqfiles/hs_index")
s.prepare_to_run()'''
# s.add_input({1:["/home/kuba/ADP_project/HBR_Rep1_ERCC-Mix2_Build37-ErccTranscripts-chr22.read1.fastq"],
#             2:["/home/kuba/ADP_project/HBR_Rep1_ERCC-Mix2_Build37-ErccTranscripts-chr22.read2.fastq"]})
# s.add_output("/home/kuba/Pobrane/fastqfiles/SP")
# s.add_output("/home/kuba/ADP_project/UHR_Rep1_bowtie.sam")
# s = Stringtie("-p 4 -G /home/kuba/Homo_sapiens.GRCh38.100.chromosome.22.gff3")
# s.add_input("/home/kuba/ADP_project/UHR_Rep1.sorted.bam")
# s.add_output("/home/kuba/ADP_project/stringtie_result.gft")
# s.run()
# SE -phred33  /home/kuba/output.fq
# print(FastQC.check_params("sadass"))
