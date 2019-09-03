Contributing
============

Contributions to Allagash are very welcome. They are likely to be accepted more quickly if they follow these guidelines.


- All existing tests should pass. Please make sure that the test suite passes, both locally and on the configured CI.
- New functionality should include tests. Please write reasonable tests for your code and make sure that they pass on your pull request.
- Classes, methods, functions, etc. should have docstrings. The first line of a docstring should be a standalone summary. Parameters and return values should be documented explicitly.
- Follow PEP 8 when possible.
- Imports should be grouped with standard library imports first, 3rd-party libraries next, and allagash imports third. Within each grouping, imports should be alphabetized. Always use absolute imports when possible, and explicit relative imports for local imports when necessary in tests.


Steps for Contributing
----------------------

There are basic steps to contributing to allagash:

    1. Fork the allagash git repository
    2. Create a development environment
    3. Install allagash dependencies
    4. Make a development build of allagash
    5. Make changes to code and add tests
    6. Update the documentation
    7. Submit a Pull Request
