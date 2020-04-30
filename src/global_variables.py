stage_tool_mapping_dict = {
    "INITIAL_QUALITY_CONTROL": ["FastQC"],
    "TRIMMING": ["TRIMMOMATIC"],
    "AFTER_TRIMMING_CONTROL": ["FastQC"],
    "MAPPING": ["Bowtie2", "STAR"],
    "COUNTING": ["HTSEQ"]
}
