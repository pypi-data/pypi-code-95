# noqa
import pkg_resources

NAME = 'evmscript_parser'
CLI_NAME = 'evmscript-parser'

try:
    version = pkg_resources.get_distribution(NAME).version
except pkg_resources.DistributionNotFound:
    version = 'v0.0.0'
