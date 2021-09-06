from .base import Version, checkVersion, dumps
from .caracteristiques_physiques.zone_generale import CaracteristiquesPhysiquesZoneGenerale
from .classification.classification import Classification
from .classification.zone_contexte import ClassificationZoneContexte
from .multimedia.multimedia import Multimedia
from .multimedia.zone_generale import MultimediaZoneGenerale
from .provenance.provenance import Provenance
from .provenance.zone_contexte import ProvenanceZoneContexte
from .provenance.zone_identification import ProvenanceZoneIdentification
from .reference.reference import Reference, ReferenceZoneGenerale
from .specimen.champs.multimedia import ChampSpecimenZoneMultimediaMultimedia
from .specimen.champs.zone_collecte.autres_coordonnees import \
    ChampSpecimenZoneCollecteAutresCoordonnees
from .specimen.champs.zone_collecte.provenance import \
    ChampSpecimenZoneCollecteProvenance
from .specimen.champs.zone_description_physique.caracteristiques_physiques import \
    ChampSpecimenZoneDescriptionPhysiqueCaracteristiquesPhysiques
from .specimen.champs.zone_identification.autre_numero import \
    ChampSpecimenAutreNumero
from .specimen.specimen import Specimen
from .specimen.zone_identification import SpecimenZoneIdentification
