# -*- coding: utf-8 -*-
import os
from conans import ConanFile, tools, AutoToolsBuildEnvironment


class RubyInstallerConan(ConanFile):
    name = "ruby_installer"
    version = "2.3.3"
    license = "Ruby"
    settings = "os_build", "arch_build", "compiler"
    url = "https://github.com/bincrafters/conan-ruby_installer"
    homepage = "https://www.ruby-lang.org/"
    description = "Ruby is an interpreted, high-level, general-purpose programming language"
    topics = ("conan", "installer", "ruby", "gem")
    author = "Bincrafters <bincrafters@gmail.com>"
    exports = "LICENSE.md"
    _autotools = None

    @property
    def _api_version(self):
        return "2.3.0"

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
        sha256 = "241408c8c555b258846368830a06146e4849a1d58dcaf6b14a3b6a73058115b7"
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
        arch = {"x86": "i386", "x86_64": "x64"}[str(self.settings.arch_build)]
        folder = "ruby-{}-{}-mingw32".format(self.version, arch)
        url = "https://dl.bintray.com/oneclick/rubyinstaller/{}.7z".format(folder)
        tools.download(url, "ruby.7z")
        self.run("7z x {}".format("ruby.7z"), run_environment=True)
        tools.rmdir(self._source_subfolder)
        os.rename(folder, self._source_subfolder)
        tools.rmdir(os.path.join(self._source_subfolder, "lib", "ruby", self._api_version, "rubygems", "defaults"))

    def build(self):
        if self.settings.os_build == "Windows":
            self._configure_installer()
        else:
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        if self.settings.os_build == "Windows":
            self.copy("*", src=self._source_subfolder, symlinks=True, excludes="LICENSE.txt")
            self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)
        else:
            self.copy("COPYING", dst="licenses", src=self._source_subfolder)
            self.copy("LEGAL", dst="licenses", src=self._source_subfolder)
            self.copy("GPL", dst="licenses", src=self._source_subfolder)
            autotools = self._configure_autotools()
            autotools.install()
            tools.rmdir(os.path.join(self.package_folder, "share"))
            tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_id(self):
        del self.info.settings.compiler

    def package_info(self):
        ruby = os.path.join(self.package_folder, "bin")
        self.output.info('Appending PATH environment variable: %s' % ruby)
        self.env_info.PATH.append(ruby)
