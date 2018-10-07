import os
from distutils.spawn import find_executable
from conans import ConanFile


class RubyInstallerTestConan(ConanFile):
    def test(self):
        self.output.info("which ruby: {}".format(find_executable("ruby")))
        self.run("ruby -v")
