from conan import ConanFile
from conan.errors import ConanInvalidConfiguration, ConanException
from conan.tools.files import get, copy, rmdir, load, save, rename
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.scm import Version
import os


required_conan_version = ">=1.53.0"

class AwsLambdaRuntimeConan(ConanFile):
    name = "aws-lambda-cpp"
    description = "C++ implementation of the AWS Lambda runtime"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/awslabs/aws-lambda-cpp"
    topics = ("aws", "lambda")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_backtrace": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_backtrace": False,
    }

    @property
    def _min_cppstd(self):
        return 11

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if Version(self.version) < "0.2.9":
            del self.options.with_backtrace

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libcurl/[>=7.78.0 <9]")
        if self.options.get_safe("with_backtrace", True):
            self.requires("libbacktrace/cci.20210118")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration(f"{self.ref} supports Linux only.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        dpes = CMakeDeps(self)
        dpes.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def _extract_cmake_module(self):
        cmake_module = load(self, os.path.join(self.source_folder, "cmake", "aws-lambda-runtime-config.cmake"))
        start = "set(AWS_LAMBDA_PACKAGING_SCRIPT ${CMAKE_CURRENT_LIST_DIR}/packager)"
        start_index = cmake_module.find(start)
        if start_index == -1:
            raise ConanException("Could not extract aws_lambda_package_target from aws-lambda-runtime-config.cmake file.")
        return cmake_module[start_index:]

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        save(self, os.path.join(self.package_folder, "lib", "cmake", "aws_lambda_package_target.cmake"), self._extract_cmake_module())
        rename(self, os.path.join(self.package_folder, "lib", "aws-lambda-runtime", "cmake", "packager"), os.path.join(self.package_folder, "lib", "cmake", "packager"))
        rmdir(self, os.path.join(self.package_folder, "lib", "aws-lambda-runtime"))

    def package_info(self):
        self.cpp_info.libs = ["aws-lambda-runtime"]
        self.cpp_info.builddirs.append(os.path.join("lib", "cmake"))

        self.cpp_info.set_property("cmake_file_name", "aws-lambda-runtime")
        self.cpp_info.set_property("cmake_target_name", "AWS::aws-lambda-runtime")
        self.cpp_info.set_property("cmake_build_modules", [os.path.join("lib", "cmake", "aws_lambda_package_target.cmake")])

        self.cpp_info.system_libs.append("m")
