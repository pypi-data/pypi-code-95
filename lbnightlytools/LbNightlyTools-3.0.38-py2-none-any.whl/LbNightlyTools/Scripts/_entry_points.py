###############################################################################
# (c) Copyright 2013-2020 CERN                                                #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
def ansi2html():
    '''
    Script to convert a console output to html.
    '''
    import os
    from LbNightlyTools.HTMLUtils import convertFile
    from optparse import OptionParser

    parser = OptionParser(usage='%prog [options] <input> <output>')

    try:
        opts, (input, output) = parser.parse_args()
    except ValueError:
        parser.error('wrong number of arguments')

    return convertFile(input, output)


def build_log_to_html():
    '''
    Collect the build logs produced by lbn-wrapcmd and write the content grouped by
    subdir and target.
    '''
    from LbNightlyTools.Scripts.CollectBuildLogs import LogToHTML as Script
    return Script().run()


def check_preconditions():
    from LbNightlyTools.CheckSlotPreconditions import Script
    return Script().run()


def collect_build_logs():
    '''
    Collect the build logs produced by lbn-wrapcmd and write the content grouped by
    subdir and target.
    '''
    from LbNightlyTools.Scripts.CollectBuildLogs import Script
    return Script().run()


def enabled_slots():
    from LbNightlyTools.Scripts.EnabledSlots import Script
    return Script().run()


def generate_compatspec():
    from LbRPMTools.LHCbCompatSpecBuilder import Script
    return Script().run()


def generate_do0spec():
    #
    # Little tool to generate -do0 RPM spec while we have a problem in the RPM generation.
    #
    # To find the list of LCG_XX_[...]dbg rpms from the LCG repo for e.g. LCG_79 do:
    # for f in  /afs/cern.ch/sw/lcg/external/rpms/lcg/LCG_79_*; do basename $f \
    # | sed -e 's/-79.noarch.rpm//' | sed -e 's/1.0.0//' | grep dbg; done
    #
    # You have have a lits of entries like: LCG_79_yoda_1.3.1_x86_64_slc6_gcc49_dbg
    # N.b. the RPM version ahs been removed !
    #
    # On each of them run:
    # lbn-generate-do0spec <name> && rpmbuild -bb tmp.spec

    import sys
    import logging

    # First checking args
    if len(sys.argv) == 1:
        logging.error("Please specify RPM name")
        sys.exit(2)

    rpmname = sys.argv[1]

    if rpmname.find("dbg") == -1:
        logging.error(
            "RPM is not in dbg config, cannot create meta for do0 version")
        sys.exit(2)

    do0name = rpmname.replace("dbg", "do0")
    logging.warning(
        "Generating tmp.spec for %s depending on %s" % (do0name, rpmname))

    # Now generating the spec
    from subprocess import call
    call(
        ["lbn-generate-metaspec", "-o", "tmp.spec", do0name, "1.0.0", rpmname])


def generate_extspec():
    from LbRPMTools.LHCbExternalsSpecBuilder import Script
    return Script().run()


def generate_genericspec():
    from LbRPMTools.LHCbGenericSpecBuilder import GenericScript
    return GenericScript().run()


def generate_lbscriptsspec():
    from LbRPMTools.LHCbLbScriptsSpecBuilder import Script
    return Script().run()


def generate_metaspec():
    from LbRPMTools.LHCbMetaSpecBuilder import MetaScript
    return MetaScript().run()


def generate_spec():
    from LbRPMTools.LHCbRPMSpecBuilder import Script
    return Script().run()


def gen_release_config():
    from LbNightlyTools.Scripts.Release import ConfigGenerator as Script
    return Script().run()


def index():
    from LbNightlyTools.Scripts.Index import Script
    return Script().run()


def install():
    from LbNightlyTools.Scripts.Install import Script
    return Script().run()


