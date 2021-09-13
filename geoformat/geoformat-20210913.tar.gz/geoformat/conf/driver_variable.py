

# OGR driver names
OGR_FORMAT_ESRI_SHAPEFILE = "ESRI SHAPEFILE"
OGR_FORMAT_POSTGRESQL = "POSTGRESQL"
OGR_FORMAT_KML = "KML"
OGR_FORMAT_XLSX = "XLSX"
OGR_FORMAT_CSV = "CSV"
OGR_FORMAT_GEOJSON = "GEOJSON"
OGR_DRIVER_NAMES = {OGR_FORMAT_ESRI_SHAPEFILE,
                    OGR_FORMAT_POSTGRESQL,
                    OGR_FORMAT_KML,
                    OGR_FORMAT_XLSX,
                    OGR_FORMAT_CSV,
                    OGR_FORMAT_GEOJSON,
                    }


field_driver_uncompatibility = {
    (OGR_FORMAT_GEOJSON, 'Binary'): "OGR/GDAL does not allow to use binary field's type '{field_name}' in {ogr_format}."
                                    " You should convert it to string format."
}