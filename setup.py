from setuptools import setup

setup(
    # other setup arguments
    exclude_package_data=['thinc.tests.mypy.configs', 'thinc.tests.mypy.outputs']
)