def list_platforms():
    '''
    Simple script to extract the list of requested platforms from the slot
    configuration file.
    '''
    __author__ = 'Marco Clemencic <marco.clemencic@cern.ch>'

    import os
    import sys
    from LbNightlyTools.Configuration import findSlot

    usage = 'Usage: %s configuration_file' % os.path.basename(sys.argv[0])

    if '-h' in sys.argv or '--help' in sys.argv:
        print usage
        sys.exit(0)

    if len(sys.argv) != 2:
        print >> sys.stderr, usage
        sys.exit(1)

    print ' '.join(findSlot(sys.argv[1]).platforms)


def preconditions():
    from LbNightlyTools.Scripts.Preconditions import Script
    return Script().run()


def release_poll():
    from LbNightlyTools.Scripts.Release import Poll as Script
    return Script().run()


def release_trigger():
    from LbNightlyTools.Scripts.Release import Starter as Script
    return Script().run()


def reschedule_tests():
    '''
    Query the results database to find missing tests and produce the
    expected_builds.json file needed to re-schedule them.
    '''
    from LbNightlyTools import Dashboard
    from LbNightlyTools.Scripts.Common import addDashboardOptions

    from datetime import date
    import time
    import json

    # Parse command line
    from optparse import OptionParser
    parser = OptionParser(description=__doc__)

    parser.add_option(
        '--day',
        action='store',
        help='day to check as yyyy-mm-dd (default: today)',
        default=str(date.today()))
    parser.add_option(
        '-o',
        '--output',
        action='store',
        help='output file name [default: standard output]')
    addDashboardOptions(parser)

    opts, args = parser.parse_args()

    if args:
        parser.error('unexpected arguments')

    # Initialize db connection
    dashboard = Dashboard(
        credentials=None,
        flavour=opts.flavour,
        server=opts.db_url,
        dbname=opts.db_name or Dashboard.dbName(opts.flavour))

    # Prepare data
    day_start = time.mktime(time.strptime(opts.day, '%Y-%m-%d'))
    expected_builds = []

    def expected_build_info(slot, project, platform, timestamp):
        from os.path import join
        version = None
        for p in slot['projects']:
            if project == p['name'] and not p.get('no_test'):
                version = p['version']
                break
        else:
            # cannot find the project in the slot or the project is not tested
            return None
        build_id = str(slot['build_id'])
        filename = join(
            'artifacts', opts.flavour, slot['slot'], build_id, '.'.join(
                [project, version, slot['slot'], build_id, platform, 'zip']))
        return [
            filename, slot['slot'], slot['build_id'], project, platform,
            timestamp,
            platform.split('-')[1]
        ]

    for row in dashboard.db.iterview(
            'summaries/byDay', batch=100, key=opts.day, include_docs=True):
        slot_name = row.doc['slot']
        build_id = row.doc['build_id']

        for platform in row.doc['config']['platforms']:
            builds = set()
            tests = set()
            started = day_start
            if platform in row.doc['builds']:
                builds.update(
                    p for p in row.doc['builds'][platform] if p != 'info'
                    and 'completed' in row.doc['builds'][platform][p])
                started = row.doc['builds'][platform]['info']['started']
            if platform in row.doc['tests']:
                tests.update(p for p in row.doc['tests'][platform]
                             if 'completed' in row.doc['builds'][platform][p])
            expected_builds.extend(
                expected_build_info(row.doc['config'], project, platform,
                                    started) for project in builds - tests)

    if opts.output:
        import codecs
        json.dump(
            expected_builds, codecs.open(opts.output, 'w', 'utf-8'), indent=2)
    else:
        print json.dumps(expected_builds, indent=2)


def rpm():
    from LbRPMTools.PackageSlot import Script
    return Script().run()


