# -*- coding: utf-8 -*-

SOURCES = """SELECT DISTINCT ON (info.source_name)
    info.id,
    info.source_name as name
FROM info
ORDER BY info.source_name ASC, info.id ASC
"""

ADDRESSES = """
SELECT DISTINCT ON (info.tags->>'addr:street')
    info.id as id,
    info.source_name as source_name,
    info.tags->>'addr:city' as city,
    info.tags->>'addr:street' as street
FROM info
WHERE
    info.tags::jsonb ? 'addr:street'
ORDER BY
    info.tags->>'addr:street'
"""

HOUSENUMBERS = """
SELECT
    info.id as id,
    info.source_name as source_name,
    info.tags->>'addr:housenumber' as housenumber,
    info.tags->>'addr:street' as street,
    info.tags->>'addr:city' as city
FROM info
WHERE
    info.tags::jsonb ? 'addr:street'
"""

POINTS = """
SELECT
    info.id AS id,
    info.source_name as source_name,
    sources.id as src_id,
    node.geom as geom,
    info.source_id as source_id,
    info.tags as tags,
    info.properties as properties,
    json_build_array(ST_X(node.geom),ST_Y(node.geom)) as crds,
    node.id as node_id
FROM
    info,
    node,
    sources
WHERE
    sources.name=info.source_name AND
    node.info_id=info.id AND
    ((info.tags IS NOT NULL) OR (info.properties IS NOT NULL))
"""

WAYS = """
SELECT
    info.id AS id,
    ST_MakeLine(node.geom ORDER BY way_node.sorting) as geom,
    ST_Centroid(ST_MakeLine(node.geom ORDER BY way_node.sorting)) as centroid,
    ST_IsClosed(ST_MakeLine(node.geom ORDER BY way_node.sorting)) as is_closed,
    count(node.id) as length,
    info.source_name,
    sources.id as src_id,
    info.source_id as source_id,
    info.tags as tags,
    info.properties as properties
FROM
    info,
    node,
    way_node,
    sources
WHERE
    sources.name=info.source_name AND
    way_node.info_id=info.id AND
    way_node.node_id=node.id
GROUP BY
    info.id, sources.id
"""

GRAPH = """
SELECT
    -- start_node.id as id,
    format('%s-%s', start_node.id, end_node.id) as id,
    way_info.source_name,
    sources.id as src_id,
    way_info.source_id,
    ST_MakeLine(ARRAY[start_node.geom, end_node.geom]) as geom,
    start_info.id as sinfo_id,
    start_node.id as snode_id,
    start_info.tags as stags,
    end_info.id as tinfo_id,
    end_node.id as tnode_id,
    end_info.tags as ttags,
    way_info.tags as tags,
    way_info.properties as properties,
    ST_Distance(ST_Transform(start_node.geom, 3857), ST_Transform(end_node.geom, 3857)) as len,
    start_node.geom as snode,
    end_node as tnode
FROM
    info as way_info,
    info as start_info,
    info as end_info,
    node as start_node,
    node as end_node,
    way_node as start_way,
    way_node as end_way,
    sources
WHERE
    sources.name=way_info.source_name AND
    way_info.id = start_way.info_id AND
    start_info.id = start_node.info_id AND
    end_info.id = end_node.info_id AND
    start_way.node_id = start_node.id AND
    end_way.node_id = end_node.id AND
    (way_info.tags::jsonb?'highway')::boolean AND
    (start_way.sorting+1 = end_way.sorting)
"""

SPLITTEDSEGMENTSNODES = """
SELECT
    nextval('snodesseq') as id,
    -- insta_id(node.info_id) as id,
    node.info_id as node_id,
    wayinfo.id as way_id,
    relinfo.id as rel_id,
    count(node.id) OVER (PARTITION BY way_node.info_id) as length,
    ST_MakeLine(node.geom) OVER (PARTITION BY way_node.info_id ORDER BY way_node.sorting) as geom,
    node.geom as node,
    way_node.sorting as sorting,
    relinfo.source_name AS source_name,
    sources.id as src_id,
    relinfo.tags AS tags,
    relinfo.properties AS properties,
    relinfo.source_id AS source_id,
    relation.role as role,
    array_agg(relation.role) OVER (PARTITION BY relation.info_id) as all_roles
FROM
    info as relinfo,
    info as wayinfo,
    node,
    way_node,
    relation,
    sources
WHERE
    sources.name=relinfo.source_name AND
    node.id = way_node.node_id AND
    relation.info_id = relinfo.id AND
    way_node.info_id=wayinfo.id AND
    way_node.info_id = relation.member_id AND
    relinfo.tags::jsonb ?| array['landuse', 'boundary']
"""

SIMPLEPOLYGONS = """
SELECT
    -- format('%s', id),
    nextval('spolyseq') as id,
	ST_MakePolygon(geom) as geom,
    centroid,
    trunc(ST_Area(ST_Transform(ST_MakePolygon(geom), 3857))::numeric, 2) as area,
	source_name,
    src_id,
	source_id,
	tags::jsonb,
	properties::jsonb
FROM (
    SELECT * FROM ways
    WHERE length > 2 AND is_closed AND
        ((tags::jsonb?'area' AND tags->>'area'<>'no') OR tags::jsonb ?| array['landuse', 'boundary', 'building', 'leisure', 'natural'])
    ) as filtered_way
"""

REBUILDEDPOLYGONPATHS = """
SELECT
    -- format('%s-%s', segment_points.rel_id, nextval('mypolyseq')) as id,
    -- format('%s-%s', segment_points.rel_id::text, md5(random()::text || clock_timestamp()::text)::uuid) as id,
    nextval('rpathseq') as id,
    -- min(segment_points.way_id) as way_id,
    -- insta_id(segment_points.rel_id) as id,

    (ST_Dump(ST_LineMerge(ST_Union(segment_points.geom order by segment_points.rel_id)))).geom as geom,
    ST_IsClosed((ST_Dump(ST_LineMerge(ST_Union(segment_points.geom order by segment_points.rel_id)))).geom) as is_closed,
    sum(segment_points.length) as length,
    segment_points.source_name,
    segment_points.src_id,
    segment_points.tags::jsonb,
    segment_points.properties::jsonb,
    segment_points.source_id
FROM segment_points
WHERE 'outer' = ANY(all_roles)
GROUP BY
    segment_points.rel_id, segment_points.source_name, segment_points.src_id, segment_points.source_id,
    segment_points.tags::jsonb, segment_points.properties::jsonb
"""

REBUILDEDPOLYGONS = """
SELECT
    nextval('spolyseq') as id,
    -- way_id,
    ST_MakePolygon(geom) as geom,
    ST_Centroid(geom) as centroid,
    trunc(ST_Area(ST_Transform(ST_MakePolygon(geom), 3857))::numeric, 2) as area,
    source_name,
    src_id,
    source_id,
    tags,
    properties
FROM (SELECT * FROM {rpath} WHERE is_closed) as closed_paths
""".format

POLYS = "(SELECT * FROM {spolys}) UNION (SELECT * FROM rpolys);".format
