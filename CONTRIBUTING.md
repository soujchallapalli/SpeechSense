# Contributing to `SpeechSense`

Contributions are welcome, and they are greatly appreciated!
Every little bit helps, and credit will always be given.

You can contribute in many ways:

# Types of Contributions

## Report Bugs

Report bugs at https://github.com/SpeechSense/SpeechSense/issues

If you are reporting a bug, please include:

- Your operating system name and version.
- Any details about your local setup that might be helpful in troubleshooting.
- Detailed steps to reproduce the bug.

## Fix Bugs

Look through the GitHub issues for bugs.
Anything tagged with "bug" and "help wanted" is open to whoever wants to implement a fix for it.

## Implement Features

Look through the GitHub issues for features.
Anything tagged with "enhancement" and "help wanted" is open to whoever wants to implement it.

## Write Documentation

SpeechSense could always use more documentation, please include additional docs in mkdocs.

## Submit Feedback

The best way to send feedback is to file an issue at https://github.com/SpeechSense/SpeechSense/issues

If you are proposing a new feature:

- Explain in detail how it would work.
- Keep the scope as narrow as possible, to make it easier to implement.
- Remember that this is a birkbeck-driven project, and that contributions
  are welcome :)

# Get Started!

Ready to contribute? Here's how to set up `SpeechSense` for local development.
Please note this documentation assumes you already have `Poetry` and `Git` installed and ready to go.

1. Fork the `SpeechSense` repo on GitHub.

2. Clone your fork locally:

```bash
cd <directory_in_which_repo_should_be_created>
git clone git@github.com:YOUR_NAME/SpeechSense.git
```

3. Navigate into the directory and install the environment:

```bash
cd SpeechSense
make install
```

This installs all dependencies and sets up pre-commit hooks.

4. Create a branch for local development:

```bash
git checkout -b name-of-your-bugfix-or-feature
```

Now you can make your changes locally.

5. Don't forget to add test cases for your added functionality to the `tests` directory.

6. When you're done making changes, check that your changes pass the formatting and type checks:

```bash
make check
```

Now, validate that all unit tests are passing:

```bash
make test
```

7. Commit your changes and push your branch to GitHub:

```bash
git add .
git commit -m "Your detailed description of your changes."
git push origin name-of-your-bugfix-or-feature
```

8. Submit a pull request through the GitHub website.

# Pull Request Guidelines

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.

2. If the pull request adds functionality, the docs should be updated.
