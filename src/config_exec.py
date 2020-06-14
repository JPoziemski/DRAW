import logging
import os
import subprocess

import global_variables

import tools


class ConfigExec:
    """Object resposible for execute properly run tools provided in Config files"""

    def __init__(self, Config):
        self.logger = logging.getLogger(__name__)
        self.master_output_directory = os.path.join(global_variables.OUTPUT_DIRECTORY, Config.run_id)
        # os.mkdir(self.master_output_directory)
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
        output_dir = self.master_output_directory
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

                    tool_input = [input_arg, curr_output_dir, tool_params, self.Config.get_config_variable("seq_type")]
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
                annotation_file_name = self.Config.get_config_variable("annotation_file_name")
                annotation_file_path = os.path.join(global_variables.INPUT_DIRECTORY, annotation_file_name)


                for file_path in new_input_paths:
                    input_arg = file_path
                    tool_input = [input_arg, curr_output_dir, tool_params, annotation_file_path]
                    curr_tool = self.prepare_stage_tool(tool_for_stage, tool_input)

    def prepare_stage_tool(self, tool_name, tool_input):
        """Save command tor tool and get files path that will be created as resuts for this command

        :param tool_input  - input parameters for tool
        :type tool_input: list
        :param tool_name - name of tool
        :type tool_name: str
        :return: created files - list of path for created files
        ":rtype: list
        """
        if tool_name == "FastQC":
            curr_tool = tools.FastQC(*tool_input)
        elif tool_name == "TRIMMOMATIC":
            curr_tool = tools.Trimmomatic(*tool_input)
        elif tool_name == "Hisat2":
            curr_tool = tools.Hisat2(*tool_input)
        elif tool_name == "Bowtie2":
            curr_tool = tools.Bowtie(*tool_input)
        elif tool_name == "Stringtie":
            curr_tool = tools.Stringtie(*tool_input)
        else:
            raise ValueError
        self.run_order.append(curr_tool)
        created_files = curr_tool.get_created_files()
        return created_files

    def get_inital_files(self, input_dir):
        """"""
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
        """Get list of tulpes with corresponding paired-end files

        :param files_paths_list_to_group: list of all files to group
        :type files_paths_list_to_group: list
        :return: grouped_files - tulpes list with grouped files
        :rtype: list"""
        valid_files = sorted(files_paths_list_to_group)
        grouped_files = []
        for ind in range(len(valid_files) // 2):
            curr_paired_files_paths = tuple(valid_files[2 * ind:2 * ind + 2])
            grouped_files.append(curr_paired_files_paths)

        return grouped_files

    def prepare_files_to_counting(self, input_files_list, output_dir):
        """Converts sam files to bam and sort bam files

         :param input_files_list - path to directory containing sam files
         :type input_files_list: str
         :param output_dir - directory where output files will be saved
         :type output_dir: str
         :return: creted files - list of commands used to get and sort bam files
         :rtype: list
         """
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
        """Execute all commands necessary to complete config file instructions"""
        for processed_tool in self.run_order:
            # print(processed_tool.command)
            processed_tool.run()

    def prepare_data_for_visualalisation(self):
        """Create files necessary for visualisations
        """
        gft_files_path = os.path.join(self.master_output_directory, "COUNTING")
        gft_list_file_path = self.create_gft_list(gft_files_path)
        gene_count_matrix_path = os.path.join(self.master_output_directory, "COUNTING", "gene_count_matrix.csv")
        transcript_count_matrix_path = os.path.join(self.master_output_directory, "COUNTING",
                                                    "transcript_count_matrix.csv")

        command = "python3 prepDE_python3.py -i {} -g {} -t {}".format(gft_list_file_path, gene_count_matrix_path,
                                                                       transcript_count_matrix_path)
        process = subprocess.Popen([command], stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        process.wait()

        # print(process.communicate()[1])
        if process.returncode != 0:
            raise global_variables.ToolError(process.communicate()[1].decode("utf-8"))
        pass

    def create_gft_list(self, gft_files_path):
        """"Create file 'gft_list' object which is input for prepDE.py script

        :param gft_files_path - path to directory with
        :type gft_files_path: str
        :return: gft_file_path  - path for created 'gft_list' file
        :rtype: str
        """
        bam_files_list = [file for file in os.listdir(gft_files_path) if file.endswith("gft")]
        control_file_prefix = self.Config.get_config_variable("control_file_prefix")
        gft_list_data = []
        treated_num = 1

        for file in bam_files_list:
            file_path = os.path.join(gft_files_path, file)
            if file.startswith(control_file_prefix):
                gft_list_data.append(" ".join(["control", file_path]))
            else:
                gft_list_data.append(" ".join(["treated{}".format(treated_num), file_path]))
                treated_num += 1

        gft_file_path = os.path.join(self.master_output_directory, "COUNTING", "gft_list")
        gft_list_file = open(gft_file_path, "w")
        gft_list_file.write("\n".join(gft_list_data))
        gft_list_file.close()

        return gft_file_path
