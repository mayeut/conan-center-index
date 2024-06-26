import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.53.0"


class QuickfastConan(ConanFile):
    name = "quickfast"
    description = "QuickFAST is an Open Source native C++ implementation of the FAST Protocol"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/objectcomputing/quickfast"
    topics = ("fast-protocol", "fast", "fix-adapted-for-streaming", "fpl", "fix-protocol-limited")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def export_sources(self):
        copy(self, "CMakeLists.txt", self.recipe_folder, os.path.join(self.export_sources_folder, "src"))
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # Uses Boost.Asio transitively
        self.requires("boost/1.85.0", transitive_headers=True, transitive_libs=True)
        self.requires("xerces-c/3.2.5")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "license.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["quickfast"]
        self.cpp_info.includedirs.append(os.path.join("include", "quickfast"))

        # Needed to keep support for deprecated placeholders in boost::bind
        self.cpp_info.defines.append("BOOST_BIND_GLOBAL_PLACEHOLDERS")

        if is_msvc(self) and not self.options.shared:
            self.cpp_info.defines.append("QUICKFAST_HAS_DLL=0")
