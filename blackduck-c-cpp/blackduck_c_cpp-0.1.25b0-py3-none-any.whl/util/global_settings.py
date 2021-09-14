import re

so_pattern = re.compile(r".*\.so$|.*\.so\..+$")
a_pattern = re.compile(r".*\.a$|.*\.a\..+$")
o_pattern = re.compile(r".*\.o$|.*\.o\..+$")
obj_pattern = re.compile(r".*\.obj$|.*\.obj\..+$")
cpp_pattern = re.compile(r".*\.cpp$|.*\.cpp\..+$")
c_pattern = re.compile(r".*\.c$|.*\.c\..+$")
hpp_pattern = re.compile(r".*\.hpp$|.*\.hpp\..+$")
h_pattern = re.compile(r".*\.h$|.*\.h\..+$")
dll_pattern = re.compile(r".*\.dll$|.*\.dll\..+$")
lib_pattern = re.compile(r".*\.lib|.*\.lib\..+$")

cplusplus_pattern = re.compile(r".*EXECUTING: .*\Sc\+\+ ")
gplusplus_pattern = re.compile(r".*EXECUTING: .*\Sg\+\+ ")
cc_pattern = re.compile(r".*EXECUTING: .*\Scc ")
gcc_pattern = re.compile(r".*EXECUTING: .*\Sgcc ")
ld_pattern = re.compile(r".*EXECUTING: .*\Sld ")
mvsc_link_pattern = re.compile(r".*MSVC_LINK_INVOCATION=LINK.EXE")
mvsc_cl_pattern = re.compile(r".*MSVC_LINK_INVOCATION=CL.EXE")
compl_non_mtch_ptrn_1 = re.compile(r".* -c .*")
compl_non_mtch_ptrn_2 = re.compile(r".* -E .*")

