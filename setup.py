"""Compatibility entry point for older packaging tools."""

from pathlib import Path

from setuptools import find_packages, setup


ROOT = Path(__file__).parent

setup(
    name="biomethodlens",
    version="0.1.0",
    description="Evidence-linked specialist review for bioinformatics manuscripts",
    long_description=(ROOT / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    author="Kayode Raheem",
    author_email="47569280+kayoderaheem@users.noreply.github.com",
    url="https://github.com/kayoderaheem/BioMethodLens",
    license="MIT",
    package_dir={"": "src"},
    packages=find_packages("src"),
    data_files=[
        (
            "share/biomethodlens/config",
            [str(path.relative_to(ROOT)) for path in (ROOT / "config").glob("*.json")],
        ),
        (
            "share/biomethodlens/schemas",
            [str(path.relative_to(ROOT)) for path in (ROOT / "schemas").glob("*.json")],
        ),
        (
            "share/biomethodlens/prompts/reviewers",
            [str(path.relative_to(ROOT)) for path in (ROOT / "prompts" / "reviewers").glob("*.md")],
        ),
    ],
    python_requires=">=3.9",
    extras_require={"pdf": ["pypdf>=5.0"], "dev": ["coverage>=7.0", "jsonschema>=4.21", "ruff>=0.8"]},
    entry_points={"console_scripts": ["biomethodlens=biomethodlens.cli:main"]},
    zip_safe=False,
)
