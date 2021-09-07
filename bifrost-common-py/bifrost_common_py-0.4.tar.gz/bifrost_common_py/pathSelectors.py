"""
* This module exports state path selectors. 
* It is part of the bifrost-common suite for module developers.
* 
* The current state version is B5 / JOTUNN-
* 
* @module selectors
* @author Ralf Mosshammer <bifrost.at@siemens.com>
* @copyright Siemens AG Austria, 2019, 2020, 2021

* Composite object containing selection functions.
* Python implementation
* @author Manuel Matzinger <manuel.matzinger@siemens.com>
"""

def domains():
    return '/domains'
def domainId(domain, id):
    return '/domains/'+str(domain)+'/byId/'+str(id)
def allDomainElements(domain):
    return '/domains/'+str(domain)+'/allElements'
def domainByPosition(domain):
    return '/domains/'+str(domain)+'/byPosition'
def domainPosition(domain, pos):
    return '/domains/'+str(domain)+'/byPosition/'+str(pos)
def domainByTypeRef(domain):
    return '/domains/'+str(domain)+'/byTypeRef'
def domainChildRefs(domain, id):
    return '/domains/'+str(domain)+'/byId/'+str(id)+'/childRefs'
def domainTypeRef(domain, id):
    return '/domains/'+str(domain)+'/byId/'+str(id)+'/typeRef'
def domainParentRefs(domain, id):
    return '/domains/'+str(domain)+'/byId/'+str(id)+'/parentRefs'
def domainDynamicRefs(domain, id):
    return '/domains/'+str(domain)+'/byId/'+str(id)+'/dynamicRefs'
def domainPositionOfId(domain, id):
    return '/domains/'+str(domain)+'/byId/'+str(id)+'/position'
def domain(domain):
    return '/domains/'+str(domain)+'/'

def meta():
    return '/meta'
def settlementId():
    return '/meta/id'
def settlementHash():
    return '/meta/settlementHash'
def settlementName():
    return '/meta/name'
def settlementDescription():
    return '/meta/description'
def domainHash():
    return '/meta/domainHash'
def dynamicHash():
    return '/meta/dynamicHash'
def valueHash():
    return '/meta/valueHash'
def scenarioHash():
    return '/meta/scenarioHash'
def transientHash():
    return '/meta/transientHash'
def structuralHash():
    return '/meta/structuralHash'
def previewImage():
    return '/meta/preview'
def qOriginal():
    return '/meta/qOriginal'
def qEntangledWith():
    return '/metaq/EntangledWith'

def runsById():
    return '/meta/runsById'
def runId(runId):
    return '/meta/runsById/'+str(runId)
def allRuns():
    return '/meta/allRuns'
def timeHorizon(runId):
    return '/meta/runsById/'+str(runId)+'/timeHorizon'
def startTime(runId):
    return '/meta/runsById/'+str(runId)+'/startTime'
def prefetchStep(runId):
    return '/meta/runsById/'+str(runId)+'/prefetchStep'
def runComplete(runId):
    return '/meta/runsById/'+str(runId)+'/complete'
def runPersisted(runId):
    return '/meta/runsById/'+str(runId)+'/persisted'
def runHistoric(runId):
    return '/meta/runsById/'+str(runId)+'/historic'
def runScenarioHash(runId):
    return '/meta/runsById/'+str(runId)+'/scenarioHash'
def currentRunId():
    return '/meta/currentRunId'

def dominion():
    return '/domains/dominion'
def dominionId(id):
    return '/domains/dominion/byId/'+str(id)

def landscape():
    return '/domains/landscape'
def landscapeId(id):
    return '/domains/landscape/byId/'+str(id)
def landscapeDynamicRefs(id):
    return '/domains/landscape/byId/'+str(id)+'/dynamicRefs'
def landscapeFlavors(id):
    return '/domains/landscape/byId/'+str(id)+'/flavor'
def landscapeTypeRef(id):
    return '/domains/landscape/byId/'+str(id)+'/typeRef'
def allLandscapeElements():
    return '/domains/landscape/allElements'

def powergrid():
    return '/domains/powergrid'
def powergridId(id):
    return '/domains/powergrid/byId/'+str(id)
def powergridElementRefs(id):
    return '/domains/powergrid/byId/'+str(id)+'/elementRefs'
def powergridParentRefs(id):
    return '/domains/powergrid/byId/'+str(id)+'/parentRefs'
def powergridChildRefs(id):
    return '/domains/powergrid/byId/'+str(id)+'/childRefs'
def powergridDynamicRefs(id):
    return '/domains/powergrid/byId/'+str(id)+'/dynamicRefs'
def powergridTypeRef(id):
    return '/domains/powergrid/byId/'+str(id)+'/typeRef'
def allPowergridElements():
    return '/domains/powergrid/allElements'

def datagrid():
    return '/domains/datagrid'
def datagridId(id):
    return '/domains/datagrid/byId/'+str(id)
def datagridDynamicRefs(id):
    return '/domains/datagrid/byId/'+str(id)+'/dynamicRefs'
def allDatagridElements():
    return '/domains/datagrid/allElements'

def thermogrid():
    return '/domains/thermogrid/'
def thermogridId(id):
    return '/domains/thermogrid/byId/'+str(id)
def thermogridDynamicRefs(id):
    return '/domains/thermogrid/byId/'+str(id)+'/dynamicRefs'
def allThermogridElements():
    return '/domains/thermogrid/allElements'

def dynamics():
    return '/dynamics'
def allDynamics():
    return '/dynamics/allElements'
def allStickyDynamics():
    return '/dynamics/allStickyElements'
