from setuptools import setup, find_packages


def read_version(module_name):
    from re import match, S
    from os.path import join, dirname

    with open(join(dirname(__file__), module_name, "__init__.py")) as f:
        return match(r".*__version__.*('|\")(.*?)('|\")", f.read(), S).group(2)


setup(
    name="gongish",
    version=read_version("gongish"),
    description="A simple and fast HTTP framework for Python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="http://github.com/meyt/gongish",
    author="Mahdi Ghane.g",
    license="MIT",
    keywords="web tool-chain",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Unix",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries",
    ],
    entry_points={"console_scripts": ["gongish = gongish.cli:main"]},
    install_requires=["pymlconf == 2.2.0"],
)
