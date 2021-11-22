import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parent

README = (HERE / "DOCUMENTATION.txt").read_text()

setup(
    name="MDO-Stella",
    version="1.0.0",
    description="MDO for small UAVs",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/Matheus-Ribeiro-ITA/TG-Stella-MDO",
    author="Matheus Ribeiro Sampaio",
    author_email="matheus.ribeiro.aer@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["MDO", "avl", "results"],
    include_package_data=True,
    install_requires=['numpy', 'matplotlib', 'scipy'],
    entry_points={
    },
)