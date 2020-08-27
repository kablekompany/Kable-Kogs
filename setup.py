import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Kable-Kogs",
    version="1.0.1",
    author="Trent Kable",
    author_email="trent@kablekompany.com",
    description="Cogs for Kr0nos",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kableko/Kable-Kogs",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
