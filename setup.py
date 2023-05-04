from setuptools import setup

setup(
    name="lynx",
    version="0.1",
    py_modules=["lynx", "scheduler"],
    install_requires=[
        "click",
        "termcolor",
        "omegaconf",
        "apscheduler",
        "fire",
        "pre-commit",
        "pytest",
        "tzlocal",
        "fire",
        "psutil",
    ],
    entry_points="""
        [console_scripts]
        lynx=lynx:cli
    """,
)
