from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="trezor-pass",
    version="1.2.0",
    description="Trezor Password Manager Command-Line interface",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pilartomas/trezor-password-manager-cli",
    author="Tomas Pilar",
    author_email="thomas7pilar@gmail.com",
    classifiers=[
            "Programming Language :: Python :: 3",
            "Operating System :: OS Independent",
            "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)"
    ],
    keywords="trezor, password",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.7, <4",
    install_requires=["trezor", "cryptography", "inquirerpy", "dropbox", "appdirs", "pyperclip"],
    entry_points={
        "console_scripts": [
            "trezor-pass=trezorpass.cli:run",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/pilartomas/trezor-password-manager-cli/issues",
    },
)