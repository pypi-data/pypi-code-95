import logging
import uuid

from sqlalchemy import (BIGINT, DATETIME, INTEGER, TIMESTAMP, VARBINARY,
                        Column, DateTime, ForeignKey, String, text)
from sqlalchemy.orm import relationship, object_session

from ..base import UUID, Base, indent, json_loop, json_test


log = logging.getLogger(__name__)


class Specimen(Base):
    __tablename__ = "Specimen"

    id = Column("Specimen_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)
    
    from .zone_identification import SpecimenZoneIdentification as t_zone_identification
    id_zone_identification = Column("Specimen_ZoneIdentification_Id", UUID, ForeignKey(t_zone_identification.id), nullable=False)
    from .zone_discipline import SpecimenZoneDiscipline as t_zone_discipline
    id_zone_discipline = Column("Specimen_ZoneDiscipline_Id", UUID, ForeignKey(t_zone_discipline.id), nullable=True)
    from .zone_description_physique import SpecimenZoneDescriptionPhysique as t_zone_description_physique
    id_zone_description_physique = Column("Specimen_ZoneDescriptionPhysique_Id", UUID, ForeignKey(t_zone_description_physique.id), nullable=True)
    from .zone_collecte import SpecimenZoneCollecte as t_zone_collecte
    id_zone_collecte = Column("Specimen_ZoneCollecte_Id", UUID, ForeignKey(t_zone_collecte.id), nullable=True)
    from .zone_datation_geologique import SpecimenZoneDatationGeologique as t_zone_datation_geologique
    id_zone_datation_geologique = Column("Specimen_ZoneDatationGeologique_Id", UUID, ForeignKey(t_zone_datation_geologique.id), nullable=True)
    id_zone_donnees_patrimoniales = Column("Specimen_ZoneDonneesPatrimoniales_Id", UUID, nullable=True)
    from .zone_constantes_conservation import SpecimenZoneConstantesConservation as t_zone_constantes_conservation
    id_zone_constantes_conservation = Column("Specimen_ZoneConstantesConservation_Id", UUID, ForeignKey(t_zone_constantes_conservation.id), nullable=True)
    id_zone_reproduction = Column("Specimen_ZoneReproduction_Id", UUID, nullable=True)
    id_zone_objet_associe = Column("Specimen_ZoneObjetAssocie_Id", UUID, nullable=True)
    from .zone_informations_systeme import SpecimenZoneInformationsSysteme as t_zone_informations_systeme
    id_zone_informations_systeme = Column("Specimen_ZoneInformationsSysteme_Id", UUID, ForeignKey(t_zone_informations_systeme.id), nullable=True)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)
    t_version = Column("_rowVersion", TIMESTAMP, nullable=False)

    # 
    # liens internes
    #

    zone_identification = relationship(t_zone_identification, foreign_keys=[id_zone_identification])    
    zone_discipline = relationship(t_zone_discipline, foreign_keys=[id_zone_discipline])
    zone_description_physique = relationship(t_zone_description_physique, foreign_keys=[id_zone_description_physique])
    zone_collecte = relationship(t_zone_collecte, foreign_keys=[id_zone_collecte])
    zone_datation_geologique = relationship(t_zone_datation_geologique, foreign_keys=[id_zone_datation_geologique])
    zone_constantes_conservation = relationship(t_zone_constantes_conservation, foreign_keys=[id_zone_constantes_conservation])
    zone_informations_systeme = relationship(t_zone_informations_systeme, foreign_keys=[id_zone_informations_systeme])

    #
    # Liens externes
    #  

    from .zone_determination import SpecimenZoneDetermination as t_zone_determination
    zones_determination = relationship(t_zone_determination, back_populates="specimen", order_by="SpecimenZoneDetermination.ordre")
    zones_multimedia = relationship("SpecimenZoneMultimedia", back_populates="specimen", order_by="SpecimenZoneMultimedia.ordre")    
    from .zone_bibliographie import SpecimenZoneBibliographie as t_zone_bibliographie
    zones_bibliographie = relationship(t_zone_bibliographie, back_populates="specimen", order_by=t_zone_bibliographie.ordre)
    from .zone_collection_anterieure import SpecimenZoneCollectionAnterieure as t_zone_collection_anterieure
    zones_collections_anterieures = relationship(t_zone_collection_anterieure, back_populates="specimen", order_by=t_zone_collection_anterieure.ordre)
    #
    #
    #

    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id

        # many-to-one fields
        

        # one-to-one data segments

        data['zone_identification'] = json_test(self.zone_identification)
        data['zone_discipline'] = json_test(self.zone_discipline)
        data['zone_description_physique'] = json_test(self.zone_description_physique)
        data['zone_collecte'] = json_test(self.zone_collecte)
        data['zone_datatation_geologique'] = json_test(self.zone_datation_geologique)
        data['id_zone_donnees_patrimoniales'] = self.id_zone_donnees_patrimoniales
        data['zone_constantes_conservation'] = json_test(self.zone_constantes_conservation)      
        data['id_zone_reproduction'] = self.id_zone_reproduction
        data['id_zone_objet_associe'] = self.id_zone_objet_associe
        data['zone_informations_systeme'] = json_test(self.zone_informations_systeme)

        # many-to-many data segments

        data['zones_determination'] = json_loop(self.zones_determination)
        data['zones_collections_anterieures'] = json_loop(self.zones_collections_anterieures)
        data['zones_bibliographie'] = json_loop(self.zones_bibliographie)
        data['zones_multimedia'] = json_loop(self.zones_multimedia)

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user
        data['t_version'] = self.t_version.hex()

        return data

    @property
    def inventoryNumber(self):
        if self.zone_identification:
            return self.zone_identification.numero_inventaire
        return None

    @property
    def localisation(self):
        if self.zone_constantes_conservation:
            return self.zone_constantes_conservation.localisation
        return None

    def listPhotos(self):
        """
        attempts to add an image to the specimen with the given windows path
        
        returns:
        None if we couldn't find images
        list of images if we could
        """
        nb_zm = len(self.zones_multimedia)
        zm = None
        if nb_zm == 1:
            zm = self.zones_multimedia[0]
            #log.info("INFO: found one zone_multimedia created %s by %s"%(zm.t_creation.isoformat(), zm.t_creation_user))
        elif nb_zm > 1:
            log.error("ERROR: multiple zone_multimedia")
            return None

        # we have a valid zm return that
        return zm

    def addPhoto(self, order, filename):
        """
        attempts to add an image to the specimen with the given windows path
        
        returns:
        true if the image could be added
        """
        photography_type = "Photographie"
        from .zone_multimedia import SpecimenZoneMultimedia
        session = object_session(self)
        nb_zm = len(self.zones_multimedia)
        zm = None
        if nb_zm == 0:
            # find the type for photography
            # NOTE: should be a passed value...
            from ..reference.reference import Reference, ReferenceZoneGenerale
            from ..reference.type_information import TypeInformation
            type_photo = session.query(TypeInformation)\
                .join(Reference, TypeInformation.id==Reference.id)\
                .join(ReferenceZoneGenerale, Reference.id_zone_generale==ReferenceZoneGenerale.id)\
                .filter(ReferenceZoneGenerale.libelle==photography_type).first()
            # need to create a zone multimedia...
            zm = SpecimenZoneMultimedia(self, type_photo)
            session.add(zm)
            log.info("zone_multimedia created")
        elif nb_zm == 1:
            zm = self.zones_multimedia[0]
            log.info("one zone multimedia %s"%(repr(zm)))
        else:
            log.error("nb_zm = %d - UNSUPPORTED FOR NOW"%(nb_zm))
            return False
        
        return zm.addPhoto(order, filename)
        