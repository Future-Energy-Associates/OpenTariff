import setuptools

with open("README.md", "r", encoding="utf8", errors="ignore") as fh:
    long_description = fh.read()

setuptools.setup(
    name="OpenTariff",
    version="0.0.1",
    author="Future Energy Associates",
    author_email="hello@futureenergy.associates",
    description="Open source tariff definitions and utilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/future-energy-associates/open-tariff",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 3 - Alpha",
    ],
    python_requires=">=3.11",
)
