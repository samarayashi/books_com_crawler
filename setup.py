from setuptools import setup, find_packages

setup(
    name="books_crawler",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "beautifulsoup4>=4.9.3",
        "requests>=2.25.1",
        "fake-useragent>=0.1.11",
        "pyyaml>=5.4.1",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="博客來書籍資訊爬蟲",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/books_crawler",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
) 