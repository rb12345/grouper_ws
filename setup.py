try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


# Idea borrowed from http://cburgmer.posterous.com/pip-requirementstxt-and-setuppy
install_requires, dependency_links = [], []
for line in open('requirements.txt'):
    line = line.strip()
    if line.startswith('-e'):
        dependency_links.append(line[2:].strip())
    elif line:
        install_requires.append(line)

setup(
    name='grouper_ws',
    description="Grouper Web Services library for Python",
    author='Systems Development and Support, IT Services, University of Oxford',
    author_email='sysdev@it.ox.ac.uk',
    version='0.2.5',
    license='BSD',
    url='https://github.com/rb12345/grouper_ws',
    long_description=open('README.rst').read(),
    classifiers=['Development Status :: 4 - Beta',
                 'License :: OSI Approved :: BSD License',
                 'Natural Language :: English',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python',
                 'Topic :: Internet :: WWW/HTTP :: Dynamic Content'],
    packages=['grouper_ws'],
    package_dir={'grouper_ws': 'grouper_ws'},
    install_requires=install_requires,
    dependency_links=dependency_links,
)
