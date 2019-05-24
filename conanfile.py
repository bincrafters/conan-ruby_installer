# -*- coding: utf-8 -*-
import os
from conans import ConanFile, tools, AutoToolsBuildEnvironment


class RubyInstallerConan(ConanFile):
    name = "ruby_installer"
    version = "2.5.1"
    license = "MIT"
    settings = "os_build", "arch_build", "compiler"
    url = "https://github.com/bincrafters/conan-ruby_installer"
    homepage = "https://www.ruby-lang.org/"
    description = "Ruby binaries for use in recipies"
    author = "Bincrafters <bincrafters@gmail.com>"
    exports = "LICENSE.md"
    _autotools = None

    @property
    def _api_version(self):
        return "2.5.0"

    @property
    def _rubyinstaller_release(self):
        return "2"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        if self.settings.os_build == "Linux":
            self.requires("zlib/1.2.11@conan/stable")

    def build_requirements(self):
        if self.settings.os_build == "Windows":
            self.build_requires("7z_installer/1.0@conan/stable")

    def source(self):
        if self.settings.os_build != "Windows":
            sha256 = "dac81822325b79c3ba9532b048c2123357d3310b2b40024202f360251d9829b1"
            source_url = "https://cache.ruby-lang.org"
            tools.get("{}/pub/ruby/{}/ruby-{}.tar.gz".format(
                source_url,
                self.version.rpartition(".")[0],
                self.version), sha256=sha256)
            extracted_folder = "ruby-" + self.version
            os.rename(extracted_folder, self._source_subfolder)

    def _configure_autotools(self):
        if not self._autotools:
            self._autotools = AutoToolsBuildEnvironment(self)
            args = [
                "--disable-install-doc",
                "--with-out-ext=gdbm,openssl,pty,readline,syslog",
                "--without-gmp",
                "--enable-load-relative"
            ]
            self._autotools.configure(args=args, configure_dir=self._source_subfolder)
        return self._autotools

    def _configure_installer(self):
        # Extract binaries into a directory called "ruby"
        arch = {"x86": "x86",
                "x86_64": "x64"}[str(self.settings.arch_build)]
        name = "rubyinstaller-{}-{}".format(self.version, self._rubyinstaller_release)
        folder = "{}-{}".format(name, arch)
        url = "https://github.com/oneclick/rubyinstaller2/releases/download/{}/{}.7z".format(
            name, folder)
        tools.download(url, "ruby.7z")
        self.run("7z x {}".format("ruby.7z"), run_environment=True)
        os.rename(folder, self._source_subfolder)
        # Remove non-standard defaults directory
        tools.rmdir(os.path.join(self._source_subfolder, "lib", "ruby", self._api_version, "rubygems", "defaults"))

    def build(self):
        if tools.os_info.is_windows:
            self._configure_installer()
        else:
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        if tools.os_info.is_windows:
            self.copy("*", src=self._source_subfolder, symlinks=True, excludes="LICENSE.txt")
            self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)
        else:
            self.copy("LEGAL", dst="licenses", src=self._source_subfolder)
            self.copy("GPL", dst="licenses", src=self._source_subfolder)
            autotools = self._configure_autotools()
            autotools.install()

    def package_id(self):
        del self.info.settings.compiler

    def package_info(self):
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
