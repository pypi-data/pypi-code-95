"""
### jQuery vulnerabilities
"""
import os
import re
import splunk_appinspect
import splunk_appinspect.check_routine.util as util

""" This function throws a warning message during app inspect if the dashboards of the app
do not have a version attribute OR have the version attribute set to a value other than 1.1

@param:
app: An app object
reporter: Reporter object """


@splunk_appinspect.tags("cloud", "jquery", "private_app")
@splunk_appinspect.cert_version(min="2.5.0")
def check_simplexml_standards_version(app, reporter):
    """Check that the dashboards in your app have a valid version attribute."""

    xml_files = list(app.get_filepaths_of_files(types=[".xml"]))
    for query_node, relative_filepath in util.get_dashboard_nodes(xml_files):
        version = query_node.get("version")
        if version is None:
            message = (
                "Change the version attribute in the root node of your Simple XML dashboard {} to "
                + "`<version=1.1>`. Earlier dashboard versions introduce security vulnerabilities "
                + "into your apps and are not permitted in Splunk Cloud"
            ).format(relative_filepath)
            reporter.fail(message, relative_filepath)
        elif (
            version.strip() == "2" or version.strip() == "1.1"
        ):  # If UDF or simple XML dashboard 1.1, continue
            continue
        else:
            message = (
                "Version attribute of the dashboard {} is set to {}.Change the version attribute "
                + "in the root node of your Simple XML dashboard to "
                + "`<version=1.1>`. Earlier dashboard versions introduce security vulnerabilities "
                + "into your apps and are not permitted in Splunk Cloud"
            ).format(relative_filepath, version)
            reporter.fail(message, relative_filepath)


""" This function throws a warning message during app inspect if the app's HTML and JS files
have unsupported imports

@param:
app: An app object
reporter: Reporter object """


@splunk_appinspect.tags("cloud", "jquery", "private_app", "future")
@splunk_appinspect.cert_version(min="2.5.0")
def check_hotlinking_splunk_web_libraries(app, reporter):
    """Check that the app files are not importing files directly from the
    search head.
    """

    js_files = list(
        app.get_filepaths_of_files(basedir="appserver/static", types=[".js"])
    )
    unpacked_js_files = util.unpack_absolute_path(js_files)

    # Get list of files from search head (disallowed_imports.json)
    disallowed_json_path = os.path.abspath(
        os.path.join(
            __file__, "../../splunk/jquery_checks_data/disallowed_imports.json"
        )
    )
    # Get list of risky imports from search head (risky_imports.json)
    risky_imports_json_path = os.path.abspath(
        os.path.join(
            __file__, "../../splunk/jquery_checks_data/risky_imports.json"
        )
    )

    with open(
        disallowed_json_path, "r", encoding="utf-8", errors="ignore"
    ) as disallowed_modules_file:
        disallowed_modules_imports = util.populate_set_from_json(
            disallowed_modules_file
        )
    with open(
        risky_imports_json_path, "r", encoding="utf-8", errors="ignore"
    ) as risky_imports_file:
        risky_modules_imports = util.populate_set_from_json(
            risky_imports_file
        )

    # Check for SH imports in all JS files
    file_list = util.validate_imports(unpacked_js_files, disallowed_modules_imports, risky_modules_imports)
    util.communicate_bad_import_message(reporter, file_list)
