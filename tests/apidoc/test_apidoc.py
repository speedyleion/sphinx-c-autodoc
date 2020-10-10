"""
Test the behaviour of apidoc generation
"""

import os
import pytest

from itertools import product, zip_longest
from textwrap import dedent
from sphinx_c_autodoc.apidoc import main

DIRECTORIES = ("sub_dir_1", "sub_dir_2", "nested/directory")
IMPLEMENTATION_FILES = (
    "header_1.h",
    "header_2.h",
    "c_file_1.c",
    "c_file_2.c",
    "readme.md",
    "foo.txt",
)
PROJECT_FILES = IMPLEMENTATION_FILES + tuple(
    ("/".join((d, f)) for (d, f) in product(DIRECTORIES, IMPLEMENTATION_FILES) if d)
)


def test_create_all_files_in_a_project(tmp_path):
    source_dir = tmp_path / "project"
    source_files = [source_dir / n for n in PROJECT_FILES]
    for s in source_files:
        s.parent.mkdir(parents=True, exist_ok=True)
        s.write_text("")

    # Some directories that only contain files that won't be documented
    non_doc = source_dir / "undocumneted" / "some_file.txt"
    non_doc.parent.mkdir(parents=True, exist_ok=True)
    non_doc.write_text("")

    out_dir = tmp_path / "output"

    main(["-o", str(out_dir), str(source_dir)])

    names = [
        f.replace(".", "_") + ".rst" for f in PROJECT_FILES if f.endswith((".h", ".c"))
    ]

    doc_files = [out_dir / n for n in names]

    toc_files = [out_dir / d / f"{d.split('/')[-1]}.rst" for d in DIRECTORIES] + [
        out_dir / "files.rst",
        out_dir / "nested/nested.rst",
    ]
    doc_files += toc_files
    for f in doc_files:
        assert f.exists()

    total_file_count = sum((len(files) for _, _, files in os.walk(str(out_dir))))
    assert total_file_count == len(doc_files)


@pytest.mark.parametrize("filename", ("my_source.c", "another_source.c"))
def test_source_file_template_used(filename, tmp_path):
    source_dir = tmp_path / "project"
    source_file = source_dir / filename
    source_file.parent.mkdir(parents=True, exist_ok=True)
    source_file.write_text("")
    out_dir = tmp_path / "output"

    main(["-o", str(out_dir), str(source_dir)])

    out_file = out_dir / (filename.replace(".", "_") + ".rst")

    relative_source = source_file.relative_to(source_dir)
    section_under = "=" * len(filename)
    source_doc_contents = f"""\
        {filename}
        {section_under}

        .. autocmodule:: {relative_source}"""
    assert out_file.read_text() == dedent(source_doc_contents)


@pytest.mark.parametrize("filename", ("a_header.h", "a_different_header.h"))
def test_header_file_template_used(filename, tmp_path):
    source_dir = tmp_path / "project"
    header_file = source_dir / filename
    header_file.parent.mkdir(parents=True, exist_ok=True)
    header_file.write_text("")
    out_dir = tmp_path / "output"

    main(["-o", str(out_dir), str(source_dir)])

    out_file = out_dir / (filename.replace(".", "_") + ".rst")

    relative_header = header_file.relative_to(source_dir)
    section_under = "=" * len(filename)
    header_doc_contents = f"""\
        {filename}
        {section_under}

        .. autocmodule:: {relative_header}
            :members:"""
    assert out_file.read_text() == dedent(header_doc_contents)


def test_no_forced_overwrite(tmp_path):
    source_dir = tmp_path / "project"
    source_file = source_dir / "pre_existing.c"
    source_file.parent.mkdir(parents=True, exist_ok=True)
    source_file.write_text("")
    out_dir = tmp_path / "output"
    out_file = out_dir / "pre_existing_c.rst"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    pre_existing_text = "shouldn't be overwritten"
    out_file.write_text(pre_existing_text)

    main(["-o", str(out_dir), str(source_dir)])

    assert out_file.read_text() == pre_existing_text


def test_forced_overwrite(tmp_path):
    source_dir = tmp_path / "project"
    source_file = source_dir / "pre_existing.c"
    source_file.parent.mkdir(parents=True, exist_ok=True)
    source_file.write_text("")
    out_dir = tmp_path / "output"
    out_file = out_dir / "pre_existing_c.rst"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    pre_existing_text = "should be overwritten"
    out_file.write_text(pre_existing_text)

    main(["-o", str(out_dir), str(source_dir), "-f"])

    doc_contents = f"""\
        pre_existing.c
        ==============

        .. autocmodule:: pre_existing.c"""

    assert out_file.read_text() == dedent(doc_contents)


@pytest.mark.parametrize(
    "filename, template_name, template_contents",
    [
        ("user_template.c", "source.rst.jinja2", "{{filename}} in a user template"),
        ("another_template.h", "header.rst.jinja2", "{{filename}} in a user template"),
    ],
)
def test_user_template(filename, template_name, template_contents, tmp_path):
    source_dir = tmp_path / "project"
    source_file = source_dir / filename
    source_file.parent.mkdir(parents=True, exist_ok=True)
    source_file.write_text("")
    out_dir = tmp_path / "output"

    template_dir = tmp_path / "user_templates"
    template = template_dir / template_name
    template.parent.mkdir(parents=True, exist_ok=True)
    template.write_text(template_contents)

    main(["-o", str(out_dir), str(source_dir), "-t", str(template_dir)])

    out_file = out_dir / (filename.replace(".", "_") + ".rst")
    assert out_file.read_text() == template_contents.format().format(filename=filename)


