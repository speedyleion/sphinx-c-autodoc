==========================
Minimum Supported Versions
==========================

Keeping with the industry support of Python versions
https://www.python.org/downloads/, this package will try to support it's main
dependencies for 5 years.

Dropping support for a dependency version is considered a major change and will
result in a major version bump.

Python Version
--------------

============== ============== ==============
Python Version First Released End of Support 
============== ============== ==============
3.11           2022-10-24     2027-10
3.10           2021-10-04     2026-10
3.9            2020-10-05     2025-10
3.8            2019-10-14     2024-10
3.7            2018-06-27     2023-06-27
============== ============== ==============

Sphinx Version
--------------

============== ============== ==============
Sphinx Version First Released End of Support 
============== ============== ==============
5.0            2022-05-30     2027-05
4.0            2021-05-09     2026-05
3.1            2020-06-08     2025-06
============== ============== ==============

Should a supported Sphinx version only work with an unsupported Python version
then that Sphinx version will be dropped early. This is in anticipation of
possible CI limitations running unsupported versions.

Clang Version
-------------

============= ============== ==============
Clang Version First Released End of Support 
============= ============== ==============
15.0          2022-09-26     2027-09
14.0          2022-03-25     2027-03
13.0          2021-10-04     2026-10
12.0          2021-04-14     2026-04
11.0          2020-10-12     2025-10
10.0          2020-03-24     2025-03
9.0           2019-09-19     2024-09
8.0           2019-03-20     2024-03
7.0           2018-09-19     2023-09
6.0           2018-03-08     2023-06
============= ============== ==============

Since Clang seems to be on a 6 month release cycle while Python is on a one
year, and that this package uses few features of Clang, this package will most
likely continue to support some versions of Clang until the nearest Python
version gets removed.

.. note:: The different Clang versions are *not* exercised in CI. Most of the
   Python API for Clang seems pretty stable and as long as the most recent
   version of Clang keeps working it's hoped that it will catch most issues.
