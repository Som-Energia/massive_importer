import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="massive-importer", # Replace with your own username
    version="0.0.1",
    author="davids",
    author_email="davidsuarez92@gmail.com",
    description="massive importer atr spain",
    long_description="",
    long_description_content_type="text/markdown",
    url="https://github.com/Som-Energia/massive_importer",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

