#!/usr/bin/env python


from bincrafters import build_template_installer
from bincrafters import build_shared
import os

if __name__ == "__main__":

    arch = os.environ["ARCH"]
    builder = build_template_installer.get_builder()
    builder.add({"os_build" : build_shared.get_os(), "arch_build" : arch}, {}, {}, {})
    builder.run()
