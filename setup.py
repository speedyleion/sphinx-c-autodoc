import pathlib
import setuptools

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.rst").read_text()

# Sanitize unknown directives from pyi
README = README.replace(".. c:function::", ".. code-block:: rst\n\n    .. c:function::")

setuptools.setup(
    name="sphinx-c-autodoc",
    version="0.3.0",
    description="A sphinx autodoc extension for c modules",
    long_description=README,
    long_description_content_type="text/x-rst",
    url="https://sphinx-c-autodoc.readthedocs.io/en/latest/",
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
    package_data={"": ["templates/*.jinja2"]},
    install_requires=[
        "sphinx>=3",
        "clang>=6",
        "beautifulsoup4",
    ],
    entry_points={
        "console_scripts": [
            "sphinx-c-apidoc = sphinx_c_autodoc.apidoc:main",
        ]
    },
    python_requires=">=3.7",
)
