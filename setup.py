import setuptools

setuptools.setup(
    name="sphinx-c-autodoc",
    version="0.1.0",
    description="A sphinx autodoc extension for c modules",
    url="https://github.com/speedyleion/sphinx-c-autodoc",
    package_dir={"":"src"},
    packages=setuptools.find_packages("src"),
    license="Unlicense",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    project_urls={
        "Source": "https://github.com/speedyleion/sphinx-c-autodoc",
    },
    install_requires=[
        "sphinx>=2",
        "clang>=6",
        "beautifulsoup4",
    ],
    python_requires=">=3.7",
)