def rpm_validator():
    '''
    Command line client that interfaces to the YUMChecker class

    :author: Stefan-Gabriel Chitic
    '''
    import logging
    import optparse
    import os
    import sys
    import traceback
    import tempfile
    import json
    from lbinstall.YumChecker import YumChecker

    # Class for known install exceptions
    ###############################################################################

    class LHCbRPMReleaseConsistencyException(Exception):
        """ Custom exception for lb-install

        :param msg: the exception message
        """

        def __init__(self, msg):
            """ Constructor for the exception """
            # super( LHCbRPMReleaseConsistencyException, self).__init__(msg)
            Exception.__init__(self, msg)

    # Classes and method for command line parsing
    ###############################################################################

    class LHCbRPMReleaseConsistencyOptionParser(optparse.OptionParser):
        """ Custom OptionParser to intercept the errors and rethrow
        them as LHCbRPMReleaseConsistencyExceptions """

        def error(self, msg):
            """
            Arguments parsing error message exception handler

            :param msg: the message of the exception
            :return: Raises LHCbRPMReleaseConsistencyException with the exception message
            """
            raise LHCbRPMReleaseConsistencyException(
                "Error parsing arguments: " + str(msg))

        def exit(self, status=0, msg=None):
            """
            Arguments parsing error message exception handler

            :param status: the status of the application
            :param msg: the message of the exception
            :return: Raises LHCbRPMReleaseConsistencyException with the exception message
            """
            raise LHCbRPMReleaseConsistencyException(
                "Error parsing arguments: " + str(msg))

    class LHCbRPMReleaseConsistencyClient(object):
        """ Main class for the tool """

        def __init__(self,
                     configType,
                     arguments=None,
                     dry_run=False,
                     prog=" LHCbRPMReleaseConsistency"):
            """ Common setup for both clients """
            self.configType = configType
            self.log = logging.getLogger(__name__)
            self.arguments = arguments
            self.checker = None
            self.prog = prog

            parser = LHCbRPMReleaseConsistencyOptionParser(
                usage=usage(self.prog))
            parser.add_option(
                '-d',
                '--debug',
                dest="debug",
                default=False,
                action="store_true",
                help="Show debug information")
            parser.add_option(
                '--info',
                dest="info",
                default=False,
                action="store_true",
                help="Show logging messages with level INFO")
            parser.add_option(
                '--build-folder',
                dest="buildfolder",
                default='/data/archive/artifacts/release/'
                'lhcb-release/',
                action="store",
                help="Add custom folder for builds")
            parser.add_option(
                '--repo-url',
                dest="repourl",
                default='https://cern.ch/lhcb-nightlies-artifacts/'
                'release/lhcb-release/',
                action="store",
                help="Add custom repo url")
            parser.add_option(
                '--no-details',
                dest="nodetails",
                default=False,
                action="store_true",
                help="Displays only the name of"
                " the missing packages.")
            self.parser = parser

        def main(self):
            """ Main method for the ancestor:
            call parse and run in sequence

            :returns: the return code of the call
            """
            rc = 0
            try:
                opts, args = self.parser.parse_args(self.arguments)
                # Checkint the siteroot and URL
                # to choose the siteroot
                self.siteroot = tempfile.gettempdir()

                # Now setting the logging depending on debug mode...
                if opts.debug or opts.info:
                    logging.basicConfig(format="%(levelname)-8s: "
                                        "%(funcName)-25s - %(message)s")
                    if opts.info:
                        logging.getLogger().setLevel(logging.INFO)
                    else:
                        logging.getLogger().setLevel(logging.DEBUG)

                self.buildfolder = opts.buildfolder
                self.repourl = opts.repourl

                # Getting the function to be invoked
                self.run(opts, args)

            except LHCbRPMReleaseConsistencyException as lie:
                print >> sys.stderr, "ERROR: " + str(lie)
                self.parser.print_help()
                rc = 1
            except:
                print >> sys.stderr, "Exception in lb-install:"
                print >> sys.stderr, '-' * 60
                traceback.print_exc(file=sys.stderr)
                print >> sys.stderr, '-' * 60
                rc = 1
            return rc

        def run(self, opts, args):
            """ Main method for the command

            :param opts: The option list
            :param args: The arguments list
            """
            # Parsing first argument to check the mode

            # Setting up repo url customization
            # By default repourl is none, in which case the hardcoded default
            # is used skipConfig allows returning a config with the LHCb
            # repositories

            from lbinstall.LHCbConfig import Config
            conf = Config(self.siteroot)
            local_url = "%s" % (self.repourl)
            local_folder = "%s" % (self.buildfolder)
            conf.repos["local_repo"] = {"url": local_url}
            rpm_list = [
                f for f in os.listdir(local_folder) if f.endswith('.rpm')
            ]

            self.checker = YumChecker(
                siteroot=self.siteroot,
                config=conf,
                strict=True,
                simple_output=opts.nodetails)
            platform = args[0]
            packages = []
            tmp_platform = platform.replace('-', '_')
            for rpm in rpm_list:
                if tmp_platform not in rpm:
                    continue
                tmp = rpm.split('-')
                if len(tmp) > 0:
                    name = tmp[0]
                    name = name.replace('+', '\+')
                else:
                    raise Exception("No packages found")
                if len(tmp) > 1:
                    version = tmp[1]
                    vaersion = version.split('.')[0]
                else:
                    version = None
                if len(tmp) > 2:
                    release = tmp[2]
                    release = release.split('.')[0]
                else:
                    release = None

                packages.extend(self.checker.queryPackages(name, None, None))
            for rpmname, version, release in packages:
                self.log.info("Checking consistency for: %s %s %s" %
                              (rpmname, version, release))
            json_file = os.path.join(local_folder, 'build', platform,
                                     'RPMs_report.json')
            res = self.checker.getMissingPackgesFromTuples(
                packages, force_local=True)
            new_data = {}
            for missing in res:
                req = missing['dependency']
                req_name = "%s.%s.%s" % (req.name, req.version, req.release)
                p = missing['package']
                p_name = "%s.%s.%s" % (p.name, p.version, p.release)
                if not new_data.get(p_name, None):
                    new_data[p_name] = []
                new_data[p_name].append(req_name)
            if not os.path.isdir(os.path.dirname(json_file)):
                os.makedirs(os.path.dirname(json_file))
            with open(json_file, 'w') as outfile:
                new_data = {'missing_dependencies': new_data}
                json.dump(new_data, outfile)

    ###############################################################################
    def usage(cmd):
        """ Prints out how to use the script...

        :param cmd: the command executed
        """
        cmd = os.path.basename(cmd)
        return """\n%(cmd)s - '

    It can be used in the following way:

    %(cmd)s [build_id]
    Verifies the consistency of RPM(s) from the yum repository for all the releases
    in the build id.

    """ % {
            "cmd": cmd
        }

    def LHCbRPMReleaseConsistency(configType="LHCbConfig", prog="lbyumcheck"):
        """
        Default caller for command line LHCbRPMReleaseConsistency client
        :param configType: the configuration used
        :param prog: the name of the executable
        """

        logging.basicConfig(format="%(levelname)-8s: %(message)s")
        logging.getLogger().setLevel(logging.WARNING)
        return LHCbRPMReleaseConsistencyClient(configType, prog=prog).main()

    # Main just chooses the client and starts it
    return LHCbRPMReleaseConsistency()


