""" This module offers highlevel functions to get package metadata
    like the METADATA file, the name, or a list of dependencies.

    Example usages see README.rst
"""

from io import open  # needed for python 2
import os
from pep517.envbuild import BuildEnvironment
from pep517.wrappers import Pep517HookCaller
import pytoml
import shutil
import subprocess
import sys
import tarfile
import tempfile
import textwrap
import time
try:
    from urllib.parse import urlparse
except ImportError:  # Python 2...
    from urlparse import urlparse
import zipfile


def extract_metainfo_files_from_package(
        package,
        output_folder,
        debug=False
        ):
    """ Extracts metdata files from the given package, and write them
        to the given output folder.

        THe package may be referenced in any way that is permitted in
        a requirements.txt file or install_requires=[] listing, including
        with version pins, or as a folder path, or other.

        Current supported metadata files that will be extracted:

        - pytoml.yml  (only if package wasn't obtained as wheel)
        - METAINFO
    """

    if package is None:
        raise ValueError("package cannot be None")

    if not os.path.exists(output_folder) or os.path.isfile(output_folder):
        raise ValueError("output folder needs to be existing folder")

    # A temp folder for making a package copy in case it's a local folder,
    # because extracting metadata might modify files
    # (creating sdists/wheels...)
    temp_folder = tempfile.mkdtemp(prefix="pythonpackage-package-copy-")
    try:
        # Package is indeed a folder! Get a temp copy to work on:
        if is_filesystem_path(package):
            shutil.copytree(
                parse_as_folder_reference(package),
                os.path.join(temp_folder, "package")
            )
            package = os.path.join(temp_folder, "package")

        # Because PEP517 can be noisy and contextlib.redirect_* fails to
        # contain it, we will run the actual analysis in a separate process:
        try:
            subprocess.check_output([
                sys.executable,
                "-c",
                "import json\n"
                "import sys\n"
                "from pep517.metadata import "
                "_extract_metainfo_files_from_package_unsafe;\n"
                "_extract_metainfo_files_from_package_unsafe("
                "    sys.argv[1],"
                "    sys.argv[2],"
                ")",
                package, output_folder],
                stderr=subprocess.STDOUT,  # make sure stderr is muted.
                cwd=os.path.join(os.path.dirname(__file__), "..")
            )
        except subprocess.CalledProcessError as e:
            output = e.output
            try:
                output = output.decode('utf-8', 'replace')
            except AttributeError:
                pass
            if debug:
                print("Got error obtaining meta info.")
                print("Detail output:")
                print(output)
                print("End of Detail output.")
            raise ValueError(
                "failed to obtain meta info - " +
                "is this a valid package? Detailed output:\n" +
                output
            )
    finally:
        shutil.rmtree(temp_folder)


def _get_system_python_executable():
    """ Attempts to get a system-wide python binary name.
        Returns sys.executable in case of failure.
    """
    # This function is required by get_package_as_folder() to work
    # inside a virtualenv, since venv creation will fail with
    # the virtualenv's local python binary.
    # (venv/virtualenv incompatibility)

    python_name = "python" + sys.version

    def binary_is_usable(python_bin):
        try:
            filenotfounderror = FileNotFoundError
        except NameError:  # Python 2.
            filenotfounderror = OSError
        try:
            subprocess.check_output([python_bin, "--version"])
            return True
        except (subprocess.CalledProcessError, filenotfounderror):
            return False

    while (not binary_is_usable(python_name) and
           python_name.find(".") > 0):
        # Try less specific binary name:
        python_name = python_name.rpartition(".")[0]
    if not binary_is_usable(python_name):
        # Fall back to sys.executable:
        return sys.executable
    return python_name


