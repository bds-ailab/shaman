"""The ConfigurationBuilder is a class to automatically build the configuration files for the
accelerators, by asking the user to set values that are specific to his own setup
(for example, the name of his datanode).

When using the command iomodules-handler-configure, a python CLI program asks the user several
questions about his setup and then save  these information in a YAML file located by default
at io_modules/config/iomodules_config.yaml.
The different information needed for the program to work (such as the accelerator default) is
stored in the file io_modules/defaults/iomodules_config.yaml.

The configuration can be regenerated as many times as necessary by running the
iomodules-handler-configure executable.
"""

__copyright__ = """
Copyright (C) 2019 Bull S. A. S. - All rights reserved
Bull, Rue Jean Jaures, B.P.68, 78340, Les Clayes-sous-Bois, France
This is not Free or Open Source software.
Please contact Bull S. A. S. for details about its license.
"""
import os
from copy import deepcopy
import yaml
from .server_tools import check_rpm_installed


PACKAGE_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
READ_CONFIGURATION_PATH = os.path.join(PACKAGE_PATH, "io_modules/defaults/iomodules_config.yaml")
WRITE_CONFIGURATION_PATH = os.path.join(PACKAGE_PATH, "io_modules/config/iomodules_config.yaml")

# Name of the RPMs
FIOL_RPM_NAME = "fastio-optimizer-compute-1.2-Bull"
SBB_CLIENT_RPM_NAME = "flash-accelerators-client"
SBB_SLURM_RPM_NAME = "flash-accelerators-slurmd"

TYPE_MAPPING = {"str": str,
                "int": int,
                "bool": bool}