def dynamicId(id):
    return '/dynamics/byId/'+str(id)
def dynamicValue(id):
    return '/dynamics/byId/'+str(id)+'/value'
def dynamicTypeRef(id):
    return '/dynamics/byId/'+str(id)+'/typeRef'
def dynamicParentRefs(id):
    return '/dynamics/byId/'+str(id)+'/parentRefs'
def dynamicChildRef(id):
    return '/dynamics/byId/'+str(id)+'/childRef'
def dynamicsByTypeRef():
    return '/dynamics/byTypeRef'

def collections():
    return '/collections'
def collectionId(id):
    return '/collections/byId/'+str(id)
def collectionElements(id):
    return '/collections/byId/'+str(id)+'/elements'
def allCollections():
    return '/collections/allElements'

def simulation():
    return '/simulation'
def simulationRunning():
    return '/simulation/control/running'
def simulationPrefetching():
    return '/simulation/control/prefetching'
def simulationReplayPointer():
    return '/simulation/time/replayPointer'
def simulationPrefetchPointer():
    return '/simulation/time/prefetchPointer'
def simulationLoopDuration():
    return '/simulation/time/loopDuration'
def simulationStep():
    return '/simulation/time/simulationStep'
def simulationTimeWindowLeft():
    return '/simulation/time/timeWindowLeft'
def simulationTimeWindowRight():
    return '/simulation/time/timeWindowRight'
def simulationSlowModeSince():
    return '/simulation/time/slowModeSince'

def modules():
    return '/modules'
def moduleInitURL(id):
    return '/modules/byId/'+str(id)+'/initURL'
def moduleUpdateURL(id):
    return '/modules/byId/'+str(id)+'/updateURL'
def moduleConfigURL(id):
    return '/modules/byId/'+str(id)+'/configURL'
def moduleFrontendURL(id):
    return '/modules/byId/'+str(id)+'/frontendURL'
def moduleRestURL(id):
    return '/modules/byId/'+str(id)+'/restURL'
def modulePreviewURL(id):
    return '/modules/byId/'+str(id)+'/previewURL'
def moduleLogURL(id):
    return '/modules/byId/'+str(id)+'/logURL'
def moduleInitParams(id):
    return '/modules/byId/'+str(id)+'/initParameters'
def moduleUpdateParams(id):
    return '/modules/byId/'+str(id)+'/updateParameters'
def moduleId(id):
    return '/modules/byId/'+str(id)
def moduleEnabled(id):
    return '/modules/byId/'+str(id)+'/enabled'
def moduleInitialized(id):
    return '/modules/byId/'+str(id)+'/initialized'
def moduleSamplingRate(id):
    return '/modules/byId/'+str(id)+'/samplingRate'
def moduleSubs(id):
    return '/modules/byId/'+str(id)+'/subscriptions'
def modulesOfHook(hook):
    return '/modules/byHook/'+str(hook)
def allModules():
    return '/modules/allElements/'
def enabledModules():
    return '/modules/allEnabledModules/'
def modulesByHook():
    return '/modules/byHook/'

def macros():
    return '/macros'

def events():
    return '/events'
def eventId(id):
    return '/events/byId/'+str(id)
def eventParentRef(id):
    return '/events/byId/'+str(id)+'/parentRef'
def eventName(id):
    return '/events/byId/'+str(id)+'/name'
def eventCommands(id):
    return '/events/byId/'+str(id)+'/commands'
def eventTriggers(id):
    return '/events/byId/'+str(id)+'/triggers'
def allEvents():
    return '/events/allElements'

def annotations():
    return '/annotations'
def annotationId(id):
    return '/annotations/byId/'+str(id)
def annotationType(id):
    return '/annotations/byId/'+str(id)+'/type'
def annotationName(id):
    return '/annotations/byId/'+str(id)
def annotationValue(id):
    return '/annotations/byId/'+str(id)+'/value'
def annotationChildRefs(id):
    return '/annotations/byId/'+str(id)+'/childRefs'
def annotationParentRefs(id):
    return '/annotations/byId/'+str(id)+'/parentRefs'
def allAnnotations():
    return '/annotations/allElements'

def widgets():
    return '/widgets'
def widgetId(id):
    return '/widgets/byId/'+str(id)
def widgetParentRef(id):
    return '/widgets/byId/'+str(id)+'/parentRef'
def allWidgets():
    return '/widgets/allElements'

def ui():
    return '/ui'
def visibleDynamics():
    return '/ui/visibleDynamics'
def uiEvents():
    return '/ui/events'
def lastEvent():
    return '/ui/events/lastEvent'

def directoryRoot():
    return '/directory'
def directoryMeta():
    return '/directory/meta'
def _directoryMeta():
    return '/meta'
def directoryHash():
    return '/directory/meta/hash'
def directoryPatches():
    return '/directory/meta/appliedPatches'
def directoryDeferredOps():
    return '/directory/meta/deferredOps'
def _directoryDeferredOps():
    return '/meta/deferredOps'
def directoryStructures():
    return '/directory/structures'
def directoryStructuresDomain(domain):
    return '/directory/structures/byDomain/'+str(domain)
def directoryStructuresType(type):
    return '/directory/structures/byType/'+str(type)
def directoryStructureSize(type):
    return '/directory/structures/byType/'+str(type)+'/size'
def directoryDynamics():
    return '/directory/dynamics'
def directoryDynamicsByDomain():
    return '/directory/dynamics/byDomain'
def dynamicType(type):
    return '/directory/dynamics/byType/'+str(type)
def structureType(type):
    return '/directory/structures/byType/'+str(type)
def nodeType():
    return 'GRID-NODE'
