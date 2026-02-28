# Introducción a GitHub Copilot

<img src="https://octodex.github.com/images/Professortocat_v2.png" align="right" height="200px" />

Hey DarioRoblesUnahur!

Mona here. I'm done preparing your exercise. Hope you enjoy! 💚

Remember, it's self-paced so feel free to take a break! ☕️

[![](https://img.shields.io/badge/Go%20to%20Exercise-%E2%86%92-1f883d?style=for-the-badge&logo=github&labelColor=197935)](https://github.com/DarioRoblesUnahur/unahur-getting-started-with-github-copilot/issues/1)

---

&copy; 2025 GitHub &bull; [Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/code_of_conduct.md) &bull; [MIT License](https://gh.io/mit)

---

## Running the tests

This project includes a comprehensive pytest suite for testing the FastAPI backend. Tests are structured using the **Arrange–Act–Assert (AAA)** pattern for clarity.

### Install dependencies

```sh
pip install -r requirements.txt
```

### Run the test suite

```sh
pytest
```

### Test coverage

The test suite covers:
- **Fetching activities**: Verify all activities are retrievable with correct metadata
- **Signup**: Successful signup, duplicate prevention, nonexistent activity handling, email normalization
- **Withdrawal**: Successful removal, error cases (not signed up, nonexistent activity), email normalization
- **Roundtrip tests**: Full signup → withdrawal cycles
- **Multi-activity**: Users signing up for multiple activities

Each test includes clear **Arrange**, **Act**, and **Assert** sections for readability and easy debugging.

