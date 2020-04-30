import abc
import logging
import os

import global_variables
from config_parser_tools import get_cpu_number


class Config_Parser(metaclass=abc.ABCMeta):
    GLOBAL_CONFIG_VARIABLES = ["run_type",
                               "seq_type",
                               "input_file_dir",
                               "input_file_prefix",
                               "output_dir",
                               "threads_number"]

    STAGES = ()

    def __init__(self, json_file):
        self.logger = logging.getLogger(__name__)
        # self.logger.info('This is an info asdsassa message')
        # self.logger.warning('This is a warning asdas message')
        self.config_data = json_file
        self.STAGES = ()

    def check_global_config_variables(self):
        """Checks if prvided global config parameters (that are avaliable for all config file) are correct"""

        def check_global_config_variables_presence():
            for var in Config_Parser.GLOBAL_CONFIG_VARIABLES:
                if var not in self.config_data:
                    message = "{} not exists in input json file".format(var)
                    self.logger.error(message)
                    raise KeyError(message)

            return True

        def check_seq_type():
            seq_type = self.config_data["seq_type"]
            # print(seq_type)
            if seq_type != "single_end" and seq_type != "paired_end":
                message = "Incorrect seq_type set 'single_end' or 'paired_end'"
                self.logger.error(message)
                raise ValueError(message)

        def check_input_files_dir():
            input_dir = self.config_data["input_file_dir"]

            if not os.path.isdir(input_dir):
                message = "input_dir not exists"
                self.logger.error(message)
                raise ValueError(message)

        def check_input_file_prefix():
            input_file_prefix = self.config_data["input_file_prefix"]
            input_file_dir = self.config_data["input_file_dir"]

            input_files_count = 0
            for file in os.listdir(input_file_dir):
                if file.startswith(input_file_prefix):
                    input_files_count += 1

            if input_files_count < 1:
                message = "No input files"
                self.logger.error(message)
                raise ValueError(message)

        def check_output_dir():
            output_dir = self.config_data["output_dir"]

            if not os.path.isdir(output_dir):
                self.logger.warning("output_dir not exists")
                os.mkdir(output_dir)
                self.logger.debug("Creates dir: {}".format(output_dir))

        def check_thread_number_correctness():
            thread_number = self.config_data["threads_number"]
            max_threads = get_cpu_number()
            if not isinstance(1, int):
                self.logger.error("threads number must be integer")
                raise TypeError()

            if thread_number > max_threads:
                self.logger.warning("threads number must be integer")
                raise ValueError("thread number is more than available")

        check_global_config_variables_presence()
        check_seq_type()
        check_input_files_dir()
        check_output_dir()
        check_input_file_prefix()

        try:
            check_thread_number_correctness()
        except (ValueError, TypeError):
            self.logger.debug("Setting max threads number")
            self.config_data["threads_number"] = get_cpu_number()

    @abc.abstractmethod
    def check_config_specific_variables(self):
        """Checks variables specific for particular config file type"""
        pass

    def check_tool_for_stages(self):
        """Checks if provided tool is available for required stage"""

        def check_all_stages_presence():
            for step in self.STAGES:
                if step not in self.config_data["tools"]:
                    raise KeyError("{} is missing in config file ".format(step))

        def check_if_proper_tool_for_stage():
            stages = self.config_data["tools"]
            for stage in stages:
                stage_tool = self.config_data["stage"]
                available_stages = global_variables.stage_tool_mapping_dict["stage"]
                if stage_tool not in available_stages:
                    message = "{} is not avalible in stage {}, Try use: {}".format(stage_tool, stage, available_stages)
                    self.logger.error(message)
                    raise KeyError(message)

        check_all_stages_presence()
        check_if_proper_tool_for_stage()

    def get_tool_for_stage(self, stage):
        """Returns tool with parameters for stage
        :param stage(string): stage name eg 'MAPPING'
        :return tool(string): tool name
        :return tool_param(string): parameters for tools assigned to 'stage'"""
        if stage not in self.STAGES:
            message = "{} is not available for this config file".format(stage)
            self.logger.error(message)
            raise KeyError(message)

        tool = list(self.config_data["tools"][stage].keys())[0]
        tool_param = self.config_data["tools"][stage][tool]
        return tool, tool_param

    def get_config_variable(self, variable):
        """return value of variable in config data
        :param variable(string): variable name eg seq_type
        :return var_value(string): value assigned to 'variable' """
        if variable not in self.config_data[variable]:
            message = "{} is not in input config file".format(variable)
            self.logger.error(message)
            raise KeyError(message)
        else:
            var_value = self.config_data[variable]
            return var_value


class Complete_Analysis_Config(Config_Parser):
    COMPLETE_ANALYSIS_CONFIG_VARIABLES = ["run_downstream_analysis",
                                          "annotation_file_path",
                                          "control_file_prefix", ]

    def __init__(self, json_file):
        super().__init__(json_file)
        self.STAGES = ("INITIAL_QUALITY_CONTROL", "TRIMMING", "AFTER_TRIMMING_CONTROL", "MAPPING", "COUNTING")
        self.check_global_config_variables()
        self.logger.info("SUCCESS - global config variables checked")
        self.check_config_specific_variables()
        self.logger.info("SUCCESS - config file specific variables checked")
        self.check_tool_for_stages()
        self.logger.info("SUCCESS - tools to stages assignment checked")

    def check_config_specific_variables(self):

        def check_specific_global_config_variables_presence():
            for var in Complete_Analysis_Config.COMPLETE_ANALYSIS_CONFIG_VARIABLES:
                if var not in self.config_data:
                    message = "{} not exists in input json file".format(var)
                    self.logger.error(message)
                    raise KeyError(message)
            return True

        def check_run_downstream_analysis():
            run_downstream_analysis = self.config_data["run_downstream_analysis"]
            if not isinstance(run_downstream_analysis, bool):
                message = "run_downstream_analysis in not bool type"
                self.logger.error(message)
                raise TypeError(message)

        def check_annotation_file_path():
            annotation_file_path = self.config_data["annotation_file_path"]
            if not os.path.isfile(annotation_file_path):
                message = "file {} not found".format(annotation_file_path)
                self.logger.error(message)
                raise ValueError(message)

        def check_control_file_prefix():
            run_downstream_analysis_value = self.config_data["run_downstream_analysis"]
            if run_downstream_analysis_value:
                control_file_prefix = self.config_data["control_file_prefix"]
                input_file_dir = self.config_data["input_file_dir"]
                control_files_count = 0

                for file in os.listdir(input_file_dir):
                    if file.startswith(control_file_prefix):
                        control_files_count += 1

                if control_files_count < 1:
                    message = "No control files"
                    self.logger.error(message)
                    raise ValueError(message)

        check_specific_global_config_variables_presence()
        check_run_downstream_analysis()
        check_annotation_file_path()
        check_control_file_prefix()


class Sequence_Prefiltering_Config(Config_Parser):
    SEQUENCE_PREFILTERING_CONFIG_VARIABLES = []

    def __init__(self, json_file):
        super().__init__(json_file)
        self.STAGES = ("INITIAL_QUALITY_CONTROL", "TRIMMING", "AFTER_TRIMMING_CONTROL")

        self.check_global_config_variables()
        self.logger.info("SUCCESS - global config variables checked")
        self.check_tool_for_stages()
        self.logger.info("SUCCESS - tools to stages assignment checked")

    def check_config_specific_variables(self):
        pass


class Analysis_Config(Complete_Analysis_Config):

    def __init__(self, json_file):
        super().__init__(json_file)
        self.STAGES = ("MAPPING", "COUNTING")
