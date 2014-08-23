from setuptools import setup

setup(
    name='salve',
    packages=['salve', 'salve.api', 'salve.action', 'salve.block', 'salve.cli',
        'salve.filesys', 'salve.reader', 'salve.util'],
    version='2.3.0',
    description='SALVE Configuration Deployment Language',
    author='Stephen Rosen',
    author_email='sirosen@uchicago.edu',
    url='http://salve.sirosen.net/',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'License :: Apache 2.0',
        'Operating System :: OS Independent',
        'Environment :: Console'
    ],
    entry_points={'console_scripts': ['salve = salve.cli:main']}
)
