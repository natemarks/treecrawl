import os
import shutil

import nox


def tests_impl(session):
    # Install deps and the package itself.
    session.install("-e", ".[dev]")

    # Show the pip version.
    session.run("pip", "--version")
    # Print the Python version and bytesize.
    session.run("python", "--version")

    session.run(
        "coverage",
        "run",
        "--parallel-mode",
        "-m",
        "pytest",
        "-r",
        "a",
        "--tb=native",
        "--no-success-flaky-report",
        *(session.posargs or ("test/",)),
        env={"PYTHONWARNINGS": "always::DeprecationWarning"}
    )
    # session.run("coverage", "combine")
    # session.run("coverage", "report", "-m")
    # session.run("coverage", "xml")


@nox.session(python=["3.5", "3.6", "3.7", "3.8", "3.9", "pypy"])
def test(session):

    # Install deps and the package itself.
    session.install("-e", ".[dev]")

    # Show the pip version.
    session.run("pip", "--version")
    # Print the Python version and bytesize.
    session.run("python", "--version")
    # This CD is really important. it allows the tests to locate testdata
    # I should fix the tests to dynamically locate testdata
    session.cd("tests")
    session.run("pytest")


@nox.session()
def blacken(session):
    """Run black code formatter."""
    session.install("black")
    session.run(
        "black",
        "--line-length",
        "79",
        "treecrawl",
        "tests",
        "noxfile.py",
        "setup.py",
    )

    lint(session)


@nox.session
def lint(session):
    session.install("flake8", "black")
    session.run("flake8", "--version")
    session.run("black", "--version")
    session.run(
        "black",
        "--check",
        "--line-length",
        "79",
        "treecrawl",
        "tests",
        "noxfile.py",
        "setup.py",
    )

    session.run(
        "flake8",
        "treecrawl",
        "tests",
        "noxfile.py",
        "setup.py",
    )


@nox.session
def docs(session):
    session.install("-e", ".[dev]")
    session.install(".[socks,secure,brotli]")

    session.chdir("docs")
    if os.path.exists("_build"):
        shutil.rmtree("_build")
    session.run("sphinx-build", "-W", ".", "_build/html")
