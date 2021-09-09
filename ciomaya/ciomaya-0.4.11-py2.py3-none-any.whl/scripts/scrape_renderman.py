from ciomaya.lib import scraper_utils

"""
A scraper to collect paths from Renderman nodes.
"""


ATTRS = {
    "Renderman_for_Maya": {
        "PxrBump": [
            "filename"
        ],
        "PxrCookieLightFilter": [
            "map"
        ],
        "PxrDiskLight": [
            "iesProfile"
        ],

        "PxrDomeLight": [
            "lightColorMap"
        ],

        "PxrGobo": [
            "map"
        ],
        "PxrGoboLightFilter": [
            "map"
        ],

        "PxrLayeredTexture": [
            "maskTexture",
            "filename"
        ],

        "PxrMultiTexture": [
            "filename0",
            "filename1",
            "filename2",
            "filename3",
            "filename4",
            "filename5",
            "filename6",
            "filename7",
            "filename8",
            "filename9",
        ],
        "PxrNormalMap": [
            "filename"
        ],
        "PxrOSL": [
            "shadername"
        ],

        "PxrProjectionLayer": [
            "channelsFilenames",
            "filename"
        ],
        "PxrPtexture": [
            "filename"
        ],

        "PxrRectLight": [
            "lightColorMap",
            "iesProfile"
        ],

        "PxrSphereLight": [
            "iesProfile"
        ],
        "PxrStdAreaLight": [
            "profileMap",
            "rman__EmissionMap",
            "iesProfile",
            "barnDoorMap"
        ],

        "PxrStdEnvMapLight": [
            "rman__EnvMap"
        ],
        "PxrTexture": [
            "filename"
        ],
        "PxrVisualizer": [
            "matCap"
        ],
        "RenderManArchive": [
            "filename"
        ],
        "rmanImageFile": [
            "File"
        ],
        "rmanTexture3d": [
            "File"
        ],
        "RMSAreaLight": [
            "mapname"
        ],
        "RMSCausticLight": [
            "causticPhotonMap"
        ],
        "RMSEnvLight": [
            "rman__EnvMap"
        ],
        "RMSGPSurface": [
            "SpecularMapB",
            "SpecularMap",
            "RoughnessMap",
            "MaskMap",
            "SurfaceMap",
            "DisplacementMap"
        ],
        "RMSGeoAreaLight": [
            "profilemap",
            "iesprofile",
            "lightcolormap",
            "barnDoorMap"
        ],
        "RMSGeoLightBlocker": [
            "Map"
        ],
        "RMSGlass": [
            "roughnessMap",
            "surfaceMap",
            "specularMap",
            "displacementMap"
        ],
        "RMSLightBlocker": [
            "Map"
        ],
        "RMSMatte": [
            "SurfaceMap",
            "MaskMap",
            "DisplacementMap"
        ],

        "RMSOcean": [
            "roughnessMap",
            "surfaceMap",
            "specularMap",
            "displacementMap"
        ]
    }
}

# See https://rmanwiki.pixar.com/display/RFM22/String+tokens+in+RfM
TOKENS = (r"_MAPID_", r"<udim>", r"<frame>", r"<f\d?>", r"<aov>", r"#+")


def run(_):

    paths = scraper_utils.get_paths(ATTRS)
    paths = scraper_utils.starize_tokens(paths, *TOKENS)
    paths = scraper_utils.expand_workspace(paths)
    paths = scraper_utils.extend_with_tx_paths(paths)
    return paths
