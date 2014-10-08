'''
Created on 08/10/2014

@author: bobbruno
'''

from Cython.Distutils import build_ext
from distutils.core import setup
from distutils.extension import Extension


ext_modules = [Extension("analysis",
                         ["analysis.pyx"])]

setup(
      name='tokenizer function',
      cmdclass={'build_ext': build_ext},
      ext_modules=ext_modules
      )
