from __future__ import print_function
import sys
from setuptools import setup, find_packages

if sys.version_info < (3,5):
    print("SMPDF requires Python 3.5 or later", file=sys.stderr)
    sys.exit(1)

with open('README.md') as f:
    long_desc = f.read()

setup(name= "yamldiff",
      version = '0.1',
      description = "Semantic difference for YAML files",
      author = "Zahari Kassabov",
      author_email = "kassabov@to.infn.it",
      url="https://github.com/Zaharid/yamldiff",
      long_description = long_desc,
      entry_points = {'console_scripts': 
                    ['yamldiff = yamldiff.scripts.main:main']},
      package_dir = {'': 'src'},
      packages = find_packages('src'),
      zip_safe = False,
      classifiers=[
            'License :: OSI Approved :: BSD License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.5',
            ],
     )
      