@pytest.mark.parametrize(
    "files", (["a_header.h", "a_source.c"], ["a_file.h", "a_file.c"])
)
def test_toc_template_used(files, tmp_path):
    source_dir = tmp_path / "project"
    for filename in files:
        file_ = source_dir / filename
        file_.parent.mkdir(parents=True, exist_ok=True)
        file_.write_text("")

    out_dir = tmp_path / "output"

    main(["-o", str(out_dir), str(source_dir)])

    out_file = out_dir / "files.rst"

    filenames = [f.replace(".", "_") for f in files]
    toc_doc_contents = f"""\
        files
        =====

        .. toctree::
            :maxdepth: 4

            {filenames[0]}
            {filenames[1]}"""

    # The order of the files depends on the directory search order which is
    # platform dependent.  Though less than ideal we compare the lines of the content
    expected_lines = sorted(dedent(toc_doc_contents).splitlines())
    actual_lines = sorted(out_file.read_text().splitlines())
    assert actual_lines == expected_lines


@pytest.mark.parametrize("tocname", ("what", "ok"))
def test_toc_name(tocname, tmp_path):
    source_dir = tmp_path / "project"
    source_file = source_dir / "intermediate" / "test.c"
    source_file.parent.mkdir(parents=True, exist_ok=True)
    source_file.write_text("")
    out_dir = tmp_path / "output"

    main(["-o", str(out_dir), str(source_dir), f"--tocfile={tocname}"])

    out_file = out_dir / f"{tocname}.rst"
    section_under = "=" * len(tocname)

    toc_doc_contents = f"""\
        {tocname}
        {section_under}
        
        .. toctree::
            :maxdepth: 4

            intermediate/intermediate"""

    assert out_file.read_text() == dedent(toc_doc_contents)

    # The sub toc files should not get renamed and should always be named after the directory
    out_file = out_dir / "intermediate" / "intermediate.rst"

    toc_doc_contents = f"""\
        intermediate
        ============

        .. toctree::
            :maxdepth: 4

            test_c"""

    assert out_file.read_text() == dedent(toc_doc_contents)


@pytest.mark.parametrize("toc_depth", ("2", "6"))
def test_toc_depth(toc_depth, tmp_path):
    source_dir = tmp_path / "project"
    source_file = source_dir / "test.c"
    source_file.parent.mkdir(parents=True, exist_ok=True)
    source_file.write_text("")
    out_dir = tmp_path / "output"

    main(["-o", str(out_dir), str(source_dir), f"-d={toc_depth}"])

    out_file = out_dir / "files.rst"

    toc_doc_contents = f"""\
        files
        =====

        .. toctree::
            :maxdepth: {toc_depth}

            test_c"""

    assert out_file.read_text() == dedent(toc_doc_contents)


@pytest.mark.parametrize("extensions", (["sem", "xor"], ["fox", "bear"]))
def test_header_extension_flag(extensions, tmp_path):
    source_dir = tmp_path / "project"
    header_files = [
        f"{name}.{ext}"
        for name, ext in zip_longest(
            ("header_1", "header_2", "header_3"), extensions, fillvalue="h"
        )
    ]
    for name in header_files:
        header = source_dir / name
        header.parent.mkdir(parents=True, exist_ok=True)
        header.write_text("")

    out_dir = tmp_path / "output"

    header_flags = [f"--header-ext={ext}" for ext in extensions]
    main(["-o", str(out_dir), str(source_dir)] + header_flags)

    for filename in header_files:
        output = out_dir / (filename.replace(".", "_") + ".rst")
        if filename.endswith(".h"):
            assert not output.exists()
            continue

        section_under = "=" * len(filename)
        header_doc_contents = f"""\
            {filename}
            {section_under}

            .. autocmodule:: {filename}
                :members:"""
        assert output.read_text() == dedent(header_doc_contents)


@pytest.mark.parametrize("extensions", (["sem", "xor"], ["fox", "bear"]))
def test_source_extension_flag(extensions, tmp_path):
    source_dir = tmp_path / "project"
    source_files = [
        f"{name}.{ext}"
        for name, ext in zip_longest(
            ("source_1", "source_2", "source_3"), extensions, fillvalue="c"
        )
    ]
    for name in source_files:
        source = source_dir / name
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("")

    out_dir = tmp_path / "output"

    source_flags = [f"--source-ext={ext}" for ext in extensions]
    main(["-o", str(out_dir), str(source_dir)] + source_flags)

    for filename in source_files:
        output = out_dir / (filename.replace(".", "_") + ".rst")
        if filename.endswith(".c"):
            assert not output.exists()
            continue

        section_under = "=" * len(filename)
        source_doc_contents = f"""\
            {filename}
            {section_under}

            .. autocmodule:: {filename}"""
        assert output.read_text() == dedent(source_doc_contents)


def test_full_relative_path_to_files_used_in_directives(tmp_path):
    source_dir = tmp_path / "project"
    source_file = source_dir / "intermediate" / "test.c"
    source_file.parent.mkdir(parents=True, exist_ok=True)
    source_file.write_text("")
    header_file = source_dir / "a_different_dir" / "foo.h"
    header_file.parent.mkdir(parents=True, exist_ok=True)
    header_file.write_text("")
    out_dir = tmp_path / "output"

    main(["-o", str(out_dir), str(source_dir)])

    source_doc_contents = f"""\
        test.c
        ======

        .. autocmodule:: intermediate/test.c"""
    source_out = out_dir / "intermediate" / "test_c.rst"
    assert source_out.read_text() == dedent(source_doc_contents)

    header_doc_contents = f"""\
        foo.h
        =====

        .. autocmodule:: a_different_dir/foo.h
            :members:"""

    header_out = out_dir / "a_different_dir" / "foo_h.rst"
    assert header_out.read_text() == dedent(header_doc_contents)
