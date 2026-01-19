from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="generic-agent",
    version="0.1.0",
    author="Generic-Agent Team",
    author_email="team@generic-agent.org",
    description="A generic Agent Python agent that takes in the parameters it needs to run an agent workflow",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/generic-agent/generic-agent",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        # Add dependencies here
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black",
            "flake8",
        ],
    },
)