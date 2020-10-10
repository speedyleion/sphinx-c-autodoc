"""
Provide apidoc like functionality for C projects.

"""
import argparse
import os

from pathlib import Path
from typing import Sequence, Optional

from sphinx.util.template import ReSTRenderer


def get_parser() -> argparse.ArgumentParser:
    """
    Gets the argument parser for this module

    Returns:
        argparse.ArgumentParser: Argument parser to be used with this module.

    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o",
        "--output-path",
        help="Directory to place the output files. If it does not exist, it is "
        "created",
    )
    parser.add_argument(
        "-f",
        "--force",
        help="Force overwriting of any existing generated files",
        action="store_true",
    )
    parser.add_argument("source_path", help="Path to C source files to be documented")
    parser.add_argument(
        "-t", "--templatedir", help="Template directory for template files"
    )
    parser.add_argument(
        "--tocfile",
        help="Filename for the root table of contents file (default: %(default)s)",
        default="files",
    )
    parser.add_argument(
        "-d",
        dest="maxdepth",
        help="Maximum depth for the generated table of contents file(s). "
        "(default: %(default)s)",
        default=4,
        type=int,
    )
    parser.add_argument(
        "--header-ext",
        help='The extension(s) to use for header files (default: ["h"])',
        action="append",
    )
    parser.add_argument(
        "--source-ext",
        help='The extension(s) to use for source files (default: ["c"])',
        action="append",
    )
    return parser


def render_doc_file(
    source_file: Path, doc_file: Path, template_name: str, user_template_dir: str
) -> None:
    """
    Renders a documentation file, `doc_file`, for the provided `source_file`.

    Args:
        source_file: The source file to be documented.
        doc_file: The resultant documentation file that will document `source_file`.
        template_name: The name of the template to use to populate `doc_file` with.
        user_template_dir: A directory to contain possible user overrides of
            `template_name`.
    """
    doc_file.parent.mkdir(parents=True, exist_ok=True)
    context = {"filepath": "/".join(source_file.parts), "filename": source_file.name}
    template_dir = os.path.dirname(__file__) + "/templates"
    text = ReSTRenderer([user_template_dir, template_dir]).render(
        template_name, context
    )
    doc_file.write_text(text)


def build_directory_docs(
    source_path: Path, output_path: Path, toc_name: str, args: argparse.Namespace
) -> str:
    """
    Recursively build the documentation for the `source_path`.   Each file to be
    documented will be added to the table of contents in `toc_name`. Any sub
    directories which contain documented files will also be added to `toc_name`.

    Args:
        source_path: The path to the source directory to make documentation for.
        output_path: The destination path for the generated documentation files.
        toc_name: The name of this directories toc(table of contents) or index file.
        args: Arguments used for generating the documentation file.

    Returns:
        str: The reference to `toc_name` that can be used by parent documentation
            directories.

    """
    doc_names = []
    for entry in os.scandir(source_path):
        path = Path(entry)
        if entry.is_dir():
            name = path.name
            dir_doc = build_directory_docs(path, output_path / name, name, args)
            if dir_doc:
                doc_names.append(dir_doc)
        if entry.is_file():
            file_doc = create_file_documentation(path, output_path, args)
            if file_doc:
                doc_names.append(file_doc)

    if doc_names:
        return render_directory_index_file(output_path, toc_name, doc_names, args)
    return ""


def create_file_documentation(
    source_file: Path, output_path: Path, args: argparse.Namespace
) -> str:
    """
    Attempts to create the file documentation for `source_file`.
    Args:
        source_file: The file to create documentation for.
        output_path: The directory to place the generated file documentation.
        args: Arguments used for generating the documentation file.

    Returns:
        str: The short name of the documentation file can be placed in a sibling
            index file. Empty if this file shouldn't be documented.
    """
    name = source_file.name
    normalized_name = name.replace(".", "_")
    doc_name = f"{normalized_name}.rst"
    doc_file = output_path / doc_name
    if not args.force and doc_file.exists():
        return normalized_name

    template = None

    if name.endswith(args.header_ext):
        template = "header.rst.jinja2"
    elif name.endswith(args.source_ext):
        template = "source.rst.jinja2"

    if not template:
        return ""

    relative_path = source_file.relative_to(args.source_path)
    render_doc_file(relative_path, doc_file, template, args.templatedir)
    return normalized_name


def render_directory_index_file(
    output_path: Path, index_name: str, doc_names: Sequence, args: argparse.Namespace
) -> str:
    """
    Renders the template for the directory index file.

    Args:
        output_path: The location to render the directory index file in.
        index_name: The name of the directory index file
        doc_names: The list of files to provide in the director index file.
        args: Arguments used for generating the index file.

    Returns:
        str: The name of the index file to be placed in parent index files.

    """
    index_file = output_path / f"{index_name}.rst"
    context = {
        "doc_names": doc_names,
        "maxdepth": args.maxdepth,
        "title": index_name,
    }
    template_dir = os.path.dirname(__file__) + "/templates"
    text = ReSTRenderer([args.templatedir, template_dir]).render(
        "toc.rst.jinja2", context
    )
    index_file.write_text(text)
    return f"{output_path.name}/{index_name}"


def main(argv: Optional[Sequence] = None) -> int:
    """
    The main entry point for this module.  Will parse the provided arguments(`argv`)
    and generated the documentation files.
    Args:
        argv: The arguments to use for documentation generation.  Use `--help` to see
            the full documentation.  If no arguments provided then sys.argv will be
            used.

    Returns:
        int: 0 if success.  Other than 0 on failure.

    """
    parser = get_parser()
    args = parser.parse_args(argv)

    output_path = Path(args.output_path)
    source_path = Path(args.source_path)

    if not args.header_ext:
        args.header_ext = ["h"]
    args.header_ext = tuple(f".{ext}" for ext in args.header_ext)

    if not args.source_ext:
        args.source_ext = ["c"]
    args.source_ext = tuple(f".{ext}" for ext in args.source_ext)

    build_directory_docs(source_path, output_path, args.tocfile, args)
    return 0


if __name__ == "__main__":
    main()
