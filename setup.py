from setuptools import setup, find_packages

setup(
    name="dashboard-scraper",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests>=2.31.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "dashboard-scraper=dashboard_scraper.main:main",
        ],
    },
    python_requires=">=3.9",
)

