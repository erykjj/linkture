import setuptools

setuptools.setup(

    name="linkture",

    version="1.0.0",

    author="Eryk J.",

    author_email="infiniti@inventati.org",

    description="Process Bible references",

    long_description="Process Bible references and convert them into jwpub links",

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