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

    def build_requirements(self):
        if tools.os_info.is_windows:
            self.build_requires("7z_installer/1.0@conan/stable")

    def build(self):
        # Extract binaries into a directory called "ruby"
        if tools.os_info.is_windows:
            arch = {"x86": "x86",
                    "x86_64": "x64"}[str(self.settings.arch_build)]
            name = "rubyinstaller-{}-{}".format(self.version, self.rubyinstaller_release)
            folder = "{}-{}".format(name, arch)
            url = "https://github.com/oneclick/rubyinstaller2/releases/download/{}/{}.7z".format(
                name, folder)
            tools.download(url, "ruby.7z")
            self.run("7z x {}".format("ruby.7z"))
            shutil.move(folder, "ruby")
            # Remove non-standard defaults directory
            shutil.rmtree(os.path.join("ruby", "lib", "ruby", self.api_version, "rubygems", "defaults"))
        elif tools.os_info.is_linux or tools.os_info.is_macos:
            name = tools.os_info.linux_distro or "osx"
            version = str(tools.os_info.os_version)
            url = "https://rvm.io/binaries/{}/{}/{}/ruby-{}.tar.bz2".format(
                name, version, str(self.settings.arch_build), self.version)
            tools.get(url)
            shutil.move("ruby-{}".format(self.version), "ruby")

    def package(self):
        self.copy("*", src="ruby", symlinks=True)

    def package_info(self):
        self.env_info.path.append(os.path.join(self.package_folder, "bin"))

    def package_id(self):
        if tools.os_info.is_windows:
            os_build = "Windows"
        else:
            name = tools.os_info.linux_distro or "osx"
            version = str(tools.os_info.os_version)
            os_build = "{} {}".format(name, version)
        self.info.settings.os_build = os_build
