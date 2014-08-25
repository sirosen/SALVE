from setuptools import setup

readme_text = ''
changelog_text = ''
with open('README.md', 'r') as f:
    readme_text = f.read()
with open('CHANGELOG.md', 'r') as f:
    changelog_text = f.read()

setup(
    name='salve',
    version='2.3.0',

    install_requires=['argparse'],
    packages=['salve', 'salve.api', 'salve.action', 'salve.block', 'salve.cli',
        'salve.filesys', 'salve.reader', 'salve.util'],
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
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Environment :: Console'
    ]
)
