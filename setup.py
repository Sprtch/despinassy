import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="despinassy-pkg-tperale",
    version="0.0.1",
    author="tperale",
    author_email="perale.thomas@gmail.com",
    description="SQLAlchemy Global model",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sprtch/despinassy",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=["Flask-SQLAlchemy"],
)
