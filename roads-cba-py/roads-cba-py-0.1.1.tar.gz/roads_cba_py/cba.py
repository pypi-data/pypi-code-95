import numpy as np
from numpy_financial import irr

from roads_cba_py import defaults
from roads_cba_py.cba_result import CbaResult
from roads_cba_py.defaults import (
    dDiscount_Rate,
    dEconomic_Factor,
    dGrowth,
    dTrafficLevels,
    dVehicleFleet,
    iSurfaceDefaults,
    dWidthDefaults,
    dConditionData,
    dRoadWorks,
    dRecurrent,
    dRecMult,
    dWorkEvaluated,
    dm_coeff,
    dVOC,
    dSPEED,
    dRoadDet,
    iri_cc_df,
    cc_from_iri_lu,
    default_lanes,
    traffic_ranges,
    alternatives,
    traffic_range_lu,
    lanes_lu,
)
from roads_cba_py.section import Section
from roads_cba_py.utils import print_diff


def test_api(x):
    return x + 7

class CostBenefitAnalysisModel:
    def __init__(self):
        self.dDiscount_Rate = dDiscount_Rate
        self.dEconomic_Factor = dEconomic_Factor
        self.dGrowth = dGrowth
        self.dTrafficLevels = dTrafficLevels
        self.dVehicleFleet = dVehicleFleet
        self.iSurfaceDefaults = iSurfaceDefaults
        self.dWidthDefaults = dWidthDefaults
        self.dConditionData = dConditionData
        self.dRoadWorks = dRoadWorks
        self.dRecurrent = dRecurrent
        self.dRecMult = dRecMult
        self.dWorkEvaluated = dWorkEvaluated
        self.dm_coeff = dm_coeff
        self.dVOC = dVOC
        self.dSPEED = dSPEED
        self.dRoadDet = dRoadDet
        self.iri_cc_df = iri_cc_df
        self.default_lanes = default_lanes

    def compute_cba_for_section(self, section: Section) -> CbaResult:
        """
        Main entry to computer Cost Benefit Analysis for each road section
        """

        # Step 1: Get input attributes from section
        section = self.fill_defaults(section)
        dLength = section.length
        iLanes = section.lanes
        dWidth = section.width
        iRoadClass = section.road_class
        iTerrain = section.terrain
        iTemperature = section.temperature
        iMoisture = section.moisture
        # iRoadType = section.road_type
        iSurfaceType = section.surface_type
        iConditionClass = section.condition_class

        dStructuralNo = section.structural_no
        iPavementAge = section.pavement_age
        # iDrainageClass = None
        iGrowthScenario = section.traffic_growth

        dAADT = np.zeros((13, 20), dtype=np.float64)
        dAADT[0][0] = section.aadt_motorcyle
        dAADT[1][0] = section.aadt_carsmall
        dAADT[2][0] = section.aadt_carmedium
        dAADT[3][0] = section.aadt_delivery
        dAADT[4][0] = section.aadt_4wheel
        dAADT[5][0] = section.aadt_smalltruck
        dAADT[6][0] = section.aadt_mediumtruck
        dAADT[7][0] = section.aadt_largetruck
        dAADT[8][0] = section.aadt_articulatedtruck
        dAADT[9][0] = section.aadt_smallbus
        dAADT[10][0] = section.aadt_mediumbus
        dAADT[11][0] = section.aadt_largebus
        dAADT[12][0] = section.aadt_total

        iNoAlernatives, dAlternatives = self.compute_alternatives(iSurfaceType, iRoadClass, iConditionClass)

        dCostFactor = self.compute_cost_factor(iSurfaceType, iRoadClass, iConditionClass)

        # Annual traffic
        dAADT = self.compute_annual_traffic(dAADT, iGrowthScenario)
        # ESA Loading
        dESATotal = self.compute_esa_loading(dAADT, iLanes)
        # Truck percent
        dTRucks = self.compute_trucks_percent(dAADT)
        # Vehicle Utilization
        dUtilization = self.compute_vehicle_utilization(dAADT, dLength)

        ########################
        # Output variables
        ########################
        sRoadCode = np.empty((13, 20), dtype="<U30")  # alternatives, years
        dCondIRI = np.zeros((13, 20), dtype=np.float64)  # alternatives, years
        dCondCON = np.zeros((13, 20), dtype=np.int16)  # alternatives, years
        dCondSNC = np.zeros((13, 20), dtype=np.float64)  # ' alternatives, years
        iCondAge = np.zeros((13, 20), dtype=np.int16)  # ' alternatives, years
        iCondLanes = np.zeros((13, 20), dtype=np.int16)  # ' alternatives, years
        dCondWidth = np.zeros((13, 20), dtype=np.float64)  # ' alternatives, years
        dCondLength = np.zeros((13, 20), dtype=np.float64)  # ' alternatives, years
        iCondSurface = np.zeros((13, 20), dtype=np.int16)  # ' alternatives, years
        dCostCapitalFin = np.zeros((13, 20), dtype=np.float64)  # ' alternatives, years
        dCostRepairFin = np.zeros((13, 20), dtype=np.float64)  # ' alternatives, years
        dCostRecurrentFin = np.zeros((13, 20), dtype=np.float64)  # ' alternatives, years
        dCostAgencyFin = np.zeros((13, 20), dtype=np.float64)  # ' alternatives, years
        dCostCapitalEco = np.zeros((13, 20), dtype=np.float64)  # ' alternatives, years
        dCostRepairEco = np.zeros((13, 20), dtype=np.float64)  # ' alternatives, years
        dCostRecurrentEco = np.zeros((13, 20), dtype=np.float64)  # ' alternatives, years
        dCostAgencyEco = np.zeros((13, 20), dtype=np.float64)  # ' alternatives, years
        dCostVOC = np.zeros((13, 20), dtype=np.float64)  # ' alternatives, years
        dCostTime = np.zeros((13, 20), dtype=np.float64)  # ' alternatives, years
        dCostUsers = np.zeros((13, 20), dtype=np.float64)  # ' alternatives, years
        dCondSpeed = np.zeros((13, 20, 12), dtype=np.float64)  # uble  ' alterntive, years, vehicles
        dCondSpeedAve = np.zeros((13, 20), dtype=np.float64)  # ' alternative, year
        dCostTotal = np.zeros((13, 20), dtype=np.float64)  # ' alternatives, years
        dNetTotal = np.zeros((13, 20), dtype=np.float64)  # ' alternatives, years
        dSolNPV = np.zeros((13,), dtype=np.float64)  # As Double ' altertnatives
        dSolNPVKm = np.zeros((13,), dtype=np.float64)  # As Double ' alternatives
        dSolNPVCost = np.zeros((13,), dtype=np.float64)  # As Double ' alternatives
        sSolClass = np.empty((13,), dtype="<U30")  # As String ' alternatives
        sSolCode = np.empty((13,), dtype="<U30")  # As String ' alternatives
        sSolName = np.empty((13,), dtype="<U35")  # As String ' alternatives
        dSolCost = np.zeros((13,), dtype=np.float64)  # As Double ' alternatives
        dSolCostkm = np.zeros((13,), dtype=np.float64)  # As Double ' alternatives
        iSolYear = np.zeros((13,), dtype=np.float64)  # As Double ' alternatives

        ####################################################
        # Loop alternatives
        ####################################################
        iTheSelected = 1
        dNPVMax = 0.0

        for ia in range(iNoAlernatives):
            """
            LOOP YEARS
            """
            dYearRoughness = section.roughness
            dYearSNC = dStructuralNo
            iYearAge = iPavementAge
            iYearLanes = iLanes
            dYearWidth = dWidth
            dYearLength = dLength
            iYearSurface = iSurfaceType

            work_idx = int(dAlternatives[ia, 0]) - 1
            work_year = int(dAlternatives[ia, 1])
            alt = alternatives[work_idx]

            iTheRepair = alt.repair
            repair_years = [work_year + i * alt.repair_period for i in [1, 2, 3, 4]]

            dSolNPV[ia] = 0

            for iy in range(20):
                iCondLanes[ia, iy] = iYearLanes
                dCondWidth[ia, iy] = dYearWidth
                dCondLength[ia, iy] = dYearLength
                dCondSNC[ia, iy] = dYearSNC
                iCondSurface[ia, iy] = iYearSurface

                # Capital Road Work
                if iy == work_year - 1:
                    # Look at the Number of Lane Classes
                    if alt.lanes_class is not None and alt.lanes_class > 0:
                        iCondLanes[ia, iy] = iYearLanes = alt.condition
                        dCondWidth[ia, iy] = dYearWidth = alt.width
                        iCondSurface[ia, iy] = iYearSurface = alt.surface

                    # Structural number after periodic maintenance for bituminous roads
                    if alt.thickness is not None and alt.thickness > 0:
                        dCondSNC[ia, iy] = dYearSNC = dCondSNC[ia, iy] + alt.thickness * alt.strength * 0.0393701

                    # Structural number after rehabiliation for bituminous roads
                    if alt.snc is not None and alt.snc > 0:
                        dCondSNC[ia, iy] = dYearSNC = alt.snc

                    # Capital work costs
                    unit_cst = alt.get_unit_cost(iTerrain)
                    dCostCapitalFin[ia, iy] = unit_cst * dCondLength[ia, iy] * dCondWidth[ia, iy] / 1000.0 * dCostFactor
                    dCostCapitalEco[ia, iy] = dCostCapitalFin[ia, iy] * self.dEconomic_Factor

                    sRoadCode[ia, iy] = sSolCode[ia] = alt.code
                    sSolName[ia] = alt.name
                    sSolClass[ia] = alt.work_class

                    iSolYear[ia] = iy + 1  # Since iy is counted from 0 and year order starts from 1
                    dSolCost[ia] = dCostCapitalFin[ia, iy]
                    dSolCostkm[ia] = dSolCost[ia] / dCondLength[ia, iy]

                # repair road work
                if (iy + 1) in repair_years:
                    repair_alt = alternatives[iTheRepair - 1]
                    sRoadCode[ia, iy] = repair_alt.code
                    if repair_alt.lanes_class and repair_alt.lanes_class > 0:
                        iCondLanes[ia, iy] = iYearLanes = repair_alt.lanes_class
                        dCondWidth[ia, iy] = dYearWidth = repair_alt.width
                        iCondSurface[ia, iy] = iYearSurface = repair_alt.surface

                    # structural number
                    if repair_alt.snc and repair_alt.snc > 0:
                        dCondSNC[ia, iy] = dYearSNC = repair_alt.snc

                    dCostRepairFin[ia, iy] = (
                        repair_alt.get_unit_cost(iTerrain) * dCondLength[ia, iy] * dCondWidth[ia, iy] / 1000.0
                    )
                    dCostRepairEco[ia, iy] = dCostRepairFin[ia, iy] * self.dEconomic_Factor

                # recurrent road work without recurrent maintenance condition multipliers
                dCostRecurrentFin[ia, iy] = (
                    self.dRecurrent[iCondSurface[ia, iy] - 1, iCondLanes[ia, iy] - 1] * dCondLength[ia, iy] / 1000000.0
                )
                dCostRecurrentEco[ia, iy] = (
                    self.dRecurrent[iCondSurface[ia, iy] - 1, iCondLanes[ia, iy] - 1]
                    * dCondLength[ia, iy]
                    * self.dEconomic_Factor
                    / 1000000.0
                )

                # Roughness
                if iy > 0:
                    dYearRoughness = self.calculate_next_year_roughness(
                        dYearRoughness, iYearAge, ia, iy, iTemperature, iMoisture, dCondSNC, dESATotal, iCondSurface
                    )
                    max_roughness = 25.0 if iCondSurface[ia, iy] in (4, 5) else 16.0
                    dYearRoughness = min(max_roughness, dYearRoughness)

                iYearAge = iYearAge + 1

                if iy == work_year - 1:
                    """
                    Rougnesss effect function of road work type
                    """
                    dYearRoughness = alt.iri
                    iYearAge = 1

                if (iy + 1) in repair_years:
                    dYearRoughness = repair_alt.iri
                    iYearAge = 1

                dCondIRI[ia, iy] = dYearRoughness
                iCondAge[ia, iy] = iYearAge

                # VOC
                dCostVOC[ia, iy] = 0
                lane_cond_idx = iCondLanes[ia, iy] - 1
                terrain_idx = iTerrain - 1
                iri2, iri3 = np.power(dYearRoughness, 2), np.power(dYearRoughness, 3)

                voc = (
                    self.dVOC[lane_cond_idx, terrain_idx, 0, :]
                    + (self.dVOC[lane_cond_idx, terrain_idx, 1, :] * dYearRoughness)
                    + (self.dVOC[lane_cond_idx, terrain_idx, 2, :] * iri2)
                    + (self.dVOC[lane_cond_idx, terrain_idx, 3, :] * iri3)
                ) * dAADT[0:12, iy]
                dCostVOC[ia, iy] = voc.sum() * dCondLength[ia, iy] * 365 / 1000000

                # Speed
                speed = (
                    self.dSPEED[lane_cond_idx, terrain_idx, 0, :]
                    + (self.dSPEED[lane_cond_idx, terrain_idx, 1, :] * dYearRoughness)
                    + (self.dSPEED[lane_cond_idx, terrain_idx, 2, :] * iri2)
                    + (self.dSPEED[lane_cond_idx, terrain_idx, 3, :] * iri3)
                )

                dCondSpeed[ia, iy, :] = speed
                dCondSpeedAve[ia, iy] = speed.sum() / 12

                dCostTime[ia, iy] = (
                    1
                    / speed
                    * dCondLength[ia, iy]
                    * self.dVehicleFleet[:, 1]
                    * self.dVehicleFleet[:, 2]
                    * dAADT[:-1, iy]
                    * 365
                    / 1000000
                ).sum()

                # Pavement Condition Class function of rougness
                dCondCON[ia, iy] = cc_from_iri_lu[iSurfaceType](dCondIRI[ia, iy])
                dCostRecurrentFin[ia, iy] = dCostRecurrentFin[ia, iy] * dRecMult[dCondCON[ia, iy] - 1]
                dCostRecurrentEco[ia, iy] = dCostRecurrentEco[ia, iy] * dRecMult[dCondCON[ia, iy] - 1]

                # road agency costs
                dCostAgencyFin[ia, iy] = dCostCapitalFin[ia, iy] + dCostRepairFin[ia, iy] + dCostRecurrentFin[ia, iy]
                dCostAgencyEco[ia, iy] = dCostCapitalEco[ia, iy] + dCostRepairEco[ia, iy] + dCostRecurrentEco[ia, iy]

                # Users and Total
                dCostUsers[ia, iy] = dCostVOC[ia, iy] + dCostTime[ia, iy]
                dCostTotal[ia, iy] = dCostAgencyEco[ia, iy] + dCostUsers[ia, iy]

                # Net Benefits
                dNetTotal[ia, iy] = dCostTotal[0, iy] - dCostTotal[ia, iy]

                # NPV
                # Serious Note: raise to the power iy not (iy - 1) in the following equation
                dSolNPV[ia] = dSolNPV[ia] + dNetTotal[ia, iy] / ((1 + self.dDiscount_Rate) ** (iy))
                dSolNPVKm[ia] = dSolNPV[ia] / dCondLength[ia, 0]

                if dSolCost[ia] > 0:
                    dSolNPVCost[ia] = dSolNPV[ia] / dSolCost[ia]
                else:
                    dSolNPVCost[ia] = 0
            # End loop iy

            if dSolNPV[ia] >= dNPVMax:
                iTheSelected = ia
                dNPVMax = dSolNPV[ia]

        ###########################################################
        # Get the output results
        ###########################################################
        results = {
            "work_class": sSolClass[iTheSelected],
            "work_type": sSolCode[iTheSelected],
            "work_name": sSolName[iTheSelected],
            "work_cost": dSolCost[iTheSelected],
            "work_cost_km": dSolCostkm[iTheSelected],
            "work_year": int(iSolYear[iTheSelected]),
            "npv": dSolNPV[iTheSelected],
            "npv_km": dSolNPVKm[iTheSelected],
            "npv_cost": dSolNPVCost[iTheSelected],
            "eirr": irr(dNetTotal[iTheSelected]),
            "aadt": dAADT[12].tolist(),
            "truck_percent": dTRucks,
            "vehicle_utilization": dUtilization,
            "esa_loading": dESATotal[0],
            "iri_projection": dCondIRI[iTheSelected].tolist(),
            "iri_base": dCondIRI[0].tolist(),
            "con_projection": dCondCON[iTheSelected].tolist(),
            "con_base": dCondCON[0].tolist(),
            "financial_recurrent_cost": dCostRecurrentFin[iTheSelected].tolist(),
            "net_benefits": dNetTotal[iTheSelected].tolist(),
            "orma_way_id": section.orma_way_id,
        }
        return CbaResult(results)

    # This converts the surface type, road class condition class into an index offset into the dWorkEvaluated array
    # There are 5 unique condition classes, 10 road classes which defines the math below
    def get_work_evalauted_index(self, iSurfaceType, iRoadClass, iConditionClass):
        return (iSurfaceType - 1) * 50 + (iRoadClass - 1) * 5 + iConditionClass - 1

    def compute_alternatives(self, iSurfaceType, iRoadClass, iConditionClass):
        iNoAlernatives = 0
        dAlternatives = np.zeros((13, 2), dtype=np.float64)

        # Get initial road work for the 13 alternatives
        work_index = self.get_work_evalauted_index(iSurfaceType, iRoadClass, iConditionClass)
        work_year, road_work_number, alt_1, alt_2, _unit_cost_mult = self.dWorkEvaluated[work_index]

        dAlternatives[0, 0] = road_work_number
        dAlternatives[1:7, 0] = alt_1
        dAlternatives[7:13, 0] = alt_2

        # Define years of initial works for 13 alternatives
        dAlternatives[0, 1] = work_year

        if dAlternatives[1, 0] > 0:  # first road work defined: evaluate at least 7 alternatives
            dAlternatives[1:7, 1] = [1, 2, 3, 4, 5, 6]
            iNoAlernatives = 7

        if dAlternatives[7, 0] > 0:  # second road work defined: evaluate 13 alternatives
            dAlternatives[7:13, 1] = [1, 2, 3, 4, 5, 6]
            iNoAlernatives = 13

        if dAlternatives[1, 0] == 0 and dAlternatives[7, 0] == 0:  # no road works defined: evaluate 2 base alternatives
            dAlternatives[1, 0] = road_work_number
            dAlternatives[1, 1] = work_year
            iNoAlernatives = 2

        return iNoAlernatives, dAlternatives

    def compute_cost_factor(self, iSurfaceType, iRoadClass, iConditionClass):
        baz = iConditionClass - 1
        return self.dWorkEvaluated[(iSurfaceType - 1) * 50 + (iRoadClass - 1) * 5 + baz, 4]

    def calculate_next_year_roughness(
        self, dYearRoughness, iYearAge, ia, iy, iTemperature, iMoisture, dCondSNC, dESATotal, iCondSurface
    ):
        """
        Rougnesss progression function of surface type
        """

        surface_condition = iCondSurface[ia, iy]
        foo, const, Kgp, Kgm, a0, a1, a2 = self.dRoadDet[surface_condition - 1, 0:7]
        # print(ia, iy, surface_condition, foo, const, Kgp, Kgm, a0, a1, a2)

        # Surface condition classes 1,4,5,6,7 always use constant deterioration factors
        # classes 2 & 3 use them when the FOO is 1
        if surface_condition in (1, 4, 5, 6, 7) or foo == float(1):
            return dYearRoughness * (1 + const)

        # otherwise the surface_condition is either 2 or 3
        moisture_coeff = self.dm_coeff[iTemperature - 1, iMoisture - 1]

        if foo == float(3):  # Climate Related Only
            return dYearRoughness * (1 + moisture_coeff)

        if foo == float(2):
            # HDM-4 Simplified Equation:
            # RIb = RIa + Kgp * (a0 * Exp (Kgm * m * AGE3) * [(1 + SNC * a1)]-5 * YE4 + a2 * AGE3) + (Kgm *m * RIa)
            snc = dCondSNC[ia, iy]
            ye4 = dESATotal[iy]
            return dYearRoughness + (
                Kgp
                * (a0 * np.exp(Kgm * moisture_coeff * iYearAge) * np.power((1 + snc * a1), -5) * ye4 + a2 * iYearAge)
                + (Kgm * moisture_coeff * dYearRoughness)
            )

    def compute_annual_traffic(self, dAADT, iGrowthScenario):

        idx = iGrowthScenario - 1
        growth_factor = 1.0 + self.dGrowth[idx : idx + 1, :]

        # Use numpy cumumlative sum to calculate the growth into the next 20 years
        dAADT[0:12, 1:20] = growth_factor.T
        np.cumprod(dAADT[0:12, :], axis=1, out=dAADT[0:12, :])

        # Calculate the total AADT over all the vehicle classes
        dAADT[12, :].fill(0)
        dAADT[12, :] = dAADT.sum(axis=0)

        return dAADT

    def compute_esa_loading(self, dAADT, iLanes):
        annualisation_factor = 365 / 1000000 / self.dWidthDefaults[iLanes - 1, 1]
        # calculate the sumproduct of traffic volumes with their equivalent standard axle weightings
        return np.sum(dAADT[0:12, :] * self.dVehicleFleet[0:12, 0:1], axis=0) * annualisation_factor

    def compute_trucks_percent(self, dAADT):
        return np.sum(dAADT[5:9, 0]) / dAADT[12, 0]

    def compute_vehicle_utilization(self, dAADT, dLength):
        return dAADT[12, 0] * dLength * 365 / 1000000

    def fill_defaults(self, section: Section) -> Section:
        if section.road_type == 0 and section.surface_type == 0:
            raise ValueError("Must define either road type or road surface type")
        if section.surface_type == 0:
            section.surface_type = iSurfaceDefaults[section.road_type]
        if section.road_type == 0:
            if section.surface_type in (4, 5):
                section.road_type = 2
            else:
                section.road_type = 1

        # Width and Number of Lanes Class
        if section.width == 0 and section.lanes == 0:
            raise ValueError("Must define either road width or number of lanes")
        if section.width == 0:
            section.width = dWidthDefaults(section.lanes, 1)
        if section.lanes == 0:
            section.lanes = self.get_default_lanes(section.width)

        # Roughness, Pavement Age and Road Condition
        if section.roughness == 0 and section.condition_class == 0:
            raise ValueError("Must define either roughness or road condition class")
        if section.condition_class == 0:
            section.condition_class = int(cc_from_iri_lu[section.surface_type](section.roughness))
        roughness, pavement_age = dConditionData[section.surface_type - 1, section.condition_class - 1]
        if section.roughness == 0:
            section.roughness = roughness
        if section.pavement_age == 0:
            section.pavement_age = pavement_age
        if section.structural_no == 0:
            if section.surface_type < 4:
                section.structural_no = dTrafficLevels(section.traffic_level, 13 + section.condition_class)

        # Traffic Level and Traffic Data
        if section.traffic_level == 0 and section.aadt_total == 0:
            raise ValueError("Must define either traffic level class or traffic data")

        if section.aadt_total == 0:
            # print(section.get_aadts())
            section.aadt_total = dTrafficLevels[section.traffic_level - 1, 0]
            # print(section.aadt_total)
            proportions = dTrafficLevels[section.traffic_level - 1, 1:13]
            # print(proportions, sum(proportions))
            section.set_aadts(proportions * section.aadt_total)
            # print(section.traffic_level, section.get_aadts(), sum(section.get_aadts()))

        calc_aadt_total = sum(section.get_aadts())
        if calc_aadt_total != section.aadt_total:
            raise ValueError(f"Sum of veh. class AADT ({calc_aadt_total}) != total AADT ({section.aadt_total})")

        if section.traffic_level == 0:
            section.traffic_level = traffic_range_lu(section.aadt_total)

        return section

    def get_default_lanes(self, width):
        return lanes_lu(width)
