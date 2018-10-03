# setup.py
'''

'''
from setuptools import setup, find_packages

with open('./shraklor/blink/_constants.py') as constants:
    exec(constants.read())

NAMESPACE_PACKAGES=['shraklor']

setup(
    name=__APP_NAME__,
    version=__APP_VERSION__,
    description="used to simplify calls to Blink REST API",
    install_requires=['shraklor.http', 'logging', 'json', 'datetime'],
    extras_require={'test':['pytest', 'pytest-cov', 'pylint', 'sphinx']}
    packages=find_packages(),
    author='brad.source@gmail.com',
    include_package_data=True,
    namespace_packages=NAMESPACE_PACKAGES,
    url="githib"
)