def get_package_as_folder(dependency, major_python_version=3):
    """ This function downloads the given package / dependency and extracts
        the raw contents into a folder.

        Afterwards, it returns a tuple with the type of distribution obtained,
        and the temporary folder it extracted to.

        Examples of returned values:

        ("source", "/tmp/pythonpackage-venv-e84toiwjw")
        ("wheel", "/tmp/pythonpackage-venv-85u78uj")

        What the distribution type will be depends on what pip decides to
        download.
    """

    venv_parent = tempfile.mkdtemp(
        prefix="pythonpackage-venv-"
    )
    try:
        # Create a venv to install into:
        try:
            subprocess.check_output([
                _get_system_python_executable(), "-m", "venv",
                os.path.join(venv_parent, 'venv')
            ], cwd=venv_parent)
        except subprocess.CalledProcessError as e:
            output = e.output
            try:
                output = output.decode('utf-8', 'replace')
            except AttributeError:
                pass
            raise ValueError(
                'venv creation unexpectedly ' +
                'failed. error output: ' + str(output)
            )
        venv_path = os.path.join(venv_parent, "venv")

        # Update pip and wheel in venv for latest feature support:
        subprocess.check_output([
            os.path.join(venv_path, "bin", "pip"),
            "install", "-U", "pip", "wheel",
        ])

        # Create download subfolder:
        os.mkdir(os.path.join(venv_path, "download"))

        # Write a requirements.txt with our package and download:
        with open(os.path.join(venv_path, "requirements.txt"),
                  "w", encoding="utf-8"
                  ) as f:
            def to_unicode(s):  # Needed for Python 2.
                try:
                    return s.decode("utf-8")
                except AttributeError:
                    return s
            f.write(to_unicode(dependency))
        try:
            subprocess.check_output(
                [
                    os.path.join(venv_path, "bin", "pip"),
                    "download", "--no-deps", "-r", "../requirements.txt",
                    "-d", os.path.join(venv_path, "download")
                ],
                stderr=subprocess.STDOUT,
                cwd=os.path.join(venv_path, "download")
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError("package download failed: " + str(e.output))

        if len(os.listdir(os.path.join(venv_path, "download"))) == 0:
            # No download. This can happen if the dependency has a condition
            # which prohibits install in our environment.
            return (None, None)

        # Get the result and make sure it's an extracted directory:
        result_folder_or_file = os.path.join(
            venv_path, "download",
            os.listdir(os.path.join(venv_path, "download"))[0]
        )
        dl_type = "source"
        if not os.path.isdir(result_folder_or_file):
            # Must be an archive.
            if result_folder_or_file.endswith(".zip") or \
                    result_folder_or_file.endswith(".whl"):
                if result_folder_or_file.endswith(".whl"):
                    dl_type = "wheel"
                with zipfile.ZipFile(result_folder_or_file) as f:
                    f.extractall(os.path.join(venv_path,
                                              "download", "extracted"
                                              ))
                    result_folder_or_file = os.path.join(
                        venv_path, "download", "extracted"
                    )
            elif result_folder_or_file.find(".tar.") > 0:
                # Probably a tarball.
                with tarfile.open(result_folder_or_file) as f:
                    f.extractall(os.path.join(venv_path,
                                              "download", "extracted"
                                              ))
                    result_folder_or_file = os.path.join(
                        venv_path, "download", "extracted"
                    )
            else:
                raise RuntimeError(
                    "unknown archive or download " +
                    "type: " + str(result_folder_or_file)
                )

        # If the result is hidden away in an additional subfolder,
        # descend into it:
        while os.path.isdir(result_folder_or_file) and \
                len(os.listdir(result_folder_or_file)) == 1 and \
                os.path.isdir(os.path.join(
                    result_folder_or_file,
                    os.listdir(result_folder_or_file)[0]
                )):
            result_folder_or_file = os.path.join(
                result_folder_or_file,
                os.listdir(result_folder_or_file)[0]
            )

        # Copy result to new dedicated folder so we can throw away
        # our entire virtualenv nonsense after returning:
        result_path = tempfile.mkdtemp()
        shutil.rmtree(result_path)
        shutil.copytree(result_folder_or_file, result_path)
        return (dl_type, result_path)
    finally:
        shutil.rmtree(venv_parent)


def _extract_metainfo_files_from_package_unsafe(
        package,
        output_path
        ):
    # This is the unwrapped function that will
    # 1. make lots of stdout/stderr noise
    # 2. possibly modify files (if the package source is a local folder)
    # Use extract_metainfo_files_from_package_folder instead which avoids
    # these issues.

    clean_up_path = False
    path_type = "source"
    path = parse_as_folder_reference(package)
    if path is None:
        # This is not a path. Download it:
        (path_type, path) = get_package_as_folder(package)
        if path_type is None:
            # Download failed.
            raise ValueError(
                "cannot get info for this package, " +
                "pip says it has no downloads (conditional dependency?)"
            )
        clean_up_path = True

    try:
        build_requires = []
        metadata_path = None
        if path_type != "wheel":
            # We need to process this first to get the metadata.

            # Ensure pyproject.toml is available (pep517 expects it)
            if not os.path.exists(os.path.join(path, "pyproject.toml")):
                with open(os.path.join(path, "pyproject.toml"), "w") as f:
                    f.write(textwrap.dedent(u"""\
                    [build-system]
                    requires = ["setuptools", "wheel"]
                    build-backend = "setuptools.build_meta"
                    """))

            # Copy the pyproject.toml:
            shutil.copyfile(
                os.path.join(path, 'pyproject.toml'),
                os.path.join(output_path, 'pyproject.toml')
            )

            # Get build backend from pyproject.toml:
            with open(os.path.join(path, 'pyproject.toml')) as f:
                build_sys = pytoml.load(f)['build-system']
                backend = build_sys["build-backend"]

            # Get a virtualenv with build requirements and get all metadata:
            env = BuildEnvironment()
            metadata = None
            with env:
                hooks = Pep517HookCaller(path, backend)
                env.pip_install(build_requires)
                reqs = hooks.get_requires_for_build_wheel({})
                env.pip_install(reqs)
                try:
                    metadata = hooks.prepare_metadata_for_build_wheel(path)
                except Exception:  # sadly, pep517 has no good error here
                    pass
            if metadata is not None:
                metadata_path = os.path.join(
                    path, metadata, "METADATA"
                )
        else:
            # This is a wheel, so metadata should be in *.dist-info folder:
            metadata_path = os.path.join(
                path,
                [f for f in os.listdir(path) if f.endswith(".dist-info")][0],
                "METADATA"
            )

        # Copy the metadata file:
        shutil.copyfile(metadata_path, os.path.join(output_path, "METADATA"))
    finally:
        if clean_up_path:
            shutil.rmtree(path)


def is_filesystem_path(dep):
    if dep.startswith("/") or dep.startswith("file://") or (
            dep.find("/") > 0 and
            dep.find("://") < 0 and
            (dep.find("@") < 0 or
             dep.find("@") > dep.find("/"))):
        return True
    return False


def parse_as_folder_reference(dep):
    """ See if a dependency reference refers to a folder path.
        If it does, return the folder path (which parses and
        resolves file:// urls in the process).
        If it doesn't, return None.
    """
    if dep.startswith("/") or dep.startswith("file://") or (
            dep.find("/") > 0 and
            dep.find("://") < 0):
        if dep.startswith("file://"):
            dep = urlparse(dep).path
        return dep
    return None


def _extract_info_from_package(dependency, extract_type=None, debug=False):
    """ Internal function to extract metainfo from a package.
        Currently supported info types:

        - name
        - namewithpins  (an exact version pin is kept if any)
        - dependencies  (a list of dependencies)
    """
    output_folder = tempfile.mkdtemp(prefix="pythonpackage-metafolder-")
    try:
        extract_metainfo_files_from_package(
            dependency, output_folder, debug=debug
        )

        with open(os.path.join(output_folder, "METADATA"),
                  "r", encoding="utf-8"
                  ) as f:
            # Get metadata and cut away description (is after 2 linebreaks)
            metadata_entries = f.read().partition("\n\n")[0].splitlines()

        if extract_type == "name" or extract_type == "namewithpins":
            name = None
            for meta_entry in metadata_entries:
                if meta_entry.lower().startswith("name:"):
                    return meta_entry.partition(":")[2].strip()
            if name is None:
                raise ValueError("failed to obtain package name")

            if extract_type == "namewithpins" and \
                    dependency.find("==") > 0 and \
                    dependency.partition("==")[0].lower() == name.lower():
                return name + "==" + dependency.partition("==")[2].lstrip()
            return name
        elif extract_type == "dependencies":
            requirements = []
            if os.path.exists(os.path.join(output_folder, 'pyproject.toml')):
                with open(os.path.join(output_folder, 'pyproject.toml')) as f:
                    build_sys = pytoml.load(f)['build-system']
                    if "requires" in build_sys:
                        requirements += build_sys["requires"]

            # Add requirements from metadata:
            requirements += [
                entry.rpartition("Requires-Dist:")[2].strip()
                for entry in metadata_entries
                if entry.startswith("Requires-Dist")
            ]

            return list(set(requirements))  # remove duplicates
    finally:
        shutil.rmtree(output_folder)


package_name_cache = dict()


def get_package_name(dependency, use_cache=True):
    def timestamp():
        try:
            return time.monotonic()
        except AttributeError:
            return time.time()  # Python 2.
    try:
        value = package_name_cache[dependency]
        if value[0] + 600.0 > timestamp() and use_cache:
            return value[1]
    except KeyError:
        pass
    result = _extract_info_from_package(dependency, extract_type="name")
    package_name_cache[dependency] = (timestamp(), result)
    return result


def get_package_dependencies(
        package,
        recursive=False, verbose=False, cached_names=True
        ):
    """ Obtain the dependencies from a package. Please note this
        function is possibly SLOW, especially if you enable
        the recursive mode.

        @param recursive whether to fetch all indirect dependencies as well
        @param verbose whether to output verbose info while processing
        @param cached_names whether to not refetch package names when they
                            have been recently determined

        Returns a list of dependencies as strings, including all
        the restrictions like version pins that were specified by the package.
    """
    packages_processed = set()
    package_queue = [package]
    reqs = []
    reqs_as_names = []
    while len(package_queue) > 0:
        current_queue = package_queue
        package_queue = []
        for package_dep in current_queue:
            new_reqs = []
            if verbose:
                print("get_package_dependencies: resolving dependecy " +
                      "to package name: " + str(package_dep))
            package = get_package_name(package_dep, use_cache=cached_names)
            if package.lower() in packages_processed:
                continue
            if verbose:
                print("get_package_dependencies: processing package: " +
                      str(package),
                      )
                print("get_package_dependencies: Packages seen so far: " +
                      str(packages_processed),
                      )
            packages_processed.add(package.lower())

            # Use our regular folder processing to examine:
            new_reqs += _extract_info_from_package(
                package_dep, extract_type="dependencies",
                debug=verbose,
            )

            # Process new requirements:
            if verbose:
                print("get_package_dependencies: collected " +
                      "indirect deps: " + str(new_reqs),
                      )
            for new_req in new_reqs:
                try:
                    req_name = get_package_name(new_req)
                except ValueError as e:
                    if new_req.find(";") >= 0:
                        # Conditional dep where condition isn't met?
                        # --> ignore it
                        continue
                    if verbose:
                        print("get_package_dependencies: " +
                              "unexpected failure to get name " +
                              "of '" + str(new_req) + "': " +
                              str(e))
                    raise RuntimeError(
                        "failed to get " +
                        "name of dependency: " + str(e)
                    )
                if req_name.lower() in reqs_as_names:
                    continue
                if req_name.lower() not in packages_processed:
                    package_queue.append(new_req)
                reqs.append(new_req)
                reqs_as_names.append(req_name.lower())

            # Bail out here if we're not scanning recursively:
            if not recursive:
                package_queue[:] = []  # wipe queue
                break
    if verbose:
        print("get_package_dependencies: returning result: " +
              str(reqs))
    return list(set(reqs))  # Remove duplicates on return
