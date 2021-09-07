from mcconv.eic_smear_reader import EicSmearEventData
from pyHepMC3 import HepMC3 as hm


def eic_smear_to_hepmc(hepmc_evt, source_evt, rules, beam_particles):
    """

    """
    assert isinstance(source_evt, EicSmearEventData)

    v1 = hm.GenVertex()
    hepmc_evt.add_vertex(v1)

    # particles = parse_lund_particles(unparsed_event)
    for particle in source_evt.particles:

        # Create a hepmc particle
        hm_particle = hm.GenParticle(hm.FourVector(particle.px, particle.py, particle.pz, particle.energy),
                                     particle.pid,
                                     particle.status)

        # Add particle to event
        hepmc_evt.add_particle(hm_particle)

        # Event particle
        if(hm_particle.status() == 4):
            v1.add_particle_in(hm_particle)
        else:
            v1.add_particle_out(hm_particle)

    return hepmc_evt