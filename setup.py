import setuptools

setuptools.setup(

    name="linkture",

    version="1.2.1",

    author="Eryk J.",

    author_email="infiniti@inventati.org",

    description="Process and link/code Bible references",

    long_description="Functions to convert scriptures to a list of coded ranges or to .jwpub links. This script *does not* parse text files for scriptures - it only parses what is enclosed within {{ }} or provided as a string argument. Also, it doesn't check if chapters or verses actually exist (within range). Make sure the scriptures use common English names/abbreviations.",

    long_description_content_type="text/markdown",

    url="https://github.com/erykjj",

    packages=setuptools.find_packages(),

    classifiers=[

        "Programming Language :: Python :: 3",

        "License :: OSI Approved :: MIT License",

        "Operating System :: OS Independent",

    ],

    python_requires='>=3.6',

)