def slots_by_deployment():
    import sys
    import logging
    from LbNightlyTools.Scripts.Common import PlainScript
    from LbNightlyTools.Configuration import loadConfig

    CONF_ZIP_URL = ('https://gitlab.cern.ch/lhcb-core/LHCbNightlyConf/'
                    'repository/archive.zip?ref={0}')

    def getSlotsFromGit(branch='master'):
        '''
        Helper to get the list of slots defined on the repository.
        '''
        from LbNightlyTools.Utils import TemporaryDir
        from urllib import urlretrieve
        from zipfile import ZipFile
        import os
        with TemporaryDir(chdir=True):
            url = CONF_ZIP_URL.format(branch)
            logging.debug('getting config files from %s', url)
            urlretrieve(url, 'config.zip')
            logging.debug('unpacking')
            z = ZipFile('config.zip')
            z.extractall()
            return loadConfig(z.namelist()[0])

    class Script(PlainScript):
        '''
        Simple script to get the list of slots by deployment key.
        '''
        __usage__ = '%prog [options] deployment_type ...'

        def defineOpts(self):
            '''
            Prepare the option parser.
            '''
            self.parser.add_option(
                '--branch',
                help='branch of the configuration to use '
                '[default: %default]')
            self.parser.add_option(
                '--configdir',
                help='use configuration from the given '
                'directory instead of from gitlab')
            self.parser.set_defaults(branch='master')

        def main(self):
            deployments = set(map(str.lower, self.args))
            if not deployments:
                self.parser.error(
                    'you must specify at least one deployment type')
            slots = (loadConfig(self.options.configdir)
                     if self.options.configdir else getSlotsFromGit(
                         self.options.branch))
            print('\n'.join(
                name for name, slot in sorted(slots.items()) if slot.enabled
                and deployments.intersection(map(str.lower, slot.deployment))))

    return Script().run()


