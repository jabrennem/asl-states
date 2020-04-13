from setuptools import find_packages, setup

module_name = 'asl_states'

setup(
    name=module_name,
    version="1.0.0",
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
)
