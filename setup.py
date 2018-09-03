from setuptools import setup

setup(
    name='a6pgp',
    version='0.1',
    py_modules=['cli'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        a6pgp=cli:cli
    ''',
)
