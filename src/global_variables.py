import os

stage_tool_mapping_dict = {
    "INITIAL_QUALITY_CONTROL": ["FastQC"],
    "TRIMMING": ["TRIMMOMATIC"],
    "AFTER_TRIMMING_CONTROL": ["FastQC"],
    "MAPPING": ["Bowtie2", "Hisat2"],
    "COUNTING": ["HTSEQ", "Stringtie"]
}
INPUT_DIRECTORY = os.path.abspath("../input")
OUTPUT_DIRECTORY = os.path.abspath("../output")
CONFIG_DIRECTORY = os.path.abspath("../config_files")

Sequence_Prefiltering_processing_order = ["INITIAL_QUALITY_CONTROL",
                                          "TRIMMING",
                                          "AFTER_TRIMMING_CONTROL"]

Complete_Analysis_Config_processing_order = ["INITIAL_QUALITY_CONTROL",
                                             "TRIMMING",
                                             "AFTER_TRIMMING_CONTROL",
                                             "MAPPING",
                                             "COUNTING"]

Analysis_Config_processing_order = ["MAPPING",
                                    "COUNTING"]
AFTER_TRIMMING_FILE_NAMES_ENDINGS = {"1": ("paired_1.fastq", "1_unpaired.fastq"),
                                     "2": ("paired_2.fastq", "2_unpaired.fastq")}


class ToolError(Exception):
    """Raised when the return code of tool is not 0 or provided parameters are wrong"""

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return "{}".format(self.message)
        else:
            "ToolError"


fastqc_path = os.path.abspath("../tools/FastQC")
trimmomatic_path = os.path.abspath("../tools/Trimmomatic-0.39")
hisat2_path = os.path.abspath("../../Pobrane/hisat2-2.2.0")
bowtie_path = os.path.abspath("../../bowtie2-2.3.5.1-linux-x86_64")
stringtie_path = os.path.abspath("../../stringtie-2.1.2")
# samtools_path = os.path.abspath("../bin/samtools")
samtools_path = "samtools"
