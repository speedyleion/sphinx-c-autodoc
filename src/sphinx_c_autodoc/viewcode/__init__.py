"""
Handles viewcode for c.

The processing idea:

1. Walk through every node in the document finding out if it is a C
   construct. Then find out which file, if any it is associated with:

   a. Create a pending cross refernce to the file.

   b. Add the file to the environment list of files to create source listings
      of, :attr:`app.env._viewcode_c_modules`

2. Walk through all of the files in the environment list,
   :attr:`app.env._viewcode_c_modules` and create a source listing for each
   one.

3. Process the pending cross references and link them up to the source
   listings.

.. note:: The environment attribute is namespaced with `c` to prevent
    populating the `viewcode`_ extension's variable for multi-language
    documentation purposes.

.. _viewcode: https://www.sphinx-doc.org/en/master/usage/extensions/viewcode.html

"""
from dataclasses import dataclass
from typing import Any, Dict, Iterator, Tuple, List, Optional

from docutils import nodes
from docutils.nodes import Node, Element

from sphinx import addnodes
from sphinx.application import Sphinx
from sphinx.environment import BuildEnvironment
from sphinx.util import logging, status_iterator
from sphinx.util.nodes import make_refnode

from sphinx_c_autodoc import ViewCodeListing

MODULES_DIRECTORY = "_modules"

# To work with the c domain from sphinx all C constructs will have this prefix.
C_DOMAIN_LINK_PREFIX = "c."

logger = logging.getLogger(__name__)


@dataclass
class DocumentationReference:
    """
    Representation of the documentation of a C construct.

    Attributes:
        docname (str):
            The document which contains the documentation of the C construct.

        module (str):
            The c module, this is relative to a path in  LINK_TO_SOURCE_ROOTS

        fullname (str):
            The name of the construct, i.e. function name, variable name etc.

    """

    docname: str
    module: str
    fullname: str


def missing_reference(
    app: Sphinx, env: BuildEnvironment, node: Element, contnode: Node
) -> Optional[Node]:
    """
    Adds a reference node to and c viewcode links which haven't been resolved
    yet.

    If the location to cross reference does not exist this will return an
    empty node.

    Args:
        app (Sphinx):
            The currently running sphinx application.

        env (BuildEnvironment):
            The current build environment.

        node (Element):
            The node which is a pending cross reference.

        contnode (Node):
            The _contents_ node of the created cross reference

    Returns:
        The cross refernce node to use.

    """
    # pylint: disable=unused-argument
    if node["reftype"] == f"{C_DOMAIN_LINK_PREFIX}viewcode":
        assert app.builder is not None
        # We have to wait until here to see if the module actually exists as a
        # plain c directive could be reference a module before the auto c
        # directives are encountered.
        modules = getattr(app.builder.env, "_viewcode_c_modules", {})
        module = modules.get(node["module"])
        if module is None:
            return nodes.inline()

        construct = _find_construct(node["fullname"], module.ast)
        if construct is None:
            return nodes.inline()

        return make_refnode(
            app.builder, node["refdoc"], node["reftarget"], node["refid"], contnode
        )
    return None


def add_source_listings(app: Sphinx) -> Iterator[Tuple[str, Dict[str, Any], str]]:
    """
    The idea is to create a code listing of each source file that has a
    pending cross reference to.

    The pending source files to create listings for are stored in
    :attr:`app.env._viewcode_c_modules`.

    Meant to be connected to the `html-collect-pages` event,
    https://www.sphinx-doc.org/en/master/extdev/appapi.html#event-html-collect-pages

    Args:
        app: The current sphinx app being run.

    Yields:
        Tuple[str, Dict[str, Any], str]: The name of the page, the contents
        of the page, the name of the template to use for generating the final
        page.
    """
    assert app.builder is not None
    modules_to_list = getattr(app.builder.env, "_viewcode_c_modules", {})

    iterator = status_iterator(
        sorted(modules_to_list.items()),
        "highlighting c module code... ",
        "blue",
        len(modules_to_list),
        app.verbosity,
        lambda x: x[0],
    )

    for module, code_listing in iterator:
        highlighted_source = _get_highlighted_source(app, code_listing.raw_listing)
        _insert_line_anchors(app, highlighted_source, code_listing)

        context = {
            "title": module,
            "body": (
                f"<h1>Source code for {module}</h1>" + "\n".join(highlighted_source)
            ),
        }
        yield (_get_source_page_name(module), context, "page.html")


def _get_source_page_name(module: str) -> str:
    """
    Get the page name of the resultant source listing.

    Args:
        module (str): The module of the source listing.

    Returns:
        str: The page name of the resultant source listing.
    """
    return f"{MODULES_DIRECTORY}/{module}"


