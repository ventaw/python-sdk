
from setuptools import setup, find_packages

setup(
    name="ventaw",
    version="0.1.0",
    description="Python SDK for Ventaw AI Sandboxes",
    author="Ventaw",
    author_email="support@ventaw.com",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
    ],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
)
