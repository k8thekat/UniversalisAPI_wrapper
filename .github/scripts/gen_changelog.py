# ruff: noqa
import pathlib
import subprocess  # noqa: S404
from pathlib import Path
import re

# Unique information for the project.
user = "k8thekat"
gitHub_repo_name: str = "UniversalisAPI_wrapper"
project_name: str = "async_universalis"
project_dir: pathlib.Path = pathlib.Path().joinpath(project_name)
project_branch: str = "development"
repo_url = f"https://github.com/k8thekat/{gitHub_repo_name}"

# Initializing a Repo only.
_flag: bool = False


# Grab Version from __init__.py
version = ""
with Path().parent.parent.parent.parent.joinpath(f"{project_name}/__init__.py").open() as file:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', file.read(), re.MULTILINE).group(1)  # type:ignore

if not version:
    raise RuntimeError("Version is not set")


cl_file: pathlib.Path = pathlib.Path().parent.parent.parent.parent.joinpath("CHANGELOG.md")
if cl_file.exists() is False:
    msg = "Unable to locate the file. %s"
    raise FileNotFoundError(msg, cl_file.as_posix())


# Grab Version from `CHANGELOG.md`
with cl_file.open(encoding="utf-8") as changelog:
    changelog_data = changelog.read()
    split_data = changelog_data.split("\n")
    ver_data = split_data[0]  # Version - *.*.*** (commit hash)
    ver_data = ver_data.split(" ")
    last_commit: str = ver_data[-1][1:8]
    cl_ver: str = ver_data[-3]

# If the version is `0.0.0` we are initializing the repo.
if cl_ver == "0.0.0":
    _flag = True

# Compare CHANGELOG.md and __init__.py Versions.
if _flag is False and (not version or cl_ver == version):
    msg = "<%s> | Version has not been updated `%s`: %s == `CHANGELOG.md`: %s"
    raise ValueError(msg, "Changelog Generator", gitHub_repo_name, version, cl_ver)


def gitHub_commit() -> None:
    # Verify that the current branch is `project_branch`.
    output: bytes = subprocess.check_output(["git", "branch"])
    branch: str = output.decode("utf-8").strip("*").strip().split("\n")[0]
    if branch != project_branch:
        msg = "<%s> | Current branch is not `%s`: %s"
        raise RuntimeError(msg, "Changelog Generator", project_branch, changelog)

    # Verify that there are new commits.
    output = subprocess.check_output(["git", "log"])
    new_commit = output.decode("utf-8").split("\n")[0][7:14]
    if new_commit == last_commit:
        msg = "No new commits since last version: %s == %s"
        raise RuntimeError(msg, last_commit, new_commit)

    # Format the git log data into a dictionary for Changelog.
    output = subprocess.check_output(["git", "log", '--format="%B"', last_commit + "..HEAD"])
    files: dict[str, list[str]] = {}
    cur_data = output.decode("utf-8")
    cur_data = cur_data.strip().strip('"')
    cur_data = cur_data.split("\n")
    file_name = None
    for entry in cur_data:
        _entry = entry
        if len(entry) == 0 or len(entry) == 1:
            continue
        if entry.startswith("$"):
            # This should skip our auto generated changelog commit from Github Actions.
            continue

        if entry.startswith('"'):
            _entry = entry.strip('"')

        elif entry.startswith("#"):
            file_name = entry[1:].strip()
            if file_name not in files:
                files[file_name] = []

        else:
            if entry.startswith("--"):
                _entry = "\t-" + entry[2:]
            if file_name is None:
                file_name = "Overall"
                files[file_name] = []
            files[file_name].append(_entry)

    update_changelog(version=version, new_commit=new_commit, files=files)


def gitHub_initial_commit() -> None:
    # Verify that there are new commits.
    output = subprocess.check_output(["git", "log"])
    new_commit = output.decode("utf-8").split("\n")[0][7:14]
    if new_commit == last_commit:
        msg = "No new commits since last version: %s == %s"
        raise RuntimeError(msg, last_commit, new_commit)

    # Format the git log data into a dictionary for Changelog.
    output = subprocess.check_output(["git", "log", '--format="%B"'])
    headers: dict[str, list[str]] = {}
    cur_data = output.decode("utf-8")
    cur_data = cur_data.strip().strip('"')
    cur_data = cur_data.split("\n")
    header = None
    for entry in cur_data:
        _entry = entry
        if len(entry) == 0 or len(entry) == 1:
            continue
        if entry.startswith("$"):
            # This should skip our auto generated changelog commit from Github Actions.
            continue

        if entry.startswith('"'):
            _entry = entry.strip('"')

        elif entry.startswith("#"):
            header = entry[1:].strip()
            if header not in headers:
                headers[header] = []

        else:
            if entry.startswith("--"):
                _entry = "\t-" + entry[2:]
            if header is None:
                header = "Overall"
                headers[header] = []
            headers[header].append(_entry)

    update_changelog(version=version, new_commit=new_commit, files=headers)


def update_changelog(version: str, new_commit: str, files: dict[str, list[str]]) -> None:
    # Format the data into the `CHANGELOG.md`
    set_version = f"# Version - {version} - [{new_commit[:7]}]({repo_url}/commit/{new_commit})\n"
    data = set_version
    for file_name, file_changes in files.items():
        data: str = data + "## " + file_name + "\n" + "\n".join(file_changes) + "\n\n"

    data = data + changelog_data
    with cl_file.open("r+", encoding="utf-8") as changelog:
        changelog.seek(0)
        changelog.truncate()
        changelog.write(data)


if _flag is True:
    gitHub_initial_commit()
else:
    gitHub_commit()

# Github Actions Checkout/Commit
# id | k8thekat = 68672235
subprocess.run(["git", "config", "user.name", "github-actions[bot]"], check=False)
subprocess.run(["git", "config", "user.email", "68672235+github-actions[bot]@users.noreply.github.com"], check=False)
subprocess.run(["git", "add", "."], check=False)
subprocess.run(["git", "commit", "-m", f"$ Autogenerated Changelog for {version}"], check=False)
subprocess.run(["git", "push", "--force"], check=False)
