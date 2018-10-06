from setuptools import find_packages, setup

setup(
    name="pynxos",
    version="0.1.0",
    packages=find_packages(),
    description="A library for managing Cisco NX-OS devices through NX-API.",
    author="Kirk Byers; Matt Schwenn; mzbenhami",
    author_email="ktbyers@twb-tech.com",
    url="https://github.com/ktbyers/pynxos/",
    download_url="https://github.com/ktbyers/pynxos/tarball/master",
    install_requires=["requests>=2.7.0", "future", "scp"],
)