def test_poll():
    from LbNightlyTools.Scripts.Test import Poll as Script
    return Script().run()


def lbq_builddone():
    '''
    Send the message that a build for a project has been done
    '''
    __author__ = 'Ben Couturier <ben.couturier@cern.ch>'

    import sys
    import LbMsg.BuildMsg
    from LbNightlyTools.Scripts.Common import PlainScript

    class Script(PlainScript):
        '''
        Sends the message that a build has been done
        '''
        __usage__ = '%prog <slot> <project> <config> <buildId>'
        __version__ = ''

        def main(self):
            '''
            Main function of the script.
            '''
            # Checking the arguments
            if len(self.args) != 4:
                self.log.error(
                    'Please specify <slot> <project> <config> <buildId>')
                exit(1)

            slot = self.args[0]
            project = self.args[1]
            config = self.args[2]
            buildId = self.args[3]

            msg = LbMsg.BuildMsg.NightliesMessenger()
            msg.sendBuildDone(slot, project, config, buildId)

    return Script().run()


def lbq_buildnotif():
    '''
    Receive messages that a build for a project has been done
    '''
    __author__ = 'Ben Couturier <ben.couturier@cern.ch>'

    import sys
    import LbMsg.BuildMsg
    from LbNightlyTools.Scripts.Common import PlainScript

    class Script(PlainScript):
        '''
        Sends the message that a build has been done
        '''
        __usage__ = '%prog <slot> <project> <config> <buildId>'
        __version__ = ''

        def defineOpts(self):
            '''
            Options specific to this script.
            '''
            self.parser.add_option(
                '-q',
                '--queue',
                default=None,
                help='Name of the (persistent) queue to store the messages')
            self.parser.add_option(
                '-b',
                '--bindings',
                default=None,
                help='Message bindings for this channel')

            self.parser.add_option(
                '-c',
                '--consume',
                action="store_true",
                default=False,
                help='Wait and loop on all messages coming from the server')

        def main(self):
            '''
            Main function of the script.
            '''

            queueName = None
            if self.options.queue:
                queueName = self.options.queue

            binds = None
            if self.options.bindings:
                binds = [self.options.bindings]

            msg = LbMsg.BuildMsg.NightliesMessenger()
            if self.options.consume:

                def callback(ch, method, properties, body):
                    print(" [x] %r:%r" % (method.routing_key, body))

                msg.consumeBuildsDone(callback, queueName, binds)
            else:
                if queueName == None:
                    raise Exception(
                        "No point in just getting messages on a newly created queue. Name the queue with -q or use -c instead"
                    )
                msg.getBuildsDone(queueName, binds)

    return Script().run()


