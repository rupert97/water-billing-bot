"""Setup configuration for Water Billing Tracker Bot"""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="water-billing-bot",
    version="1.0.0",
    author="Water Billing Bot Contributors",
    description="Serverless automation tool for water bill notifications via Telegram",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/water-billing-bot",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Office/Business :: Financial",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "Natural Language :: English",
    ],
    python_requires=">=3.12",
    install_requires=[
        "boto3>=1.26.0",
        "botocore>=1.29.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "isort>=5.0.0",
            "mypy>=0.950",
            "bandit>=1.7.0",
            "pylint>=2.0.0",
        ],
    },
    entry_points={},
    keywords="aws lambda telegram notifications automation water billing",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/water-billing-bot/issues",
        "Documentation": "https://github.com/yourusername/water-billing-bot#readme",
        "Source Code": "https://github.com/yourusername/water-billing-bot",
    },
)
