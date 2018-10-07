from conans import ConanFile, tools
import shutil
import os.path


class RubyInstallerConan(ConanFile):
    name = "ruby_installer"
    version = "2.5.1"
    api_version = "2.5.0"
    rubyinstaller_release = "2"
    license = "MIT"
    settings = "os_build", "arch_build"
    url = "https://github.com/elizagamedev/conan-ruby_installer"
    description = "Install Ruby binaries for use in recipies"
    exports = "LICENSE.md"

    folder = "ruby-{}".format(version)

    def system_requirements(self):
        if tools.os_info.is_linux:
            installer = tools.SystemPackageTool()
            packages = ["ruby"]
            installer.install("ruby")
            if tools.os_info.with_apt:
                packages.append("zlib1g-dev")
            elif tools.os_info.is_linux and not tools.os_info.with_pacman:
                packages.append("zlib-devel")
            installer.install(packages)

    def build_requirements(self):
        if tools.os_info.is_windows:
            self.build_requires("7z_installer/1.0@conan/stable")

    def source(self):
        if not tools.os_info.is_windows:
            tools.get("https://cache.ruby-lang.org/pub/ruby/{}/{}.tar.gz".format(
                self.version.rpartition(".")[0],
                self.folder))

    def build_ruby(self):
        with tools.chdir(self.folder):
            args = [
                "--prefix={}".format(self.package_folder),
                "--disable-install-doc",
                "--with-out-ext=gdbm,openssl,pty,readline,syslog",
                "--without-gmp",
            ]
            self.run("./configure {}".format(" ".join(args)))
            self.run("make")
            self.run("make install")

    def build(self):
        if tools.os_info.is_windows:
            # Extract binaries into a directory called "ruby"
            arch = {"x86": "x86",
                    "x86_64": "x64"}[str(self.settings.arch_build)]
            name = "rubyinstaller-{}-{}".format(self.version, self.rubyinstaller_release)
            folder = "{}-{}".format(name, arch)
            url = "https://github.com/oneclick/rubyinstaller2/releases/download/{}/{}.7z".format(
                name, folder)
            tools.download(url, "ruby.7z")
            self.run("7z x {}".format("ruby.7z"))
            shutil.move(folder, self.folder)
            # Remove non-standard defaults directory
            shutil.rmtree(os.path.join(self.folder, "lib", "ruby", self.api_version, "rubygems", "defaults"))
        else:
            # On Unix, the binaries are less reliable. We will have to build it
            # ourselves.
            self.build_ruby()

    def package(self):
        if tools.os_info.is_windows:
            self.copy("*", src=self.folder, symlinks=True, excludes="LICENSE.txt")
            self.copy("LICENSE.txt", dst="license", src=self.folder)
        else:
            self.copy("LEGAL", dst="license", src=self.folder)
            self.copy("GPL", dst="license", src=self.folder)

    def package_info(self):
        self.env_info.path.append(os.path.join(self.package_folder, "bin"))
