import copy
from pyHepMC3 import HepMC3 as hm
from mcconv import McFileTypes, UnparsedTextEvent


def add_hepmc_attribute(obj, name, str_value, val_type):
    if val_type == int:
        obj.add_attribute(name, hm.IntAttribute(int(str_value)))
    if val_type == float:
        obj.add_attribute(name, hm.FloatAttribute(float(str_value)))
    if val_type == str:
        obj.add_attribute(name, hm.StringAttribute(str_value))


LUND_RULES = {
    "px": 6,             # Column where px is stored
    "py": 7,             # Column where py is stored
    "pz": 8,             # Column where pz is stored
    "e": 9,              # Energy
    "pid": 2,            # PID of particle (PDG code)
    "status": 1,         # Status
    "evt_index": None,   # Event number (none = take io_event_number)
    "evt_weight": 9,     # Weight
    "evt_attrs": {},     # That is how one can store event level data
    "prt_attrs": {},     # Particle level data
    "beam_rule": "manual"
}

LUND_GEMC_RULES = {
    "px": 6,        # Column where px is stored
    "py": 7,        # Column where py is stored
    "pz": 8,        # Column where pz is stored
    "e": 9,         # Energy
    "pid": 3,       # PID of particle (PDG code)
    "status": 2,    # Status
    "evt_weight": 9,     # Weight
    "evt_attrs": {"weight": (9, float)},        # That is how one can store event level data
    "prt_attrs": {"life_time": (1, float)},     # In LUND GemC the second col. (index 1) is life time.
    # If that is need to be stored, that is how to store it
    "beam_rule": "manual"
}

BEAGLE_RULES = {
    "px": 6,             # Column where px is stored
    "py": 7,             # Column where py is stored
    "pz": 8,             # Column where pz is stored
    "e": 9,              # Energy
    "pid": 2,            # PID of particle (PDG code)
    "status": 1,         # Status
    "evt_index": 1,      # 2nd column
    "evt_weight": -5,    # Weight (5th column from the right)
    "evt_attrs": {"atarg": (4, float), "ztarg": (5, float)},     # That is how one can store event level data
    "prt_attrs": {},     # Particle level data
    "beam_rule": "manual"
}

PYTHIA6_EIC_RULES = copy.deepcopy(LUND_RULES)
PYTHIA6_EIC_RULES["beam_rule"] = "first_lines"
PYTHIA6_EIC_RULES["evt_index"] = 1

# A map of rules by HepMC
LUND_CONV_RULES = {
    McFileTypes.BEAGLE: BEAGLE_RULES,
    McFileTypes.LUND: LUND_RULES,
    McFileTypes.LUND_GEMC: LUND_GEMC_RULES,
    McFileTypes.PYTHIA6_EIC: PYTHIA6_EIC_RULES
}


def lund_to_hepmc(hepmc_evt, txt_event, rules, beam_particles=None):
    """
        Rules define columns, that are used for extraction of parameters

        rules = {
            "px": 6,        # Column where px is stored
            "py": 7,        # Column where py is stored
            "pz": 8,        # Column where pz is stored
            "e": 9,         # Energy
            "pid": 2,       # PID of particle (PDG code)
            "status": 1,    # Status
            "evt_attrs": {"weight": (9, float)},        # That is how one can store event level data
            "prt_attrs": {"life_time": (1, float)},     # In LUND GemC the second col. (index 1) is life time.
                                                        # If that is need to be stored, that is how to store it
            "beam_rule":  "manual"            # users must provide beam parameters through flags/arguments
        }
        rules["px"]
        rules["py"]
        rules["pz"]
        rules["e"]
        rules["pid"]
        rules["status"]
        rules["evt_attrs"]
        rules["prt_attrs"]

    """
    assert isinstance(txt_event, UnparsedTextEvent)

    prt_col_px = rules["px"]
    prt_col_py = rules["py"]
    prt_col_pz = rules["pz"]
    prt_col_e = rules["e"]
    prt_col_pid = rules["pid"]
    prt_col_status = rules["status"]
    evt_attrs = rules["evt_attrs"]
    prt_attrs = rules["prt_attrs"]
    prt_beam_rule = rules["beam_rule"]
    evt_weight = rules.get("evt_weight", None)
    evt_index_column = rules.get("evt_index", None)

    hepmc_evt.add_attribute("start_line_index", hm.IntAttribute(txt_event.start_line_index))

    v1 = hm.GenVertex()
    
    # do we have a manual beam particles? 
    
    if prt_beam_rule == "manual":

        # sanity check
        if not beam_particles:
            raise ValueError("For this type of text/lund file the beam information should be provided by user. "
                             "But it was not provided")

        # add user provided beam particles
        for beam_particle in beam_particles:
            px, py, pz, energy, pid = tuple(beam_particle)
            hm_beam_particle = hm.GenParticle(hm.FourVector(px, py, pz, energy), pid, 4)
            v1.add_particle_in(hm_beam_particle)
            hepmc_evt.add_particle(hm_beam_particle)

    # Add event level attributes
    for name, params in evt_attrs.items():
        column_index, field_type = params
        add_hepmc_attribute(hepmc_evt, name, txt_event.event_tokens[column_index], field_type)

    # Set event weight (if we have a column)
    if evt_weight:
        hepmc_evt.weights().append(float(txt_event.event_tokens[evt_weight]))

    # Set event number (if we have a column)
    if evt_index_column is not None:
        event_index = int(txt_event.event_tokens[evt_index_column])
    else:
        event_index = txt_event.io_event_index
    hepmc_evt.set_event_number(event_index)

    # particles = parse_lund_particles(unparsed_event)
    for particle_index, particle_line in enumerate(txt_event.unparsed_particles):

        # Parse main columns with 4 vectors
        px = float(particle_line[prt_col_px])
        py = float(particle_line[prt_col_py])
        pz = float(particle_line[prt_col_pz])
        energy = float(particle_line[prt_col_e])
        pid = int(particle_line[prt_col_pid])
        if isinstance(prt_col_status, (list, tuple)):
            # is it a tuple like
            status = prt_col_status[1](particle_index, particle_line[prt_col_status[0]])
        else:
            status = int(particle_line[prt_col_status])

        # Set beam particle status as 4 for the first 2 particles
        if prt_beam_rule == "first_lines" and particle_index in [0, 1]:
            status = 4

        # Take only final state particle
        if status not in [1, 4]:
            continue

        # Create a hepmc particle
        hm_beam_particle = hm.GenParticle(hm.FourVector(px, py, pz, energy), pid, status)

        hepmc_evt.add_particle(hm_beam_particle)

        # Add particle level attributes
        for name, params in prt_attrs.items():
            column_index, field_type = params
            add_hepmc_attribute(hm_beam_particle, name, particle_line[column_index], field_type)

        # Add particle to event
        if status == 4:
            # Beam particle
            v1.add_particle_in(hm_beam_particle)
        else:
            # All other particles
            v1.add_particle_out(hm_beam_particle)

    hepmc_evt.add_vertex(v1)
    return hepmc_evt