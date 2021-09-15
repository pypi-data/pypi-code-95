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
def get_command():
    '''
    Run a LHCbPR job
    '''
    __author__ = 'Ben Couturier <ben.couturier@cern.ch>'

    # We first try to import from LbCommon, then revert to the old package (LbUtils)
    # if needed
    try:
        from LbCommon.Script import PlainScript as _PlainScript
    except:
        from LbUtils.Script import PlainScript as _PlainScript

    import sys
    import os
    from datetime import datetime
    from LbPR.LbPRJobManager import JobManager
    from LbNightlyTools import Configuration

    def getProjectVersionFromConfig(config, project):
        ''' Look up the project version for SetupProject '''
        retval = None
        for proj in config['projects']:
            if proj['name'].lower() == project.lower():
                retval = proj['version']
                break
        return retval

    def getSlotDateFromConfig(config):
        completed = config["completed"]
        return datetime.strptime(completed, '%Y-%m-%dT%H:%M:%S.%f')

    class Script(_PlainScript):
        '''
        Script to create the commands to run a LHCbPR Job
        '''
        __usage__ = '%prog  <command> <project> <version> <platform>' \
                    ' <options> <setup-options> <slot config>'
        __version__ = ''

        def defineOpts(self):
            '''Define options.'''
            from LbNightlyTools.Scripts.Common import addBasicOptions
            self.parser.add_option(
                '-u',
                '--url',
                action='store',
                help='URL for the LHCbPR REST service')
            self.parser.add_option(
                '-c',
                '--check-ssl',
                action='store_true',
                help='Check SSL certificate.')
            self.parser.add_option(
                '-o',
                '--output',
                action='store',
                help='output file name '
                '[default: runlhcbpr.sh]')
            addBasicOptions(self.parser)

        @staticmethod
        def interpretOptions(options, executable, app_name, app_version,
                             platform):
            if not executable:
                return options["content"]

            return executable["content"].format(
                app_name=app_name,
                app_version=app_version,
                platform=platform,
                build="$(pwd)/../build",
                options=options["content"])

        @staticmethod
        def interpretSetup(setup, app_name, app_version):
            if not setup:
                return ''

            return setup["content"].format(
                app_name=app_name, app_version=app_version)

        @staticmethod
        def interpretSetupArgs(setupcontent):
            if setupcontent:
                return "--setup-name='{setup[description]}' --setup-content='{setup[content]}'".format(
                    setup=setupcontent)
            return ""

        @staticmethod
        def interpretExecArgs(options):
            if not options:
                return ""
            return ("--exec-name='{ex[name]}' --exec-content='{ex[content]}'".
                    format(ex=options))

        def main(self):
            '''
            Main function of the script.
            '''

            # Checking the arguments
            if len(self.args) != 6:
                self.parser.error(
                    'Please specify <project> <version> <platform> '
                    '<options> <setup-options> <slot config>')
                exit(1)

            application = self.args[0]
            version = self.args[1]
            platform = self.args[2]
            job_options = self.args[3]

            # Handler | Executable
            # Handler | Executable | Setup
            testenv = self.args[4].split("|")
            executuable_options = testenv[0]
            handlers = testenv[1]
            setup_options = None if len(testenv) < 3 else testenv[2]

            slot_config = self.args[5]

            # Parsing the slot config to extract relevant information
            self.log.info("Parsing config file %s" % slot_config)
            config = Configuration.load(slot_config)
            project_version = getProjectVersionFromConfig(config, application)
            slot_completed = getSlotDateFromConfig(config)
            # print("SASHA", slot_completed)
            self.log.info("Using %s %s", application, project_version)

            # Now create the interface with LHCbPR
            manager = JobManager(self.options.url, self.options.check_ssl)
            try:
                # Get the actual options based on description
                optionscontent = manager.getJobOptions(job_options)

                # Get the actual executable
                executablecontent = manager.getExecutableOptions(
                    executuable_options)

                # Get the actual options based on description
                setupcontent = manager.getSetupOptions(setup_options)

            except Exception as exc:
                self.log.error(
                    "Could not get job description options "
                    "from LHCbPR service %s: %s", self.options.url, str(exc))
                raise exc

            runfilename = "runlhcbpr.sh"
            if self.options.output != None:
                runfilename = self.options.output

            self.log.warning("Writing file: %s", runfilename)

            try:
                with open(runfilename, 'w') as runfile:
                    # runfile.write("\n")
                    # lblogin_cmd = ". LbLogin.sh -c %s" % platform
                    setup_cmd = self.interpretSetup(
                        setup=setupcontent,
                        app_name=application,
                        app_version=project_version)
                    run_cmd = self.interpretOptions(
                        options=optionscontent,
                        executable=executablecontent,
                        app_name=application,
                        app_version=project_version,
                        platform=platform)
                    print((run_cmd, optionscontent))
                    setup_args = self.interpretSetupArgs(setupcontent)
                    exec_args = self.interpretExecArgs(executablecontent)

                    runfile.write('''
#!/usr/bin/env bash
#
# File generated by lbpr-get-command to run the LHCbPR Job
#

set -v

# Setting the CMTPROJECTPATH for the software installed locally
if [ -f build/setupSearchPath.sh ]; then
    . build/setupSearchPath.sh
fi
export User_release_area=$(pwd)/build
# Setting the environment and cleanup
OLDPATH=$PATH
{setup_cmd}
rm -f start.txt end.txt platform.txt
echo $CMTCONFIG > platform.txt

# Add valgrind from AFS to the PATH
if [ -f /afs/cern.ch/lhcb/group/rich/vol4/jonrob/scripts/new-valgrind.sh ]; then
    source /afs/cern.ch/lhcb/group/rich/vol4/jonrob/scripts/new-valgrind.sh
fi

# Adding jemalloc for the perf jobs
if [ -d /opt/dirac/lhcbpr/sw/jemalloc-3.6.0/lib ]; then
    export LD_LIBRARY_PATH=/opt/dirac/lhcbpr/sw/jemalloc-3.6.0/lib:$LD_LIBRARY_PATH
fi

# Get kerberos ticket
kinit -k -t /afs/cern.ch/user/l/lhcbpr/private/lhcbpr.keytab lhcbpr@CERN.CH

echo $LD_LIBRARY_PATH
# Now running the test itself
set -o pipefail
date +"%Y-%m-%d %T %z" > start.txt
time_start=`cat start.txt`
if [ -d output ]; then
    rm -rf output
fi
mkdir output
pushd $(pwd)
OUTPUT_PATH=output
cd $OUTPUT_PATH

# send the initial info to couchdb that the periodic test has started
log_cmd=`python - $1 $time_start << END
import sys
import os
import logging
from LbNightlyTools.Utils import Dashboard
logging.basicConfig(level=logging.DEBUG)
dash = Dashboard(credentials=None,
                    flavour='periodic')
build_id = sys.argv[2] + "_" + sys.argv[3] + "_" + sys.argv[4]
if 'BUILD_ID' in os.environ:
        build_id = os.environ.get('BUILD_ID')
doc_name = build_id + "." + sys.argv[1]
data_dict = dict()
if 'BUILD_URL' in os.environ:
    data_dict['build_url'] = os.environ.get('BUILD_URL') + '/console'
data_dict['app_name'] = '{app_name}'
data_dict['app_version'] = '{app_version}'
data_dict['opt_name'] = '{options[description]}'
data_dict['time_start'] = sys.argv[2] + "_" + sys.argv[3] + "_" + sys.argv[4]
data_dict['status'] = 'running'
data_dict['app_version_datetime'] = '{app_version_datetime}'
dash.update(doc_name, data_dict)
END`

# Set environment for throughput tests
if [[ '{handlers}' == *"Throughput"* ]] ; then
    source /cvmfs/projects.cern.ch/intelsw/psxe/linux/19-all-setup.sh
fi

if [ -z "$LHCBPR_MOCK_OUTPUT_PATH" ]
then
    {run_cmd} 2>&1 | tee run.log
else
    OUTPUT_PATH="$LHCBPR_MOCK_OUTPUT_PATH"
fi
RETCODE=$?
popd
PATH=$OLDPATH

date +"%Y-%m-%d %T %z" > end.txt
COLLECT_LOG=$OUTPUT_PATH/collect.log
echo "==> Return code: $RETCODE" | tee $COLLECT_LOG
# Gathering the results with LHCbPR

if [ "$RETCODE" = "0" ] ; then
    echo "Run OK now gathering the results" | tee -a $COLLECT_LOG
else
    echo "Non 0 return code - Will NOT gather the results" | tee -a $COLLECT_LOG
fi

# FIXME, temporal workaround for MiniBrunel-Callgrind test
if [ '{options[description]}' == 'MiniBrunel-Callgrind' ]
then
valgrindroot=/cvmfs/lhcbdev.cern.ch/tools/valgrind/3.12.0/x86_64-centos7
export PATH=$valgrindroot/bin:$PATH
export LD_LIBRARY_PATH=$valgrindroot/lib/valgrind:$LD_LIBRARY_PATH
for i in $OUTPUT_PATH/callgrind.out.*.1; do
if [ -f "$i" ]; then
callgrind_log=`ls -tr $OUTPUT_PATH/callgrind.out.*.1 | tail -1`
callgrind_annotate --inclusive=yes $callgrind_log > $callgrind_log.anno
fi
done
fi

time_end=`cat end.txt`
hostname=`hostname`
cpu_info=`lscpu | grep "^Model name:" | cut -d: -f2 | sed -e 's/^[[:space:]]*//'`
mem_info=`cat /proc/meminfo | grep MemTotal`

lbpr-collect -r $OUTPUT_PATH -s "`cat start.txt`" -e "`cat end.txt`" -p `hostname` -u "$cpu_info" -m "$mem_info" -c `cat platform.txt` --opt-content='{options[content]}' {setup_args} {exec_args} --opt-name='{options[description]}' -l '{handlers}' --app-name='{app_name}' --app-version='{app_version}'  --app-version-datetime="{app_version_datetime}" -i $1 -t $RETCODE -a | tee -a $COLLECT_LOG

# send the final info to couchdb that the periodic test has ended
log_cmd=`python - $1 $time_start $time_end $RETCODE $OUTPUT_PATH $CMTCONFIG $hostname "$cpu_info" "$mem_info"<< END
import sys
import os
import logging
import subprocess
from LbNightlyTools.Utils import Dashboard
logging.basicConfig(level=logging.DEBUG)
dash = Dashboard(credentials=None,
                    flavour='periodic')
build_id = sys.argv[2] + "_" + sys.argv[3] + "_" + sys.argv[4]
if 'BUILD_ID' in os.environ:
        build_id = os.environ.get('BUILD_ID')
doc_name = build_id + "." + sys.argv[1]
data_dict = dict()
data_dict['time_end'] = sys.argv[5] + "_" + sys.argv[6] + "_" + sys.argv[7]
data_dict['status'] = sys.argv[8]
logsDir = "logs/" + '{app_name}' + "/" + '{options[description]}' + "/" + '{app_version}' + "_" + sys.argv[2] + "_" + sys.argv[3] + "_" + sys.argv[4]
logName = os.path.join(sys.argv[9],'run.log')
eos_path = os.path.join(os.environ['LHCBPR_EOS_LOGS'], '')
targetDir = 'root://eoslhcb.cern.ch/' + eos_path + logsDir + '/run.log'
logCollectName = os.path.join(sys.argv[9],'collect.log')
targetCollectDir = 'root://eoslhcb.cern.ch/' + eos_path + logsDir + '/collect.log'
try:
    subprocess.call(['xrdcp', logName, targetDir])
    subprocess.call(['xrdcp', logCollectName, targetCollectDir])
except Exception, ex:
    logging.warning('Error copying log to eos: %s', ex)
data_dict['run_log'] = "https://eoslhcbhttp.cern.ch/" + eos_path + logsDir + "/run.log"
data_dict['collect_log'] = "https://eoslhcbhttp.cern.ch/" + eos_path + logsDir + "/collect.log"
cmtconfig_dict = dict()
host_dict = dict()
cmtconfig_dict['platform'] = sys.argv[10]
host_dict['hostname'] =  sys.argv[11]
host_dict['cpu_info'] = sys.argv[12]
host_dict['memoryinfo'] = sys.argv[13]
data_dict['CMTCONFIG'] = cmtconfig_dict
data_dict['HOST'] = host_dict
dash.update(doc_name, data_dict)
END`

exit $RETCODE
                    '''.format(
                        setup_cmd=setup_cmd,
                        run_cmd=run_cmd,
                        options=optionscontent,
                        setup_args=setup_args,
                        exec_args=exec_args,
                        handlers=handlers,
                        app_name=application,
                        app_version=version,
                        app_version_datetime=slot_completed.strftime(
                            "%Y-%m-%d %H:%M:%S -0400")))
            except Exception as exc:
                self.log.error("Error generating runfile: %s", str(exc))
                raise exc

    return Script().run()
