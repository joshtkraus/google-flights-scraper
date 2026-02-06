"""Generate the code references pages and navigation."""

from pathlib import Path

import mkdocs_gen_files

nav = mkdocs_gen_files.Nav()

repo_dir = Path(__file__).parents[1]
src_dir = repo_dir / "src"
module_dir = src_dir / "google_flights_scraper"
test_dir = repo_dir / "tests"

for path in [
    p
    for p in sorted(repo_dir.rglob("*py"))
    if p.is_relative_to(module_dir) and not p.is_relative_to(test_dir)
]:
    module_path = path.relative_to(src_dir).with_suffix("")
    doc_path = path.relative_to(src_dir).with_suffix(".md")
    full_doc_path = Path("reference", doc_path)

    parts = tuple(module_path.parts)

    if parts[-1] == "__init__":
        parts = parts[:-1]
        doc_path = doc_path.with_name("index.md")
        full_doc_path = full_doc_path.with_name("index.md")
    elif parts[-1] == "__main__":
        continue

    nav[parts] = doc_path.as_posix()

    with mkdocs_gen_files.open(full_doc_path, "w") as fd:
        indent = ".".join(parts)
        fd.write(f"::: {indent}")

    mkdocs_gen_files.set_edit_path(full_doc_path, path)

with mkdocs_gen_files.open("reference/SUMMARY.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())
