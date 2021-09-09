
from enum import Enum


class ErrorCode(Enum):
    OtherExceptionNotCaught = -2147483648
    InstallFailure = -2147023293
    ErrorUnknownProduct = -2147023291
    RebootRequired = -2147021886
    AccessDenied = -1073741819
    SemaphoreNotFound = -1073741637
    DiskResourcesExhausted = -1073741510
    DeviceNoResources = -1073741502
    InvalidHwProfile = -1073741205
    JavaHeapSizeError = -805306369
    ExceptionFromCOM = -532459699
    RunningSixtyFourOnThirtyTwo = -107374150
    RemotingException = -1001
    CorruptFileException = -1000
    InstallCompleteNoErrors = 0
    ErrorWithAccessControlOrInstallDll = 1
    ServiceStopFailed = 2
    FailedToCleanInstallDirectory = 3
    FailedToCreateInstallDirectory = 4
    DeltaInstallProcessReturnedError = 10
    DeltaProcessInstallFailed = 11
    DeltaProcessStartFailed = 12
    CreateServiceFailed = 13
    GetVersionFromSiEInstallerFile = 30
    FailToDeleteDataCollection = 31
    FailedToDeleteODXEditor = 32
    InstallSontheimFromComponents = 33
    OverridesComponentsFolder = 34
    DataCollectionFolderNotFound = 35
    OverridesFromComponentsToODXEditor = 36
    RegisterCPlusPlusDLLsForCOM = 38
    RegisterDotNetDLLsForTLB = 39
    RegisterDotNetDLLsForCodebase = 40
    FailedToSetAccessControlOnRegistry = 90
    SettingAccessControlForAppData = 91
    SettingAccessControlForEDTProgramFiles = 92
    FailedToSetAccessControlOnFiles = 93
    FailedToCreateRegistryKey = 94
    FailedToGenerateACLPaths = 95
    FailedToInstallPlugInsForMaster = 96
    FailedToSyncGlobals = 97
    DeltaMismatch = 200
    OperatingSystemNotSupported = 303
    EDTInUse = 304
    EDTBusy = 306
    PreviousVersionDoesNotMatchExpected = 200
    ThirdPartyComponentsFailed = 1603
    PrerequisitesNotMet = 1328
    MFInstallerError = 1344
    TooManyOpenFiles = 1073807364
    UnknownError = 214748364


