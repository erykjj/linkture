import setuptools
from pathlib import Path

work_dir = Path(__file__).parent
long_description = (work_dir / 'README.md').read_text()


setuptools.setup(

    name='linkture',
    version='2.5.4',
    author='Eryk J.',
    author_email='infiniti@inventati.org',
    url='https://github.com/erykjj/linkture',
    license='MIT',

    description='PARSE and PROCESS BIBLE SCRIPTURE REFERENCES: extract, tag, link, rewrite, translate, BCV-encode and decode',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords=[
        'bible', 'scriptures', 'scripture-references', 'scripture-translation',
        'scripture-parser', 'scripture-linker'
    ],

    packages=setuptools.find_packages(),
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Topic :: Religion',
        'Topic :: Text Processing :: General',
        'Topic :: Text Processing :: Linguistic'
    ],
    python_requires='>=3.9',
    install_requires=[
        'setuptools>=59.6.0',
        'argparse>=1.4.0',
        'regex>=2023.8.8',
        'unidecode>=1.3.8',
        'pathlib>=1.0.1',
        'pandas==2.2.2'
    ]

)