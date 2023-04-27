from setuptools import setup

setup(
    name="crude_link",
    version="0.1",
    py_modules=["crude_link"],
    install_requires=["click", "termcolor", "omegaconf", "apscheduler", "fire"],
    entry_points="""
        [console_scripts]
        crude_link=crude_link:main
    """,
)
