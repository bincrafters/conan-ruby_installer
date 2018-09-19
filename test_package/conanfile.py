import os
import shutil
from conans import ConanFile


class RubyInstallerTestConan(ConanFile):
    def test(self):
        self.output.info("which ruby: {}".format(shutil.which("ruby")))
        self.run("ruby -v")
