#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This file is part of CbM (https://github.com/ec-jrc/cbm).
# Author    : Guido Lemoine, Konstantinos Anastasakis
# Credits   : GTCAP Team
# Copyright : 2021 European Commission, Joint Research Centre
# License   : 3-Clause BSD


import sys
import requests
from lxml import etree
import psycopg2
from datetime import datetime
from cbm.datas import db


def main(conn_str, aoi_polygon=None, start=None, end=None, card='', option=''):
    """
    start, end : 2019-06-01
    option: s1 ptype CARD-COH6 or CARD-BS, s2 plevel : LEVEL2A or LEVEL2AP
    card : s2, c6 or bs
    """
    aoi_polygon = '' if aoi_polygon is None else f"ST_Intersects(ST_GeomFromEWKT('SRID=4326; POLYGON(({aoi_polygon}))'), ST_SetSRID(ST_FlipCoordinates(col.zone),4326))"
    
    conn = db.connection()
    cur = conn.cursor()

    sql = f"""    CREATE TABLE dias_catalogue_test AS
        SELECT
    		injection_date AS obstime,
            id AS reference,
            RIGHT(sat, LENGTH(sat) - 1) AS sensor,
            LEFT(lower(sat), LENGTH(sat) - 1) AS card,
            null AS status,
            ST_FlipCoordinates(zone) AS footprint
        FROM (
    		SELECT
    			id, uid, sat, type, zone, injection_date, s3_path
    		FROM
    			dblink('{conn_str}',
    				   'SELECT id, uid, sat, type, zone, injection_date, s3_path
                       WHERE {aoi_polygon}
                       FROM datas')
    		AS f(
    			id VARCHAR,
    			uid VARCHAR,
    			sat VARCHAR,
    			type VARCHAR,
    			zone GEOMETRY,
    			injection_date TIMESTAMP WITHOUT TIME ZONE,
    			s3_path VARCHAR
    			)
    	) AS datas
    ;"""
    cur.execute(sql)
