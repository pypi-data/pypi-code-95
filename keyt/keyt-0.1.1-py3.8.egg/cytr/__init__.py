#             _
#   ___ _   _| |_ _ __
#  / __| | | | __| '__|
# | (__| |_| | |_| |
#  \___|\__, |\__|_|
#       |___/
#
# Stateless password manager/generator.
#
# Generate a password based on: username, domain and a master password.
# The intent of this program is to have a password manager/generator without
# saving any data anywhere in any form.
# The password is generated from a hash of the input data, there is never a use
# of random, with the same input you will always have the same output.
#
# The generated password is a 40 char length by default and can be changed to
# a 15 char password with the 'short-simple' option.
#
# The password is encoded in Base85, so it will contain letters, numbers and
# special characters: 0-9 a-z A-Z #$%&()*+-;<=>?@^_{|}~
# The Base85 version used in cytr remove 2 special chars: ` and ! because of
# incompatibility issues with a shell string.
# b85encode (Base85) is used instead of a85encode (Ascii85) because it contain
# special characters that may be incompatible with shell: "',./:[\]`!
#
# The 'shot-simple' version is encoded using base64 (b64encode) so will only
# contain letters and numbers: 0-9 a-z A-Z
#

__version__ = "1.4.0"
