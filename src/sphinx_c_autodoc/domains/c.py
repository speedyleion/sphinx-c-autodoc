"""
Patches to extend the C domain that comes with sphinx.

In particular:

* Allow for nesting of type/structure defines. The current c domain doesn't
  handle nested structures correctly.
* Add a `module` option to most C directives. This allows for proper cross
  referencing with viewcode.

"""
from sphinx.domains.c import CObject, ASTDeclaration
from sphinx.addnodes import desc_signature
from sphinx.ext.autodoc import identity, bool_option


def patch_c_domain() -> None:
    """
    Patch the built in C domain of sphinx.
    """
    # Allows for determining what files directives are for.
    # also enables the noindex logic
    CObject.option_spec.update({"module": identity, "noindex": bool_option})

    original_handle_signature = CObject.handle_signature

    def _new_handle_signature(
        self: CObject, sig: str, signode: desc_signature
    ) -> ASTDeclaration:
        """
        Decorates the `signode` node with the module and fullname of the item
        that created the node.  Similar to the python domain's version.
        """
        ast = original_handle_signature(self, sig, signode)

        signode["module"] = self.options.get("module")
        last_symbol = self.env.temp_data["c:last_symbol"]
        signode["fullname"] = str(last_symbol.get_full_nested_name())

        return ast

    CObject.handle_signature = _new_handle_signature  # type: ignore
