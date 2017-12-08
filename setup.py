from setuptools import setup

setup(
        name='papertrading',
        version='0.1',
        description='Command line tool used to simulate stock market investing.',
        url='https://github.com/JamesWhiteleyIV/Paper-Trading',
        author='James Whiteley IV',
        author_email='jameswhiteleyiv@gmail.com',
        license='MIT',
        classifiers=[
            'Programming Language :: Python :: 2.7',
            ],
        keywords='paper trading stock market investment pandas',
        packages=['papertrading'],
        #packages=find_packages(exclude=['docs', 'tests*']),
        #install_requires=['pandas', 'pandas-datareader', 'numpy', 'matplotlib'] #these get installed before this package
        include_package_data=True,
        zip_safe=False
        )
