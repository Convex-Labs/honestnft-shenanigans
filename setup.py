from setuptools import setup, find_packages

extras_require = {
    "dev": [
        "pre-commit",
        "black[jupyter]",
    ],
    "test": [
        "tox",
        "coverage[toml]",
        "mypy",
        "nbqa",
    ],
    "doc": [
        "Sphinx==5.0.2",
        "sphinx-rtd-theme==1.0.0",
        "sphinx-autodoc-typehints==1.18.3",
        "pandoc",
        "nbsphinx==0.8.9",
        "sphinxcontrib-youtube==1.2.0",
        "sphinxcontrib-autoprogram @ git+https://github.com/Barabazs/autoprogram#egg=sphinxcontrib-autoprogram",
    ],
}


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="honestnft-shenanigans",
    version="0.1.0",
    description="HonestNFT Shenanigan Scanning Tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Convex Labs",
    author_email="hello@convexlabs.xyz",
    url="https://github.com/Convex-Labs/honestnft-shenanigans",
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    install_requires=[
        "numpy>=1.18.4",
        "pandas>=1.1.5",
        "web3==5.27.0",
        "requests>=2.25.1",
        "matplotlib>=3.3.4",
        "seaborn>=0.11.1",
        "ipfshttpclient>=0.8.0a2",
        "scikit-learn>=1.0.1",
        "papermill==2.3.3",
        "multicall==0.5.1",
        "python-dotenv==0.19.2",
        "plotly==5.6.0",
        "py-is_ipfs==0.5.1",
        "beautifulsoup4==4.11.1",
    ],
    python_requires=">=3.8.0",
    extras_require=extras_require,
    license="MIT",
    keywords="honestnft blockchain ethereum web3 nft analysis",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
