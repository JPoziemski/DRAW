import abc
import logging
import os
import subprocess

import global_variables
from global_variables import ToolError

ERROR_EXCEPTIONS_STARTS = ["<exception str() failed>", ]


class Tool(metaclass=abc.ABCMeta):

    def __init__(self, input, output_dir, user_params):
        self.logger = logging.getLogger(__name__)
        self.params = user_params
        self.input = input
        self.output_dir = output_dir
        self.command = ""
        self.DISABLED_ARGS = []
        self.input_arg = ""
        self.output_arg = ""

    @abc.abstractmethod
    def prepare_to_run(self):
        pass

    def get_output_arg(self):
        return self.output_arg

    def run(self):

        print(self.command)
        process = subprocess.Popen(self.command, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        process.wait()

        # print(process.communicate()[1])
        if process.returncode != 0:
            raise ToolError(process.communicate()[1].decode("utf-8"))
        pass

    def check_params(self):

        invalid_args = []
        for arg in self.DISABLED_ARGS:
            if arg in self.params:
                invalid_args.append(arg)

        if invalid_args:
            raise ToolError("For tool {} used disallowed arguments {}".format(type(self).__name__,
                                                                              ", ".join(invalid_args)))

    @abc.abstractmethod
    def add_input(self, input):
        pass

    @abc.abstractmethod
    def add_output(self, output):
        pass


class FastQC(Tool):
    TOOL_PATH = global_variables.fastqc_path
    EXEC_PATH = os.path.join(TOOL_PATH, "fastqc")
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
    TOOL_PATH = global_variables.trimmomatic_path
    EXEC_PATH = os.path.join(TOOL_PATH, "trimmomatic-0.39.jar")

    def __init__(self, input, output, params):
        super().__init__(input, output, params)
        self.output_file_names = []
        self.set_seq_type_from_params()
        self.DISABLED_ARGS = []
        self.prepare_to_run()

    def set_seq_type_from_params(self):
        if "PE" in self.params:
            self.seq_type = "paired_end"
            self.params = self.params.replace("PE ", "")
            self.seq_type_arg = "PE"
        else:
            self.seq_type = "single_end"
            self.params = self.params.replace("SE ", "")
            self.seq_type_arg = "SE"

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
            self.output_file_names = [os.path.join(output_dir, output_file) for output_file in self.output_file_names]
            self.output_arg = " ".join(self.output_file_names)
        else:
            input_basename = os.path.basename(self.input)
            if input_basename.endswith(".fq"):
                output_file_name = input_basename.replace(".fq", "trimmed.fastq")
            else:
                output_file_name = input_basename.replace(".fastq", "trimmed.fastq")
            self.output_arg = os.path.join(output_dir, output_file_name)

    def prepare_output_file_names_for_paired_end(self):
        if not self.input:
            raise ValueError("input not defined, first provide input")

        self.output_file_names = []
        splited_input = self.input.split()

        for file_name in splited_input:

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


class Hisat(Tool):
    BUILD_PATH = os.path.join(global_variables.hisat2_path, "hisat2-build")
    EXEC_PATH = os.path.join(global_variables.hisat2_path, "hisat2")

    def __init__(self, input, output, params, sequence, index_prefix):
        super().__init__(input, output, params)
        self.sequence = sequence
        self.index_prefix = index_prefix
        self.DISABLED_ARGS = ["--sra-acc", "--qseq", "-f", "-c", "-r", "--qc-filter"]
        self.prepare_to_run()

    def add_input(self, input):
        if isinstance(input, list):
            self.input_arg = "-U {}".format(",".join(input))
        elif isinstance(input, dict):
            if 1 in input.keys() and 2 in input.keys():
                files_1 = input[1]
                files_2 = input[2]
                self.input_arg = "-1 {} -2 {}".format(",".join(files_1), ",".join(files_2))
        else:
            raise TypeError("Input data should be: list or dict")

    def add_output(self, output_dir):
        if self.input_arg.startswith("-U"):
            input_file_name = os.path.basename(self.input[0])
            output_file_name = input_file_name.replace(".fastq", ".sam")
        else:
            input_file_name = self.input[1]
            output_file_name = input_file_name.replace("_1.fastq", ".sam")

        self.output_arg = "-S {}".format(os.path.join(output_dir, output_file_name))

    def build(self):

        command = "{} {} {}".format(Hisat.BUILD_PATH, self.sequence, self.index_prefix)

        process = subprocess.Popen(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        process.wait()

        # print(process.communicate()[1])
        if process.returncode != 0:
            raise ToolError(process.communicate()[1].decode("utf-8"))
        # print(process.communicate(),process.returncode)

    def prepare_to_run(self):
        self.add_input(self.input)
        self.add_output(self.output_dir)
        self.build()
        self.command = ["{} {} {} -x {} {}".format(Hisat.EXEC_PATH, self.input_arg,
                                                   self.output_arg, self.index_prefix, self.params)]


class Bowtie(Hisat):
    BUILD_PATH = os.path.join(global_variables.bowtie_path, "bowtie2-build")
    EXEC_PATH = os.path.join(global_variables.bowtie_path, "bowtie2")

    def __init__(self, input, output, params, sequence, index_prefix):
        super().__init__(input, output, params, sequence, index_prefix)
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
        self.build()
        self.command = "{} {} {} -x {} {} --no-unal".format(Bowtie.EXEC_PATH, self.input, self.output,
                                                            self.index_prefix, self.params)


class Stringtie(Tool):
    EXEC_path = os.path.join(global_variables.stringtie_path, "stringtie")

    def __init__(self, input, output, user_params):
        super().__init__(input, output, user_params)
        self.DISABLED_ARGS = ["--merge"]

    def add_input(self, input_path):
        self.input_arg = input_path

    def add_output(self, output):
        input_file = os.path.basename(self.input)
        self.output_filename = input_file.replace(".sam", "count.gft")
        self.output_arg = "-o {}".format(output)

    def prepare_to_run(self):
        self.add_input(self.input)
        self.add_output(self.output_dir)
        self.command = ["{} {} {} {}".format(Stringtie.EXEC_path, self.input, self.params, self.output_arg)]
        self.prepare_to_run()


class samtools:
    @staticmethod
    def sam_to_bam(input_file, output_file):
        params = "view - S - b {} > {}".format(input_file, output_file)
        samtools.run(params)

    @staticmethod
    def sort_bam(input, output):
        params = "sort {} -o {}".format(input, output)
        samtools.run(params)

    @staticmethod
    def run(params):
        command = "{} {}".format(global_variables.samtools_path, params)
        process = subprocess.Popen(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        process.wait()

        # print(process.communicate()[1])
        if process.returncode != 0:
            raise ToolError(process.communicate()[1].decode("utf-8"))
        pass


s = Trimmomatic(
    "/home/kuba/ADP_project/HBR_Rep1_ERCC-Mix2_Build37-ErccTranscripts-chr22.read1.fastq /home/kuba/ADP_project/HBR_Rep1_ERCC-Mix2_Build37-ErccTranscripts-chr22.read2.fastq",
    "/home/kuba/ADP_project/",
    "PE LEADING:1 TRAILING:1 SLIDINGWINDOW:4:15 MINLEN:20")
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
s.run()
# SE -phred33  /home/kuba/output.fq
# print(FastQC.check_params("sadass"))
