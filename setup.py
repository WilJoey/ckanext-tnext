from setuptools import setup, find_packages
import sys, os

version = '0.2'

setup(
    name='ckanext-tnext',
    version=version,
    description="Tainan open data ckan extension",
    long_description='''
    ''',
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='tainan',
    author_email='tainanod@gmail.com',
    url='',
    license='mit',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['ckanext', 'ckanext.tnext'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
    ],
    entry_points='''
        [ckan.plugins]
        tnext=ckanext.tnext.plugin:TnextPlugin
    ''',
)
