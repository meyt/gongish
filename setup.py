from setuptools import find_packages, setup


def read_version(module_name):
    from os.path import dirname, join
    from re import S, match

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
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Unix",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    entry_points={"console_scripts": ["gongish = gongish.cli:main"]},
    install_requires=["pymlconf == 2.2.0"],
)
