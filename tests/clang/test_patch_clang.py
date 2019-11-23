"""
Focus on testing the patching of clang
"""
from c_docs.parser import patch_cindex
from clang import cindex

def test_re_patch():
    """
    Tests that re-patching doesn't cause issues.

    The first patching happens by import, this second patching ensures that this
    doesn't add another entry for the package functions into the clang function
    list.
    """
    patch_cindex()

    functions = tuple(f[0] for f in cindex.functionList)
    assert len(functions) == len(set(functions))


