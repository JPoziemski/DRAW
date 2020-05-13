import global_variables
import os

import global_variables

import tools


class config_exec:
    def __init__(self, Config):
        self.logger = logging.getLogger(__name__)
        self.Config = Config
        self.run_order = []
        file_type = self.Config.get_config_variable("run_type")

        if file_type == "complete_analysis":
            self.stages_order = global_variables.Complete_Analysis_Config_processing_order
        elif file_type == "analysis":
            self.stages_order = global_variables.Analysis_Config_processing_order
        else:
            self.stages_order = global_variables.Sequence_Prefiltering_processing_order

    def create_stage_tool_dict(self):
        input_dir = self.Config.get_config_variable("input_file_dir")
        input_files_prefix = self.Config.get_config_variable("input_file_prefix")
        output_dir = self.Config.get_config_variable("output_dir")

        for stage in self.stages_order:
            output_dir = os.path.join(output_dir, stage)
            tool_for_stage, tool_params = self.Config.get_tool_for_stage(stage)
            new_input_paths = []
            if stage == "INITIAL_QUALITY_CONTROL" or stage == "AFTER_TRIMMING_CONTROL":
                input_path = os.path.join(input_dir, input_files_prefix)
                tool_input = [input_path, output_dir, tool_params]
                curr_tool = self.prepare_stage_tool(stage, tool_for_stage, tool_input)
                self.run_order.append(curr_tool)
            elif stage == "TRIMMING":
                tool_for_stage, tool_params = self.Config.get_tool_for_stage(stage)

                for obj in self.input_file_paths:
                    if isinstance(obj, tuple):
                        input_arg = " ".join(obj)
                    else:
                        input_arg = obj

                    tool_input = [input_arg, output_dir, tool_params]
                    curr_tool = self.prepare_stage_tool(stage, tool_for_stage, tool_input)
                    self.run_order.append(curr_tool)
                    new_input_paths.append(())

    def prepare_stage_tool(self, stage, tool_for_stage, tool_input):
        if stage == "INITIAL_QUALITY_CONTROL" or stage == "AFTER_TRIMMING_QUALITY_CONTROL":
            if tool_for_stage == "FastQC":
                return tools.FastQC(*tool_input)
        elif stage == "TRIMMING":
            if tool_for_stage == "TRIMMOMATIC":
                return tools.Trimmomatic(*tool_input)
        elif stage == "MAPPING":
            if tool_for_stage == "Hisat2":
                return tools.Hisat2(*tool_input)
            elif tool_for_stage == "Bowtie2":
                return tools.Bowtie2(*tool_input)
        else:
            if tool_for_stage == "Stringtie":
                return tools.Stringtie(*tool_input)

    def get_inital_files(self, input_dir):

        input_files_prefix = self.Config.get_config_variable("input_file_prefix")
        input_files_paths = []
        if self.Config.get_config_variable("seq_type") == "single_end":
            for file_name in os.listdir(input_dir):
                if file_name.startswith(input_files_prefix):
                    self.input_files_paths.append(os.path.join(input_dir, file_name))
        else:
            valid_files = [file_name for file_name in os.listdir(input_dir) if file_name.startswith(input_files_prefix)]
            sorted_files = sorted(valid_files)
            for ind in range(len(sorted_files) // 2):
                curr_paired_files = sorted_files[2 * ind:2 * ind + 2]
                curr_paired_files_paths = (os.path.join(input_dir, file_name) for file_name in curr_paired_files)
                self.input_files_paths.append(curr_paired_files_paths)
