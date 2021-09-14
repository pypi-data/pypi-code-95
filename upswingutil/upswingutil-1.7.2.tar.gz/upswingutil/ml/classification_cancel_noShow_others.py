import pandas as pd
import numpy as np
from upswingutil.db import Mongodb
from upswingutil.pms import PMS
from loguru import logger
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.utils import resample
from numpy import zeros
from upswingutil.resource import get_model_from_cloud_storage, upload_model_to_cloud_storage


class Classification_Cancellation_NoShow_Others:
    def __init__(self, pms:str, orgId:str):
        self.pms = pms
        self.orgId = orgId

    def get_data(self) -> list:
        __pipeline__ = list()
        if self.pms == PMS.RMS:
            __pipeline__ = [
                {
                    '$addFields': {
                        'durationOfStay': {
                            '$floor': {
                                '$divide': [
                                    {
                                        '$subtract': [
                                            {
                                                '$toDate': '$departureDate'
                                            }, {
                                                '$toDate': '$arrivalDate'
                                            }
                                        ]
                                    }, 60 * 60 * 24 * 1000
                                ]
                            }
                        }, 
                        'bookingWindowDays': {
                            '$floor': {
                                '$divide': [
                                    {
                                        '$subtract': [
                                            {
                                                '$toDate': '$arrivalDate'
                                            }, {
                                                '$toDate': '$createdDate'
                                            }
                                        ]
                                    }, 60 * 60 * 24 * 1000
                                ]
                            }
                        }
                    }
                }, {
                    '$match': {
                        'guests': {
                            '$type': 4
                        }
                    }
                }, {
                    '$addFields': {
                        'didVisit': {
                            '$switch': {
                                'branches': [
                                    {
                                        'case': {
                                            '$eq': [
                                                '$status', 'Cancelled'
                                            ]
                                        }, 
                                        'then': 0
                                    }, {
                                        'case': {
                                            '$eq': [
                                                '$status', 'NoShow'
                                            ]
                                        }, 
                                        'then': 1
                                    }
                                ], 
                                'default': 2
                            }
                        }, 
                        'guestCount': {
                            '$size': '$guests'
                        }
                    }
                }, {
                    '$project': {
                        'didVisit': 1, 
                        'guestCount': 1, 
                        'durationOfStay': 1, 
                        'bookingWindowDays': 1, 
                        'Class': 1, 
                        'rateTypeName': 1, 
                        'clientId': 1, 
                        'rateTypeName': 1
                    }
                }
            ]

        elif self.pms == PMS.ORACLE:
            __pipeline__ = [
                {
                    '$match': {
                        'hotelId': 'SAND01', 
                        'guestInfo.adults': {
                            '$gte': 1
                        }
                    }
                }, {
                    '$project': {
                        'createBusinessDate': 1, 
                        'arrivalDate': 1, 
                        'departureDate': 1, 
                        'guestCount': '$guestInfo.adults', 
                        'rateTypeName': '$roomStay.ratePlanCode', 
                        'clientId': '$hotelId', 
                        'Class': '$roomStay.roomType', 
                        'status': 1
                    }
                }, {
                    '$match': {
                        'rateTypeName': {
                            '$type': 2
                        }
                    }
                }, {
                    '$addFields': {
                        'didVisit': {
                            '$switch': {
                                'branches': [
                                    {
                                        'case': {
                                            '$eq': [
                                                '$status', 'Cancelled'
                                            ]
                                        }, 
                                        'then': 0
                                    }, {
                                        'case': {
                                            '$eq': [
                                                '$status', 'NoShow'
                                            ]
                                        }, 
                                        'then': 1
                                    }
                                ], 
                                'default': 2
                            }
                        }, 
                        'durationOfStay': {
                            '$floor': {
                                '$divide': [
                                    {
                                        '$subtract': [
                                            {
                                                '$toDate': '$departureDate'
                                            }, {
                                                '$toDate': '$arrivalDate'
                                            }
                                        ]
                                    }, 60 * 60 * 24 * 1000
                                ]
                            }
                        }, 
                        'bookingWindowDays': {
                            '$floor': {
                                '$divide': [
                                    {
                                        '$subtract': [
                                            {
                                                '$toDate': '$arrivalDate'
                                            }, {
                                                '$toDate': '$createBusinessDate'
                                            }
                                        ]
                                    }, 60 * 60 * 24 * 1000
                                ]
                            }
                        }
                    }
                }, {
                    '$project': {
                        'arrivalDate': 0, 
                        'createBusinessDate': 0, 
                        'departureDate': 0, 
                        'status': 0
                    }
                }
            ]

        mongo = Mongodb(self.orgId)
        result = mongo.execute_pipeline(mongo.RESERVATION_COLLECTION, __pipeline__)
        mongo.close_connection()
        return result
        
    def preprocess(self):
        data = pd.DataFrame(self.get_data())
        logger.info(f'DataFrame Created from the Data Pipeline !!')
        data = data.query('guestCount > 0')
        features = data.iloc[:, 1:]
        if self.pms == PMS.RMS:
            features['rateTypeName'] = features['rateTypeName'].replace("", 'None')
        labels = features['didVisit']
        features = features.drop('didVisit', axis=1)

        ##Feature Engineering (one Hot Encoding the categories)
        #1. THis approach below is very easy but can not be replicated when predictions, we need a trained model to perform the same one hot encoding 
        features = pd.get_dummies(features, columns=['clientId', 'rateTypeName', 'Class'])

        ##2. Therefore, we are using the OneHot Encoding method to train a scikit learn model and furhter be able to use it during prediction
        # self.one_hot = OneHotEncoder(sparse=False, drop='first')
        # self.one_hot.fit(features[['clientId','rateTypeName', 'Class']])
        # upload_model_to_cloud_storage(self.one_hot, self.orgId, 'Classification_Cancellation_NoShow_Others__ONE-HOT-ENCODING.pkl')
        # join = pd.DataFrame(self.one_hot.transform(features[['clientId','rateTypeName', 'Class']]))
        # features = pd.concat([features, join],axis=1).drop(['rateTypeName', 'Class', 'clientId'], axis=1)

        X_train, self.X_test, y_train, self.y_test = train_test_split(features, labels, test_size=0.3, random_state=42)
        logger.info(f'Train-Test Split Successful !!')
        ## Upsampling to deal with Skewed Distributed Class
        train_data = pd.concat([X_train, y_train], axis=1)
        negative = train_data[train_data.didVisit==0]
        positive = train_data[train_data.didVisit==2]
        neutral = train_data[train_data.didVisit==1]

        # upsample minority
        neg_upsampled = resample(negative,
        replace=True, # sample with replacement
        n_samples=len(positive), # match number in majority class
        random_state=27) # reproducible results

        neu_upsampled = resample(neutral,
        replace=True, # sample with replacement
        n_samples=len(positive), # match number in majority class
        random_state=27)
        # combine majority and upsampled minority
        upsampled = pd.concat([positive, neg_upsampled, neu_upsampled])
        upsampled = upsampled.sample(frac=1)
        self.labels = upsampled.didVisit
        self.features = upsampled.drop('didVisit', axis=1)
        logger.info(f'Upsampled Training Features and Labels are Created !!')


    def train(self):

        try:
            ## MODEL ARCHITECTURE CREATION
            self.model = tf.keras.Sequential([
                tf.keras.layers.Dense(64, activation='relu', input_shape=(self.features.shape[1],)),
                tf.keras.layers.Dense(32, activation='relu',activity_regularizer=tf.keras.regularizers.L2(0.01)),
                tf.keras.layers.Dense(32, activation='relu',activity_regularizer=tf.keras.regularizers.L2(0.01)),
                tf.keras.layers.Dense(3, activation='softmax')
            ])

            logger.info("Model is Successfully Initialized...")
            
            ## COMPILATION PHASE
            self.model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

            ## TRAINING PHASE
            self.history = self.model.fit(self.features, self.labels, batch_size=32, epochs=8, validation_data=(self.X_test, self.y_test), verbose=0)
            logger.info('Model is Successfully Trained, Here is the Metrics of the Model training:-->')
            logger.info(f"\tLoss: {self.history.history['loss'][-1] :.4f}\n \
                \tValidation Loss: {self.history.history['val_loss'][-1] :.4f} \
                \tAccuracy: {self.history.history['accuracy'][-1]*100 :.4f} \
                \tValidation Accuracy: {self.history.history['val_accuracy'][-1]*100 :.4f}  \
                ")

            try:
                upload_model_to_cloud_storage(self.model, self.orgId, 'Classification_Cancellation_NoShow_Others.pkl')
                logger.info("upload_model_to_cloud_storage Successfully ...")
            except Exception as e:
                self.model.save('Classification_Cancellation_NoShow_Others')
                logger.info("Tensorflow Model Saved!! --> model.save() ")


        except Exception as e:
            logger.info(f"Model is not Created, Some Error: {e}, with Model Initlization/Compilation/Training !")

    def predict(self, clientId:int, rateTypeName:str, Class:str, durationOfStay:float, bookingWindowDays:float, guestCount:int):

        try:
            self.model = get_model_from_cloud_storage(self.orgId, "Classification_Cancellation_NoShow_Others.pkl")
            logger.info("Loading of the Model from the Cloud is Successful!")
        except Exception as e:
            logger.info(f'Error in Loading: {e}')
            self.model = tf.saved_model.load('Classification_Cancellation_NoShow_Others')

        if self.pms == PMS.RMS:
            test_shape = 34
            columns = ['durationOfStay', 'bookingWindowDays', 'guestCount', 'clientId_0',
        'clientId_11263', 'clientId_11264', 'clientId_11286', 'clientId_11288',
        'clientId_11289', 'clientId_11290', 'clientId_11347', 'clientId_12053',
        'clientId_12333', 'clientId_12952', 'clientId_13773', 'clientId_14170',
        'clientId_14277', 'clientId_14278', 'rateTypeName_',
        'rateTypeName_BAR (Multi)', 'rateTypeName_BAR Rate',
        'rateTypeName_BAR_Airbnb', 'rateTypeName_BAR_BB',
        'rateTypeName_BAR_Hotelbeds',
        'rateTypeName_BAR_Hotelbeds_Non Refundable',
        'rateTypeName_BAR_Non Refundable',
        'rateTypeName_Direct Booking_Internal Rate',
        'rateTypeName_Old system rate', 'rateTypeName_Owner House Use ONLY',
        'Class_Good', 'Class_Loyal', 'Class_None', 'Class_Temporary',
        'Class_VIP']
        elif self.pms == PMS.ORACLE:
            test_shape = 17
            columns = None

        test = pd.DataFrame(zeros(shape=(1,test_shape), dtype=np.int), columns=columns)

        test['durationOfStay'] = durationOfStay
        test['bookingWindowDays'] = bookingWindowDays
        test['guestCount'] = guestCount
        test[f'Class_{Class}'] = 1
        test[f'rateTypeName_{rateTypeName}'] = 1
        test[f'clientId_{clientId}'] = 1

        pred = self.model.predict(test)
        final = pred.argmax()
        d = {
                0:'Cancelled',
                1:'No Show',
                2:'Others'
            }
        final = d[final]
        overall = {d[i]:round(pred[0][i]*100, 4) for i in range(3)}
        return final, overall


        
