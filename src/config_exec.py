import logging
import os

import global_variables

import tools


class ConfigExec:
    def __init__(self, Config):
        self.logger = logging.getLogger(__name__)
        self.Config = Config
        self.run_order = []
        self.input_files_paths = []
        file_type = self.Config.get_config_variable("run_type")

        if file_type == "complete_analysis":
            self.stages_order = global_variables.Complete_Analysis_Config_processing_order
        elif file_type == "analysis":
            self.stages_order = global_variables.Analysis_Config_processing_order
        else:
            self.stages_order = global_variables.Sequence_Prefiltering_processing_order

        self.create_stage_tool_dict()

    def create_stage_tool_dict(self):
        input_dir = global_variables.INPUT_DIRECTORY
        input_files_prefix = self.Config.get_config_variable("input_file_prefix")
        output_dir = global_variables.OUTPUT_DIRECTORY
        input_file_paths = self.get_inital_files(input_dir)

        for stage in self.stages_order:
            curr_output_dir = os.path.join(output_dir, stage)
            os.mkdir(curr_output_dir)
            tool_for_stage, tool_params = self.Config.get_tool_for_stage(stage)
            new_input_paths = []

            if stage == "INITIAL_QUALITY_CONTROL" or stage == "AFTER_TRIMMING_CONTROL":

                input_path = os.path.join(input_dir, input_files_prefix)
                tool_input = [input_path, curr_output_dir, tool_params]
                __ = self.prepare_stage_tool(tool_for_stage, tool_input)


            elif stage == "TRIMMING":
                tool_for_stage, tool_params = self.Config.get_tool_for_stage(stage)

                for obj in input_file_paths:
                    if isinstance(obj, tuple):
                        input_arg = " ".join(obj)
                    else:
                        input_arg = obj

                    tool_input = [input_arg, curr_output_dir, tool_params]
                    created_files = self.prepare_stage_tool(tool_for_stage, tool_input)
                    new_input_paths.extend(created_files)

                if self.Config.get_config_variable("seq_type") == "paired_end":
                    new_input_paths = self.group_paired_end_files(new_input_paths)

                input_file_paths = new_input_paths[:]


            elif stage == "MAPPING":
                tool_for_stage, tool_params = self.Config.get_tool_for_stage(stage)
                reference_path = os.path.join(global_variables.INPUT_DIRECTORY,
                                              self.Config.get_config_variable("reference_file_name"))

                for obj in input_file_paths:
                    input_arg = obj
                    tool_input = [input_arg, curr_output_dir, tool_params, reference_path]
                    created_files = self.prepare_stage_tool(tool_for_stage, tool_input)
                    new_input_paths.extend(created_files)

                input_file_paths = new_input_paths[:]


            elif stage == "COUNTING":
                bam_files_path = os.path.join(curr_output_dir, "bam_files")
                os.mkdir(bam_files_path)
                new_input_paths = self.prepare_files_to_counting(input_file_paths, bam_files_path)
                tool_for_stage, tool_params = self.Config.get_tool_for_stage(stage)

                for file_path in new_input_paths:
                    input_arg = file_path
                    tool_input = [input_arg, curr_output_dir, tool_params]
                    curr_tool = self.prepare_stage_tool(tool_for_stage, tool_input)

    def prepare_stage_tool(self, tool_for_stage, tool_input):
        if tool_for_stage == "FastQC":
            curr_tool = tools.FastQC(*tool_input)
        elif tool_for_stage == "TRIMMOMATIC":
            curr_tool = tools.Trimmomatic(*tool_input)
        elif tool_for_stage == "Hisat2":
            curr_tool = tools.Hisat2(*tool_input)
        elif tool_for_stage == "Bowtie2":
            curr_tool = tools.Bowtie(*tool_input)
        elif tool_for_stage == "Stringtie":
            curr_tool = tools.Stringtie(*tool_input)
        else:
            raise ValueError
        self.run_order.append(curr_tool)
        created_files = curr_tool.get_created_files()
        return created_files

    def get_inital_files(self, input_dir):

        input_files_prefix = self.Config.get_config_variable("input_file_prefix")
        input_files_paths = []
        if self.Config.get_config_variable("seq_type") == "single_end":
            for file_name in os.listdir(input_dir):
                if file_name.startswith(input_files_prefix):
                    input_files_paths.append(os.path.join(input_dir, file_name))
        else:
            valid_files = [file_name for file_name in os.listdir(input_dir) if file_name.startswith(input_files_prefix)]
            valid_files_paths_list = [os.path.join(input_dir, file_name) for file_name in valid_files]
            input_files_paths = self.group_paired_end_files(valid_files_paths_list)

        return input_files_paths

    def group_paired_end_files(self, files_paths_list_to_group):

        valid_files = sorted(files_paths_list_to_group)
        grouped_files = []
        for ind in range(len(valid_files) // 2):
            curr_paired_files_paths = tuple(valid_files[2 * ind:2 * ind + 2])
            grouped_files.append(curr_paired_files_paths)

        return grouped_files

    def prepare_files_to_counting(self, input_files_list, output_dir):

        created_files = []
        for file_path in input_files_list:
            file_name = os.path.basename(file_path)
            bam_file_name = file_name.replace(".sam", ".bam")
            bam_file_path = os.path.join(output_dir, bam_file_name)

            samtools_convert = tools.samtools()
            samtools_convert.sam_to_bam(file_path, bam_file_path)
            self.run_order.append(samtools_convert)
            sorted_bam_path = bam_file_path.replace(".bam", "_sorted.bam")

            samtools_sort = tools.samtools()
            samtools_sort.sort_bam(bam_file_path, sorted_bam_path)
            self.run_order.append(samtools_sort)
            created_files.append(sorted_bam_path)

        return created_files

    def run(self):
        for processed_tool in self.run_order:
            # print(processed_tool.command)
            processed_tool.run()
