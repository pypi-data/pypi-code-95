#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
from confluent_kafka import Producer, KafkaException, KafkaError

def obtenirConfigurationsProducteurDepuisVariablesEnvironnement():
    bootstrap_servers = os.environ['BOOTSTRAP_SERVERS'] if 'BOOTSTRAP_SERVERS' in os.environ else 'localhost:9092'
    
    config_kafka = {
        'bootstrap.servers': bootstrap_servers
    }
    
    return config_kafka    

def creerProducteur(config):
    producteur = Producer(**config)
    return producteur
"""
Fonction: publierMessage
Description: Cette fonction permet produire un message sur un topic Kafka
Paramètres:
    producteur: Producteur Kafka à utiliser
    message: Dictionnaire du message à publier:
        key: Clé pour publier le message
        value: Message à publier
    topic:Topic Kafka sur lequel publier le message
Retour:
    True si le message a bien été publié
"""    
def publierMessage(producteur, message, topic, logger=None):
    def callback_livraison(err, msg):
        if err:
            log_message = "Livraison du message impossible: {}".format(err)
            if logger is not None:
                logentry = {}
                logentry['topic'] = msg.topic()
                logentry['partition'] = msg.partition()
                logentry['offset'] = msg.offset()
                logentry['message_code'] = "ERREUR_PRODUCTEUR"
                logger.error(log_message, extra=logentry)
            
            else:
                print(log_message)
        else:
            log_message = "Le message a été livré. Topic {}, Partition {}, Offset {}".format(
                msg.topic(),
                msg.partition(),
                msg.offset())
            if logger is not None:
                logentry = {}
                logentry['topic'] = msg.topic()
                logentry['partition'] = msg.partition()
                logentry['offset'] = msg.offset()
                logentry['message_code'] = "CALLBACK_MESSAGE_PUBLIE"
                logger.info(log_message, extra=logentry)
            else:
                print(log_message)
                
    if logger is None:
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger()
    try:
        producteur.produce(topic, value=message["value"], key=message["key"], callback=callback_livraison)
        logentry = {}
        logentry['topic'] = topic
        logentry['key'] = message["key"].decode()
        logentry['value'] = message["value"].decode()
        logentry['message_code'] = "MESSAGE_PUBLIE"
        log_message = "Message {} publié sur le topic {}".format(message["key"].decode(), topic)
        logger.info(log_message, extra=logentry)
    except BufferError as e:
        logentry = {}
        logentry['topic'] = topic
        logentry['key'] = message["key"].decode()
        logentry['value'] = message["value"].decode()
        logentry['message_code'] = "PRODUCTEUR_QUEUE_MESSAGE_PLEINE"
        log_message = "La queue de message est pleine. Erreur {}".format(str(e))
        logger.error(log_message, extra=logentry)
        return False
    except KafkaError as e:
        logentry = {}
        logentry['topic'] = topic
        logentry['key'] = message["key"].decode()
        logentry['value'] = message["value"].decode()
        logentry['message_code'] = "ERREUR_PRODUCTEUR"
        logentry['error_code'] = e.error_code
        logentry['reason'] = e.reason
        log_message = "Erreur Kafka: {}: {}".format(e.error_code, e.reason)
        logger.error(log_message, extra=logentry)
        return False
    except KafkaException as e:
        logentry = {}
        logentry['topic'] = topic
        logentry['key'] = message["key"].decode()
        logentry['value'] = message["value"].decode()
        logentry['message_code'] = "ERREUR_PRODUCTEUR"
        logentry['error_code'] = e.error_code
        logentry['reason'] = e.reason
        log_message = "Erreur Kafka: {}: {}".format(e.args[0].error_code, e.args[0].reason)
        logger.error(log_message, extra=logentry)
        return False
        
    producteur.flush()
    return True