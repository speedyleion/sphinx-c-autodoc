==========================
Minimum Supported Versions
==========================

Keeping with the industry support of Python versions
https://www.python.org/downloads/, this package will try to support the
currently supported Python versions. The minimum supported dependency versions
will be the newest version of the dependency that was available when the minimum
supported Python version was released.

Dropping support for a dependency version is not considered a major change and
will only result in a minor version bump.

Planned support calendar. The end dates aren't December 31st, they're the
October end of life dates for the associated Python version.

+------+------+------+------+------+------+------+------+------+
| 2022 | 2023 | 2024 | 2025 | 2026 | 2027 | 2028 | 2029 | 2030 |
+======+======+======+======+======+======+======+======+======+
|       Python 3.10                | xxxx | xxxx | xxxx | xxxx |
+----------------------------------+------+------+------+------+
|             Python 3.11                 | xxxx | xxxx | xxxx |
+------+----------------------------------+------+------+------+
| xxxx |      Python 3.12                        | xxxx | xxxx |
+------+------+----------------------------------+------+------+
| xxxx | xxxx |      Python 3.13                               |
+------+------+------+-----------------------------------------+
| xxxx | xxxx | xxxx |      Python 3.14                        |
+------+------+------+-------------+------+------+------+------+
|       Sphinx 4.x                 | xxxx | xxxx | xxxx | xxxx |
+----------------------------------+------+------+------+------+
|                Sphinx 5.x               | xxxx | xxxx | xxxx |
+-----------------------------------------+------+------+------+
|                Sphinx 6.x               | xxxx | xxxx | xxxx |
+------+----------------------------------+------+------+------+
| xxxx |             Sphinx 7.x                  | xxxx | xxxx |
+------+------+----------------------------------+------+------+
| xxxx | xxxx |             Sphinx 8.x                         |
+------+------+--------------------+------+------+------+------+
|             Clang 12.x           | xxxx | xxxx | xxxx | xxxx |
+----------------------------------+------+------+------+------+
|             Clang 13.x           | xxxx | xxxx | xxxx | xxxx |
+----------------------------------+------+------+------+------+
|                Clang 14.x               | xxxx | xxxx | xxxx |
+------+----------------------------------+------+------+------+
| xxxx |            Clang 15.x            | xxxx | xxxx | xxxx |
+------+----------------------------------+------+------+------+
| xxxx |            Clang 16.x                   | xxxx | xxxx |
+------+------+----------------------------------+------+------+
| xxxx | xxxx |      Clang 17.x                  | xxxx | xxxx |
+------+------+----------------------------------+------+------+
| xxxx | xxxx | xxxx |      Clang 18.x           | xxxx | xxxx |
+------+------+------+---------------------------+------+------+
| xxxx | xxxx | xxxx |      Clang 19.x           | xxxx | xxxx |
+------+------+------+---------------------------+------+------+
| xxxx | xxxx | xxxx |      Clang 20.x                         |
+------+------+------+-----------------------------------------+
|                    Beautiful Soup 4                          |
+--------------------------------------------------------------+

.. note:: The different Clang versions are *not* exercised in CI. Most of the
   Python API for Clang seems pretty stable and as long as the most recent
   version of Clang keeps working it's hoped that it will catch most issues.
