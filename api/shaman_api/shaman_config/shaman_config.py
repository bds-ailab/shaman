"""
Given data sent by the user from the Web Interface, builds the corresponding experiment
configuration.
"""
import configparser


class ShamanConfig:
    """Class to build a shaman configuration file from the data sent by the user.
    """
    CONFIGURATION_KEYS = {
        "EXPERIMENT": ["with_ioi", "default_first"],
        "PRUNING_STRATEGY": ["max_step_duration"],
        "NOISE_REDUCTION": ["resampling_policy", "fitness_aggregation", "nbr_resamples", "percentage", "estimator"],
        "BBO": ["heuristic", "initial_sample_size",
                "selection_method", "crossover_method",
                "mutation_method", "mutation_rate", "elitism",
                "regression_model", "next_parameter_strategy",
                "cooling_schedule", "restart"]
    }

    def __init__(self, default_file, output_file):
        """Initialize an object of class ShamanConfig, by using a default file and creating an
        output file.

        Args:
            default_file (str): The path to the default file.
            output_file (str): The path to the file to output.
        """
        # Open the default_file and store it as
        self.config = configparser.ConfigParser()
        self.config.read(default_file)
        # Save the path to the output file as attribute
        self.output_file = output_file

    def filter_post_data(self, post_data):
        """Separate the post_data into a nested with three top level keys:
            - experiment: parameters concerning the experiment
            - bbo_parameters: parameters concerning the BBO package
            - pruning_strategy: parameters concerning the pruning strategy.
            - noise_experiment: parameters concerning the noise reduction

        Args:
            post_data (dict): the data sent by the user containing the different configuration
                parameters.

        Returns:
            dict: a filtered dictionary.
        """
        filtered_data = {}
        # Iterate over configuration keys to properly separate the post_data
        for section, parameters in self.CONFIGURATION_KEYS.items():
            filtered_data[section] = {
                parameter: post_data[parameter] for parameter in parameters if post_data.get(parameter) is not None}
        return filtered_data

    def update_section(self, section_name, update_dict):
        """Update the section 'section_name' with the data contained in update_dict.

        Args:
            config (ConfigParser): The configuration object.
            section_name (str): The name of the section to update
            update_dict (dict): The data to use in the update.
        """
        config_current = self.config._sections[section_name]
        config_current.update(update_dict)
        self.config._sections[section_name] = config_current

    def build_configuration(self, post_data):
        """Build the configuration from a default file by filling out the different values using the
        data contained in the dictionary 'post_data'.

        Args:
            post_data (dict): Dictionary containing the parameters of the experiment
        """
        # Separate the data into the three possible sections of the CFG, filtering on the fields
        config_dicts = self.filter_post_data(post_data)
        # Update each section of the configuration
        self.update_section('BBO', config_dicts['BBO'])
        self.update_section('NOISE_REDUCTION', config_dicts['NOISE_REDUCTION'])
        self.update_section('EXPERIMENT', config_dicts['EXPERIMENT'])
        self.update_section('PRUNING_STRATEGY',
                            config_dicts['PRUNING_STRATEGY'])
        # Save the result in file
        self.save_configuration()

    def save_configuration(self):
        """Save the configuration file in the location indicated by the attribute output file.
        """
        with open(self.output_file, 'w') as configfile:
            self.config.write(configfile)
