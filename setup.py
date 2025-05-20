import setuptools


VERSION = '0.1.3'
REQUIREMENTS = [i.strip() for i in open('requirements.txt').readlines()]

with open('README.md', 'r', encoding='utf8') as f:
    long_description = f.read()


setuptools.setup(
    name='gradescope-tool',
    packages=['gradescope'],
    version=VERSION,
    author='HyunJun Park, Daniel Song',
    author_email='hyunjup4@uci.edu, djsong1@uci.edu',
    description='A Python wrapper for Gradescope to easily retrieve data from your Gradescope Courses.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Teaching-and-Learning-in-Computing/Gradescope',
    license='MIT License',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    install_requires=REQUIREMENTS
)
