from setuptools import setup, find_packages
import salve

readme_text = ''
changelog_text = ''
with open('README.rst', 'r') as f:
    readme_text = f.read()
with open('CHANGELOG.rst', 'r') as f:
    changelog_text = f.read()

setup(
    name='salve',
    version=salve.__version__,

    install_requires=['argparse'],
    packages=find_packages(exclude=['tests']),
    package_data={'': ['*.ini']},
    entry_points={'console_scripts': ['salve = salve.cli:main']},

    description='SALVE Configuration Deployment Language',
    long_description=readme_text + '\n\n\n' + changelog_text,
    author='Stephen Rosen',
    author_email='sirosen@uchicago.edu',
    url='http://salve.sirosen.net/',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'License :: OSI Approved :: Apache Software License',
        'Environment :: Console'
    ]
)