def lbq_getteststorun():
    '''
    Request for a periodic test to be run
    '''
    __author__ = 'Ben Couturier <ben.couturier@cern.ch>'

    import sys
    import LbMsg.TestMsg
    from LbNightlyTools.Scripts.Common import PlainScript
    from LbNightlyTools.Utils import JenkinsTest
    from lbmessaging.exchanges.PeriodicTestsExchange import PeriodicTestsExchange
    from lbmessaging.exchanges.Common import check_channel, get_connection

    class Script(PlainScript):
        '''
        Sends the message that a build has been done
        '''
        __usage__ = '%prog'
        __version__ = ''

        def defineOpts(self):
            '''Define options.'''
            from LbNightlyTools.Scripts.Common import addBasicOptions

            self.parser.add_option(
                '-q',
                '--queue',
                action='store',
                default=None,
                help='Persistent queue in which to store the messages')
            self.parser.add_option(
                '-j',
                '--jenkins',
                action='store_true',
                default=False,
                help='Stote the jobs to run in Jenkins format')
            addBasicOptions(self.parser)

        def main(self):
            '''
            Main function of the script.
            '''

            queueName = None
            if self.options.queue:
                queueName = self.options.queue

            # Initializing the messenger and getting the actual list
            if queueName == None:
                raise Exception('No point in just getting messages '
                                'on a newly created queue. '
                                'Name the queue with -q')

            channel = check_channel(get_connection())
            broker = PeriodicTestsExchange(channel)
            testsToRun = broker.get_tests_to_run(queueName)

            # Printing out or creating out files
            format = "test-params-{0}.txt"
            idx = 0

            for testToRun in testsToRun:
                # Just printing out CSV by default
                if not self.options.jenkins:
                    # In this case the callback just prints the message
                    print testToRun
                else:
                    # Here we writeout the files for Jenkins
                    self.log.warning(
                        "Job %d: %s" % (idx, ", ".join(testToRun.body)))
                    jenkins_test = JenkinsTest(
                        testToRun.body.slot, testToRun.body.build_id,
                        testToRun.body.project, testToRun.body.platform,
                        testToRun.body.os_label, testToRun.body.group,
                        testToRun.body.runner, testToRun.body.env)
                    with open(format.format(idx), 'w') as paramfile:
                        paramfile.writelines(jenkins_test.getParameterLines())
                        paramfile.writelines("tests_node=" +
                                             testToRun.body.os_label)
                        self.log.warning(format.format(idx))
                    idx += 1

    return Script().run()


def lbq_requesttest():
    '''
    Request for a periodic test to be run
    '''
    __author__ = 'Ben Couturier <ben.couturier@cern.ch>'

    import sys
    import LbMsg.TestMsg
    from LbNightlyTools.Scripts.Common import PlainScript

    class Script(PlainScript):
        '''
        request for a periodic test run to be done
        '''
        __usage__ = '%prog <slot> <buildId> <project> <config> <group> <env>'
        __version__ = ''

        def defineOpts(self):
            '''Define options.'''
            from LbNightlyTools.Scripts.Common import addBasicOptions

            self.parser.add_option(
                '-r',
                '--runner',
                action='store',
                default="lhcbpr",
                help='Runner to be used for the periodic tests')
            self.parser.add_option(
                '-l',
                '--os_label',
                action='store',
                default="perf",
                help='OS Label for the test to be run on Jenkins')

            addBasicOptions(self.parser)

        def main(self):
            '''
            Main function of the script.
            '''

            # Checking the arguments
            if len(self.args) != 6:
                self.log.error(
                    'Please specify <slot> <buildid> <project> <config> '
                    '<group> <env>. For example: lbq-requesttest 1467 '
                    'lhcb-sim09  Gauss x86_64-slc6-gcc49-opt '
                    '"GAUSS-RADLENGTHSCAN" "lb-run|RadLengthHandler"')
                exit(1)

            slot = self.args[0]
            buildId = self.args[1]
            project = self.args[2]
            config = self.args[3]
            group = self.args[4]
            env = self.args[5]

            msg = LbMsg.TestMsg.TestMessenger()
            msg.requestTest(slot, buildId, project, config, group, env,
                            self.options.runner, self.options.os_label)

    return Script().run()
