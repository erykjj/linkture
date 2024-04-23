import setuptools
from pathlib import Path

work_dir = Path(__file__).parent
long_description = (work_dir / "README.md").read_text()


setuptools.setup(

    name="linkture",
    version="2.5.3",
    author="Eryk J.",
    url="https://github.com/erykjj/linkture",

    description="PARSE and PROCESS BIBLE SCRIPTURE REFERENCES: extract, tag, link, rewrite, translate, BCV-encode and decode",
    long_description=long_description,
    long_description_content_type="text/markdown",

    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
    install_requires=[ 'argparse', 'pandas', 'pathlib', 'regex', 'unidecode' ]

)