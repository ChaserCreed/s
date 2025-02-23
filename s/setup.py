from setuptools import setup, find_packages

# Read the README file for a long description.
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="s",  # This is the package name on PyPI.
    version="0.1.0",
    author="Chase Reed",
    author_email="chasereed00000@gmail.com",
    description="A powerful Python package to make Selenium simpler, using advanced Selenium automation with anti-detection features and beginner-friendly functions.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chasercreed/s",  # Update with your repository URL.
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Update if you choose a different license.
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "selenium",
        "webdriver_manager",
        "fake_useragent",
        "stem",
        "requests"
    ],
)
