"""!@details
    Classes for secret share persistors and secret share device profile persistor
"""
import ionicsdk._private as _private
from ionicsdk.exceptions import *
from ionicsdk.errors import *
from ionicsdk.common import *

class SecretShareData(object):
    """!Secret Share data implementation.
        @details
        This class manages access to the secret share data.  This data consists 
        of a dictionary of key-values and a list of buckets.  Each bucket groups
        keys from the dictionary and assigns a threshold count - the number of keys
        in each bucket that must match in order to decrypt.
        
        The user must subclass this one and implement a GetData() and a GetBuckets()
        method.  These methods are called on the Python side from 'C' callbacks, and
        this class converts the Python data into native 'C' data for the SDK.
       
        def GetData() should return a dictionary of string keys to string values
        
        def GetBuckets() should return a list (or tuple) of SecretShareBucket objects.

        Example:
        \code{.py}
        class SecretShareFoo(ionicsdk.SecretShareData):
            def GetData(self):
                return {"key1":"value1"}
            def GetBuckets(self):
                secretShareBucket = ionicsdk.SecretShareBucket()
                secretShareBucket.append("key1")
                secretShareBucket.SetThreshold(1)
                return (secretShareBucket,)
         \endcode
        It is assumed the data returned is volatile and should be re-queried on any
        access to a key.
    """
    def __init__(self):
        """!Base class constructor for custom Secret Share Data.
        """
        self._callbackRefs = {}
    
        def cb_get_data(cSecretShareDataRef):
            keyvalues = self.GetData()
            count = len(keyvalues)
            
            cKeyValuePairArray = _private.CSecretShareKeyValuePairArray()
            cKeyValuePairs = (_private.CSecretShareKeyValuePair * count)()
            
            index = 0
            for key, value in keyvalues.items():
                cKeyValuePairs[index].pszKey = _private.CMarshalUtil.stringToC(key)
                cKeyValuePairs[index].pszValue = _private.CMarshalUtil.stringToC(value)
                index += 1
            
            cKeyValuePairArray.nSize = count
            cKeyValuePairArray.pKeyValuePairArray = _private.pointer(cKeyValuePairs[0])
            pcKvpArray = _private.pointer(cKeyValuePairArray)
            
            # Keep a handle to the relevant objects so they don't get free'd before the C layer finishes
            ref = _private.cast(pcKvpArray,_private.c_void_p)
            self._callbackRefs[ref.value] = [cKeyValuePairArray, cKeyValuePairs, pcKvpArray, ref]
            
            return ref.value

        def cb_get_buckets(cSecretShareDataRef):
            buckets = self.GetBuckets()
            count = len(buckets)

            cBucketArray = _private.CSecretShareBucketArray()
            cBuckets = (_private.CSecretShareBucket * count)()
            
            index = 0
            for bucket in buckets:
                strCount = len(bucket)
                cStrings = (_private.c_char_p * strCount)()
                for i in range(0, strCount):
                    cStrings[i] = c_char_p(bucket[i].encode('utf-8'))

                cBuckets[index].ppszKeyList = cStrings
                cBuckets[index].nThreshold = bucket.threshold
                cBuckets[index].nSize = strCount

                index += 1

            cBucketArray.nSize = count
            cBucketArray.pBucketList = _private.pointer(cBuckets[0])

            pcBucketArray = _private.pointer(cBucketArray)
    
            # Keep a handle to the relevant objects so they don't get free'd before the C layer finishes
            ref = _private.cast(pcBucketArray,_private.c_void_p)
            self._callbackRefs[ref.value] = [cBucketArray, cBuckets, pcBucketArray, ref]
            
            return ref.value

        def cb_release(pcValue):
            ref = _private.cast(pcValue,_private.c_void_p)
            del self._callbackRefs[ref.value]

        self._getDataCallback = _private.SecretShareCallback_getdata(cb_get_data)
        self._getBucketCallback = _private.SecretShareCallback_getbuckets(cb_get_buckets)
        self._releaseDataCallback = _private.SecretShareCallback_releasedata(cb_release)
        self._releaseBucketsCallback = _private.SecretShareCallback_releasebuckets(cb_release)
        
        self._cSecretShareData = _private.cLib.ionic_secret_share_create(self._getDataCallback, self._getBucketCallback, self._releaseDataCallback, self._releaseBucketsCallback)


class SecretShareBucket(list):
    """!Secret Share bucket implementation.
        @details
        This class is a list of keys contained in the SecretShareData. The buckets 
        group the key-value data and assign a threshold count - the number of keys 
        in each bucket that must match in order to decrypt.
        
        Access the keys just like any other list in Python. Use
        SetThreshold to assign the threshold value.
        
        A list of this object should be returned from the GetBuckets() function of a
        SecretShareData object.
    """
    def __init__(self):
        """!Base class constructor for custom Secret Share Bucket.
        """

        ##(int) Number of bucket list key values that need to match in order to decrypt a Secret Share
        self.threshold = 1

    def SetThreshold(self, threshold):
        """!Sets the threshold value for the bucket
            
        @param
            threshold (int): The threshold to use

        @return
            None
        """
        self.threshold = threshold


class SecretSharePersistor(object):
    """!Secret Share persistor implementation.
        @details
        This class uses a SecretShareData object to populate data. (See SecretShareData)
        
        DO NOT use the provided SecretShareData class alone.  You must subclass the provided
        class and add a GetData() and GetBuckets() method.
        
        A secret share persistor allows a user to generate and recover a key based 
        on groups of key-value data of which only a threshold amount of each group
        must match in order to recover the key.
        
        NOTE: The secret share persistor will query the SecretShareData each time a key
        is requested.
    """
    def __init__(self, secretsharedata):
        """!@details
            Initializes a Secret Share persistor from a secret share data object.

            @param
                secretsharedata (SecretShareData) A reference to a SecretShareData implementation object.
        """        
        if not issubclass(type(secretsharedata), SecretShareData):
            raise TypeError()

        self._cSecretSharePersistor = _private.cLib.ionic_secret_share_persistor_create(secretsharedata._cSecretShareData)

        if not self._cSecretSharePersistor:
            raise IonicException('Failed to create a SecretSharePersistor object. Check the log to know the reason for this error (common cause is failure to initialize internally).', IonicError.AGENT_ERROR)

    def SetFilePath(self, filePath):
        """!Sets the encrypted secret share file path
            
        @param
            filePath (string): The file path to use
            
        @return
            None
        """
        cFilePath = _private.CMarshalUtil.stringToC(filePath)
        _private.cLib.ionic_secret_share_persistor_set_filepath(self._cSecretSharePersistor, cFilePath)

    def GetKey(self):
        """!Generate (first call) or Retrieve (subsequent calls) a key
            
        @return
            CBytes struct that can be passed as key to other encryption functions
        """
        cBytes = _private.OWNED_POINTER(_private.CBytes)()
        _private.cLib.ionic_secret_share_persistor_get_key(self._cSecretSharePersistor,_private.byref(cBytes))
        return _private.CMarshalUtil.bytesFromC(cBytes)