def _insert_documentation_backlinks(
    app: Sphinx, highlighted_code: List[str], code_listing: ViewCodeListing
) -> None:
    """
    Insert links from `highlighted_code` to the places that documented
    `highlighted_code`.

    Args:
        app (Sphinx):
            The currently running sphinx application.

        highlighted_code (List[str]):
            The source listing to create links from.  This will be modified in place.

        code_listing (ViewCodeListing):
            Contains the documentation locations which documented `highlighted_code`.
    """
    assert app.builder is not None
    for doc in code_listing.doc_links.values():
        construct = _find_construct(doc.fullname, code_listing.ast)

        # Can happen when documenting a non existent C construct.
        # TODO consider if this should be a warning.
        if construct is None:
            continue

        link_line = construct["start_line"]
        page_name = _get_source_page_name(doc.module)
        relative_link = app.builder.get_relative_uri(page_name, doc.docname)
        link_text = f"{relative_link}#{C_DOMAIN_LINK_PREFIX}{doc.fullname}"
        highlighted_code[link_line] = (
            f'<a class="viewcode-back" href="{link_text}">[docs]</a>'
            + highlighted_code[link_line]
        )


def _find_construct(fullname: str, ast: Dict) -> Optional[Dict]:
    """
    Find a C construct inside of the provided `ast`.

    Args:
        fullname (str): The full, dotted name, to the C construct.

        ast (dict):
            A dictionary like representation of the code constructs.
            See :ref:`developer_notes:Common Terms`.

    Returns:
        Dict: The C construct if it is found in the `ast`.  None otherwise.

    """
    parts = fullname.split(".", 1)
    parent = parts[0]
    child = {}
    for child in ast["children"]:
        if child["name"] == parent:
            break
    else:
        return None

    if len(parts) > 1:
        child_path = parts[1]
        return _find_construct(child_path, child)

    return child


def _insert_line_anchors(
    app: Sphinx, highlighted_source: List[str], code_listing: ViewCodeListing
) -> None:
    """
    Insert line anchors into `highlighted_source` which can be pointed to
    from other locations in the documentation.

    Also adds in links back to the documentation locations.

    Args:
        app (Sphinx):
            The sphinx app currently doing the processing.
        highlighted_source (List[str]):
            The source to populate with anchors. This should already
            highlighted in html format.
        code_listing (ViewCodeListing):
            The code listing to retrieve anchors from.
    """
    _insert_documentation_backlinks(app, highlighted_source, code_listing)

    # The root file needs no anchor so only document it's children
    for child in code_listing.ast["children"]:
        _insert_construct_anchor(app, highlighted_source, child)


def _insert_construct_anchor(
    app: Sphinx,
    highlighted_source: List[str],
    construct: Dict,
    prefix: Optional[str] = None,
) -> None:
    """
    Recursivley insert an anchor for a c construct and anchors for all of
    it's children.

    Args:
        app (Sphinx):
            The sphinx app currently doing the processing.
        highlighted_source (List[str]):
            The source to populate with anchors. This should already
            highlighted in html format.
        construct (Dict):
            The construct to create an anchor for.
            See :ref:`c_construct`
        prefix (Optional[str]):
            The prefix representing the dotted path of the current
    """
    start = construct["start_line"]
    end = construct["end_line"]
    name = construct["name"]
    if prefix:
        prefix = ".".join((prefix, name))
    else:
        prefix = name
    highlighted_source[start] = (
        f'<div class="viewcode-block" id="{C_DOMAIN_LINK_PREFIX}{prefix}">'
        + highlighted_source[start]
    )
    highlighted_source[end] += "</div>"
    for child in construct.get("children", []):
        _insert_construct_anchor(app, highlighted_source, child, prefix)


def _get_highlighted_source(app: Sphinx, code: str) -> List[str]:
    """
    Turn the code into a highlighted source file.

    Args:
        app (Sphinx):
            The sphinx app currently doing the processing.
        code (str):
            The code to turn into highlighted source.

    Returns:
        List[str]: The code lines with necessary markup to be highlighted.
        The first line of the `code` will be in index ``1`` of the list.
    """
    highlighter = app.builder.highlighter  # type: ignore
    highlighted_code = highlighter.highlight_block(code, "c", linenos=False)

    lines = highlighted_code.splitlines()
    return _align_code_lines(lines)


