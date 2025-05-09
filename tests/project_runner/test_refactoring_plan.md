# Test Refactoring Plan: unittest to pytest

## Completed Conversions
The following files have been successfully converted from unittest to pytest style:

- `tests/project_runner/test_process.py`
- `tests/project_runner/test_postgres.py`
- `tests/project_runner/test_servers.py`
- `tests/project_runner/test_cli.py`
- `simulation/tests/test_simulator.py`
- `backend/tests/test_models.py`
- `backend/tests/test_api.py`
- `tests/test_postgres_integration.py`
- `tests/test_run.py`

## Next Steps

Now that all tests have been converted to pytest style, the following steps are recommended for further test improvements:

1. Add test coverage reporting using pytest-cov:
   - Install with `pip install pytest-cov`
   - Run using `pytest --cov=project_runner --cov=simulation --cov=backend`
   - Generate HTML reports with `pytest --cov=project_runner --cov=simulation --cov=backend --cov-report=html`

2. Consolidate fixtures:
   - Move common fixtures to conftest.py files in appropriate directories
   - Create a hierarchy of fixtures to improve reusability
   - Consider using scope='session' for long-running fixtures like database connections

3. Add parameterised tests:
   - Identify test cases that could benefit from parameterisation using `@pytest.mark.parametrize`
   - Reduce code duplication in similar test cases

4. Improve test isolation:
   - Ensure tests don't affect each other through side effects
   - Use dependency injection via fixtures rather than global state

5. Add markers to categorise tests:
   - Mark slow tests with `@pytest.mark.slow`
   - Mark integration tests with `@pytest.mark.integration`
   - Mark tests requiring PostgreSQL with `@pytest.mark.postgres`
   - Configure pytest.ini to define custom markers

6. Create test documentation:
   - Document test fixtures and their purpose
   - Create guides for writing new tests
   - Document test patterns and best practices

7. Set up continuous integration:
   - Configure CI to run tests automatically
   - Add badges to show test status in README.md

## Style and Documentation Guidelines

Continue following these guidelines when writing or modifying tests:

1. Use UK English spelling throughout (examples: behaviour, standardised, organisation)
2. Write documentation in professional, direct style without first-person language
3. Document fixture purpose with clear, concise docstrings
4. Provide meaningful assertion messages that clearly explain failure reasons
5. Use clear, descriptive test names that explain what is being tested

## Conversion Guidelines

### General Approach
1. Replace unittest.TestCase classes with standalone functions
2. Replace setUp/tearDown methods with pytest fixtures
3. Replace self.assert* methods with standard assert statements
4. Implement parameterised testing where multiple similar test cases exist
5. Use context manager-based patching when appropriate

### Best Practices
1. Create focused fixtures that reset test state before and after each test
2. Minimise reliance on global state and class-level variables
3. Group related test inputs using pytest.mark.parametrize
4. Separate test setup, action, and assertion phases with blank lines for readability
5. Break down complex test functions into multiple simpler ones

### Dependencies and Module Path Management
1. Ensure proper path management for importing project modules
2. Avoid direct imports from conftest.py where possible to minimize coupling
3. Handle conflicts between test directory and package names
4. Add any new conftest.py files required for fixtures shared across tests

## Integration with Existing Test Infrastructure
1. Ensure all tests can be run from the project root with `pytest`
2. Verify tests run successfully in the CI/CD pipeline
3. Update any existing test runners to work with pytest
4. Document any special requirements for running tests in README.md

## Test Coverage
1. Maintain or improve existing test coverage
2. Consider adding pytest-cov for test coverage reporting
3. Identify and address any gaps in test coverage during the refactoring

## Timeline
1. Simulation tests: 1 day
2. Backend tests: 1-2 days
3. Root tests: 1 day
4. Validation and documentation updates: 1 day 