from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="honestnft-shenanigans",
    version="0.0.1",
    description="HonestNFT Shenanigan Scanning Tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Convex-Labs/honestnft-shenanigans",
    author="Convex Labs",
    author_email="hello@convexlabs.xyz",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    packages=["extras", "metadata", "fair_drop"],
    include_package_data=True,
    install_requires=[
        "numpy>=1.18.4",
        "pandas>=1.1.5",
        "web3>=5.13.1",
        "requests>=2.25.1",
        "matplotlib>=3.3.4",
        "seaborn>=0.11.1",
        "ipfshttpclient>=0.8.0a2"
    ],
)