def _align_code_lines(highlighted_code: List[str]) -> List[str]:
    """
    Source lines are 1 based indices, while actual lists are 0 based. This
    funciton ensures that the first code line ends up at index 1 in the list
    of lines.

    For whatever reason pygments html, the actual backend formatter, places
    the termination on a separate trailing line, but doesn't put the initial
    surround on a preceding line.

    .. code_block::

          highlighted_code = ["<div><pre><span></span>{first line of file}",
                              "{second line of flie}",
                              ...

                              "{last line of flie}",
                              "</pre></div>"]

    So we'll break the first line into two so that the ``div`` and ``pre``
    tags go into index 0 and the first line ends up in index 1.

    Args:
        highlighted_code (List[str]):
            The code to align correctly for line numbers.

    Returns:
        List[str]: The code properly aligned with ``1`` based line numbering.
    """
    *leading_html, first_line = highlighted_code[0].partition("<pre>")
    highlighted_code[0:1] = ["".join(leading_html), first_line]
    return highlighted_code


def doctree_read(app: Sphinx, doctree: Node) -> None:
    """
    Go through the entire document looking for C signature nodes to create
    cross references to the actual source listings.

    Args:
        app (Sphinx):
            The sphinx app currently doing the processing.

        doctree (Node):
            The root node of the document to walk through. This will be
            modified in place, by modifiying signature nodes of C constructs.
    """
    c_nodes = (n for n in doctree.traverse(addnodes.desc) if n.get("domain") == "c")
    for node in c_nodes:
        signature_nodes = (n for n in node if isinstance(n, addnodes.desc_signature))

        # I really dislike negative flags. Anyway it's ok to link to source
        # listing from anywhere, but it's undesirable to link from the source
        # listing back to any documentation location. So we leverage the
        # :noindex: option and assume that only the entries which allowed the
        # indices are the consolidated locations of documentation.
        use_back_refs = not node.get("noindex", False)

        for signature in signature_nodes:
            fullname = signature.get("fullname")
            if use_back_refs:
                _add_pending_back_reference(app, signature, fullname)
            _add_pending_source_cross_reference(app, signature, fullname)


def _add_pending_source_cross_reference(
    app: Sphinx, signode: addnodes.desc, fullname: str
) -> None:
    """
    Adds a pending source cross reference to the signature in the doctree, `signode`.

    The viewcode and linkcode extensions walk the doctree once parsed and
    then add this node, however since sphinx_c_autodoc already has to add
    logic, the `module` option to the directives it seems more practical to
    just create the full pending cross reference here, and then viewcode is
    an extension which will populate this cross refernce.

    Args:
        app (Sphinx):
            The sphinx app currently doing the processing.
        signode (Node):
            The signature node to apply the source code cross reference to.
        fullname (str):
            The dotted fullname of the C construct.
    """
    module = signode.get("module")
    if module is None:
        return

    assert app.builder is not None
    assert app.builder.env is not None

    source_page = _get_source_page_name(module)

    # Using the `viewcode-link` to be consistent with the python versions in
    # case someone else wants to walk the tree and do other links
    inline = nodes.inline("", "[source]", classes=["viewcode-link"])

    # Limit this cross referencing only to html
    html_node = addnodes.only(expr="html")
    html_node += addnodes.pending_xref(
        "",
        inline,
        reftype=f"{C_DOMAIN_LINK_PREFIX}viewcode",
        refdomain="std",
        refexplicit=False,
        reftarget=source_page,
        refid=f"{C_DOMAIN_LINK_PREFIX}{fullname}",
        refdoc=app.builder.env.docname,
        module=module,
        fullname=fullname,
    )

    signode += html_node


def _add_pending_back_reference(
    app: Sphinx, signode: addnodes.desc, fullname: str
) -> None:
    """
    Updates the ``doc_links`` entry of the modules stored in
    ``_viewcode_c_modules`` so that they can later be added to the source
    code listings as links to the documentation locations.

    Args:
        app (Sphinx):
            The sphinx app currently doing the processing.
        signode (Node):
            The signature node to create the back reference to.
        fullname (str):
            The name of the construct, i.e. function name, variable name etc.
    """
    module = signode.get("module")
    if module is None:
        return

    assert app.builder is not None
    assert app.builder.env is not None

    env = app.builder.env
    code_listing = env._viewcode_c_modules.get(module)  # type: ignore
    if code_listing is None:
        return

    doc_links = code_listing.doc_links
    doc_links.setdefault(
        fullname, DocumentationReference(env.docname, module, fullname)
    )


def setup(app: Sphinx) -> None:
    """
    Setup function for registering this with sphinx

    Args:
        app (Sphinx):
            The application for the current run of sphinx.
    """
    app.connect("doctree-read", doctree_read)
    app.connect("missing-reference", missing_reference)
    app.connect("html-collect-pages", add_source_listings)