class ConfigurationBuilder:
    """
    The ConfigurationBuilder provides a way to build the configuration file for the IO modules by
    solliciting the help of the user.

    The python CLI program asks the user several questions about his setup and then save these
    informations in a YAML file located by default at io_modules/config/iomodules_config.yaml.
    """

    def __init__(self, read_conf=READ_CONFIGURATION_PATH, write_conf=WRITE_CONFIGURATION_PATH):
        """Takes as input the configuration file which contains all the defaults and outputs the
        configuration file which contains the values specific to the user.

        Args:
            read_conf (str, optional): The path to the configuration which contains the default
                values.
                Defaults to READ_CONFIGURATION_PATH.
            write_conf (str, optional): The path to the configuration file which will be specific
                to the user's installation.
                Defaults to WRITE_CONFIGURATION_PATH.
        """
        # Store configuration path
        self.read_config_path = read_conf
        self.write_config_path = write_conf
        # Ensure write directory exists
        os.makedirs(os.path.dirname(WRITE_CONFIGURATION_PATH), exist_ok=True)
        # Parse default configuration
        self.default_configuration = self.parse_configuration(self.read_config_path)
        self.configuration = None

    @staticmethod
    def parse_configuration(path):
        """Parses the YAML configuration file containing the defaults.

        Args:
            path (str): The path to the configuration file.

        Returns:
            The parsed configuration, as a dictionary.
        """
        with open(path, "rb") as _file:
            configuration = yaml.load(_file, Loader=yaml.SafeLoader)
        return configuration

    @staticmethod
    def ensure_fiol_installed(fiol_rpm=FIOL_RPM_NAME):
        """
        Ensure that FIOL rpm is installed then return nothing.
        Raise an OSError if FIOL rpm is not installed
        """
        if check_rpm_installed(fiol_rpm) is False:
            print(
                "FastIO Acceleration library is not installed. "
                "Contact package maintainer for information regarding installation procedure."
            )

    @staticmethod
    def ensure_sbb_client_installed(sbb_client_rpm=SBB_CLIENT_RPM_NAME):
        """Ensure that SBB client is installed then return nothing.
        Raise an OSError if SBB client rpm is not installed."""
        if not check_rpm_installed(SBB_CLIENT_RPM_NAME):
            print(
                "SBB Client library is not installed."
                "Contact package maintainer for information regarding installation procedure."
                )
        if not check_rpm_installed(SBB_SLURM_RPM_NAME):
            print(
                "SBB Slurm library is not installed. "
                "Contact package maintainer for information regarding installation procedure."
                )

    @staticmethod
    def ensure_input(input_, _type, default=None):
        """Checks that the value of input_ (provided by the user) is valid by:
            - Checking if input_ is empty and raising an error if there is no default provided
            - Checking that the type of input_ matches the type specified in the configuration.
        If it is valid, it returns the input correctly typed.

        Args:
            input_ (.): The input to check. Could be any type.
            _type (str): The type the input must be. Must be a key of the dictionary TYPE_MAPPING.
            default (str, optional): The default value for the input. Defaults to None.

        Returns:
            The input with the right type.
        """
        # Check cases where user returns nothing
        if input_ == "":
            # If a default is defined return the default
            if default is not None:
                return default
            # Else raise an error
            raise ValueError("Given value was empty. "
                             "Please provide a valid value")
        # If expected type is str then return value as is
        if _type == TYPE_MAPPING["str"]:
            return input_
        # If expected type is bool we cannot apply the bool function directly
        if _type == TYPE_MAPPING["bool"]:
            if input_.lower() in ["yes", "true", "1", "y"]:
                return True
            if input_.lower() in ["no", "n", "false", "0"]:
                return False
            raise ValueError(
                f"Could not cast value to {_type}. "
                "Please provide a valid value"
            )
        # Else juste try to apply the type and return new value
        try:
            return TYPE_MAPPING[_type](input_)
        except ValueError:
            raise ValueError(
                f"Could not cast value to {_type}. "
                "Please provide a valid value")

    def ask_field(self, name, _type, description="", default=None):
        """Asks the user to give an input for the field 'name' of the configuration.

        Args:
            name (str): The name of the field to fill.
            _type (str): The type of the input.
            description (str, optional): The description of the field. Defaults to "".
            default (str, optional): The default value for this field. Defaults to None.

        Returns:
            The user's input
        """
        if description:
            description = f"({description})"
        else:
            description = ""
        # Ask the user value and if it does not match the requirements,
        # ask the value again.
        # Prompted message is different if there is a default value
        try:
            if default:
                value = input(f"Set value for {name} {description} "
                              f"[default={default}] [type={_type}]:\n")
            else:
                value = input(f"{name} {description} "
                              f"[no default] [type={_type}]\n")
            return self.ensure_input(value, _type, default)
        except ValueError:
            print(f"Expected type {_type}. Try again.")
            return self.ask_field(name, _type, description, default)

    def get_section_configuration(self, section):
        """
        Stores the user's input in a dictionary that will be written to the new configuration file
        for the section 'section'.

        Args:
            section (str): The name of the section to store the inputs for.

        Returns:
            A dictionary containing the information for the section.
        """
        new_config = dict()
        # Iterate over each option defined in the section
        for option_name, option in self.default_configuration[section].items():
            new_option = deepcopy(option)
            # new value is assigned to default value or None
            new_option["value"] = default_value = option.get("default", None)
            expected_type = option.get("type", str)
            description = option.get("description", str)
            # If value needs to be set by user
            if option.get('ask_user'):
                # Replace new value with the validated input
                new_option["value"] = self.ask_field(option_name, expected_type, description,
                                                     default_value)
            # And update the section's configuration only for default and for value
            new_config[option_name] = new_option
        return new_config

    def build_configuration(self):
        """
        Asks if the user wants to setup the accelerator, and if yes,
        stores the different options as an attribute of the class.
        """
        configuration = dict()
        for section in list(self.default_configuration.keys()):
            skip = input(f"Do you want to generate configuration for {section} ?")
            if skip.lower() in ["yes", "true", "1", "y"]:
                print(f"Generating configuration for section {section}")
                section_config = self.get_section_configuration(section)
                configuration.update({
                    section: section_config
                })
                self.configuration = configuration
            elif skip.lower() in ["no", "n", "false", "0"]:
                print(f"Skipping set up for {section}")
            else:
                print("Please answer the question !")
        self.configuration = configuration
        print(
            "Configuration is done."
            f"Current configuration is set to: {self.dumps()}"
        )

    def dumps(self):
        """
        Dumps the configuration containing the user's input to a YAML.
        """
        return yaml.dump(self.configuration, default_flow_style=False)

    def write_config(self):
        """
        Writes the configuration containing the user's input to a YAML file located in the
        config/ folder of the package.
        """
        if self.configuration is not None:
            print(f"Writing configuration to {self.write_config_path}")
            with open(self.write_config_path, "w") as _file:
                yaml.dump(data=self.configuration, stream=_file, default_flow_style=False)
        else:
            raise ValueError(
                "Configuration has not been set yet."
                "You can use the `build_configuration()` method for that."
            )

    def run(self):
        """
        Runs the install procedure, by:
            - Checking if all RPMs are properly installed
            - Ask the user all the needed inputs
            - Write the inputs to a configuration file
        """
        self.ensure_fiol_installed()
        self.ensure_sbb_client_installed()
        self.build_configuration()
        self.write_config()


def main():
    """Main function which runs the configuration procedure."""
    proc = ConfigurationBuilder()
    proc.run()


if __name__ == "__main__":
    main()
