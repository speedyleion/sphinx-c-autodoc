"""
Patches to extend the C domain that comes with sphinx.

In particular:

* Allow for nesting of type/structure defines. The current c domain doesn't
  handle nested structures correctly.
* Add a `module` option to most C directives. This allows for proper cross
  referencing with viewcode.

"""
from sphinx.domains.c import CObject
from sphinx.addnodes import desc_signature
from sphinx.ext.autodoc import identity


def patch_c_domain() -> None:
    """
    Patch the built in C domain of sphinx.
    """
    # Allows for determining what files directives are for.
    CObject.option_spec.update({"module": identity})

    original_handle_signature = CObject.handle_signature

    def _new_handle_signature(self: CObject, sig: str, signode: desc_signature) -> str:
        """
        Decorates the `signode` node with the module and fullname of the item
        that created the node.  Similar to the python domain's version.
        """
        # The logic for the c domain to build up the fullname will only look at
        # the type stack if the item is a "member". Fortunatly this appears to
        # be the only time the method looks at the :attr:`name` so we can
        # conditionally change it and then restore when done.
        self_name = self.name
        if self.name in ("c:type", "c:macro") and self.env.ref_context.get("c:type"):
            self.name = "c:member"

        fullname = original_handle_signature(self, sig, signode)

        self.name = self_name

        signode["module"] = self.options.get("module")
        signode["fullname"] = fullname
        return fullname

    CObject.handle_signature = _new_handle_signature  # type: ignore
    CObject.before_content = CObject_before_content  # type: ignore
    CObject.after_content = CObject_after_content  # type: ignore


# pylint: disable=invalid-name
def CObject_before_content(self: CObject) -> None:
    """
    The c domain provided with sphinx does not handle structs within structs.
    This makes it possible to document those by creating a stack fo the
    defined types.
    """
    if self.name == "c:type":
        type_list = self.env.ref_context.setdefault("c:types", [])
        type_list.append(self.names[0])
        self.env.ref_context["c:type"] = type_list[-1]


# pylint: disable=invalid-name
def CObject_after_content(self: CObject) -> None:
    """
    Pop off any c types that have finished being processed.
    """
    if self.name == "c:type":
        type_list = self.env.ref_context["c:types"]
        type_list.pop()
        try:
            self.env.ref_context["c:type"] = type_list[-1]
        except IndexError:
            del self.env.ref_context["c:type"]
