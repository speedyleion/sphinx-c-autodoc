==========================
Minimum Supported Versions
==========================

Keeping with the industry support of Python versions
https://www.python.org/downloads/, this package will try to support the
currently supported Python versions. The minimum supported dependency versions
will be the newest version of the dependency that was available when the minimum
supported Python version was released.

Dropping support for a dependency version is considered a major change and will
result in a major version bump.

Planned support calendar. The end dates aren't December 31st, they're the
October end of life dates for the associated Python version.

+------+------+------+------+------+------+------+------+
| 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 | 2027 |
+======+======+======+======+======+======+======+======+
|          Python 3.8              | xxxx | xxxx | xxxx |
+----------------------------------+------+------+------+
|                Python 3.9               | xxxx | xxxx |
+------+----------------------------------+------+------+
| xxxx |              Python 3.10                | xxxx |
+------+------+----------------------------------+------+
| xxxx | xxxx |             Python 3.11                 |
+------+------+--------------------+------+------+------+
|          Sphinx 3.1              | xxxx | xxxx | xxxx |
+------+------+--------------------+------+------+------+
| xxxx |              Sphinx 4.x                 | xxxx |
+------+------+------+---------------------------+------+
| xxxx | xxxx |                Sphinx 5.x               |
+------+------+------+----------------------------------+
| xxxx | xxxx |                Sphinx 6.x               |
+------+------+------+----------------------------------+
| xxxx | xxxx | xxxx |             Sphinx 7.x           |
+------+------+------+-------------+------+------+------+
|             Clang 6.x            | xxxx | xxxx | xxxx |
+----------------------------------+------+------+------+
|             Clang 7.x            | xxxx | xxxx | xxxx |
+----------------------------------+------+------+------+
|             Clang 8.x            | xxxx | xxxx | xxxx |
+----------------------------------+------+------+------+
|             Clang 9.x            | xxxx | xxxx | xxxx |
+----------------------------------+------+------+------+
|             Clang 10.x           | xxxx | xxxx | xxxx |
+----------------------------------+------+------+------+
|                  Clang 11.x             | xxxx | xxxx |
+------+------+---------------------------+------+------+
| xxxx | xxxx |             Clang 12.x           | xxxx |
+------+------+----------------------------------+------+
| xxxx | xxxx |             Clang 13.x           | xxxx |
+------+------+----------------------------------+------+
| xxxx | xxxx |                Clang 14.x               |
+------+------+------+----------------------------------+
| xxxx | xxxx | xxxx |            Clang 15.x            |
+------+------+------+----------------------------------+
| xxxx | xxxx | xxxx |            Clang 16.x            |
+------+------+------+----------------------------------+
|                   Beautiful Soup 4                    |
+-------------------------------------------------------+

.. note:: The different Clang versions are *not* exercised in CI. Most of the
   Python API for Clang seems pretty stable and as long as the most recent
   version of Clang keeps working it's hoped that it will catch most issues.
