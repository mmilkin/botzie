from setuptools import setup, find_packages


setup(
    name='botzie',
    version='0.01',
    author='Michael Milkin',
    author_email='mmilkin@mmilkin.com',
    packages=find_packages(exclude=['tests']),
    install_requires=['Twisted', 'pyyaml', 'pyopenssl', 'pypubsub'],
)
