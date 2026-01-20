from setuptools import setup, find_packages

setup(
    name="cli-mate",
    version="1.0.0",
    description="AI-Powered Error Analysis CLI Tool",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "click>=8.1.7",
    ],
    entry_points={
        "console_scripts": [
            "wtf=wtf.main:cli",
        ],
    },
    python_requires=">=3.10",
)
