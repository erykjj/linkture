import setuptools
from pathlib import Path

work_dir = Path(__file__).parent
long_descr = (work_dir / "README.md").read_text()

setuptools.setup(

    name="linkture",
    version="1.2.2",
    author="Eryk J.",
    url="https://github.com/erykjj/linkture",

    description="Process and link/code Bible references",
    long_description = long_descr
    long_description_content_type="text/markdown"


    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',

)