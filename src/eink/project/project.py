import os


class Project:
    """Provides information about this library."""

    # The cached return value of root_dir()
    _root_dir = None

    @staticmethod
    def root_dir():
        """Return the root directory of the package."""
        if Project._root_dir is None:
            Project._root_dir = os.path.dirname(
                os.path.dirname(os.path.abspath(__file__)))
        return Project._root_dir

    @staticmethod
    def assets_dir():
        """Return the root directory of the asset files."""
        return os.path.join(Project.root_dir(), 'assets')

    @staticmethod
    def client_code_dir():
        """Return the directory containing the client code."""
        return os.path.join(Project.assets_dir(), 'client')

    @staticmethod
    def images_dir():
        """Return the directory containing the project's images."""
        return os.path.join(Project.assets_dir(), 'images')

    @staticmethod
    def server_skeleton_dir():
        """Return the directory for generating a server skeleton.

        Return the directory containing the files for generating a
        server skeleton.
        """
        return os.path.join(Project.assets_dir(), 'server_skeleton')
