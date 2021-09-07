import logging
import time

from pyHepMC3 import HepMC3 as hm

from mcconv import detect_mc_type
from .eic_smear_to_hepmc import eic_smear_to_hepmc
from .formats.beagle import BeagleReader
from .generic_reader import GenericTextReader, UnparsedTextEvent
from .formats.lund import parse_lund_particles, parse_lund_particle_tokens
from .file_types import McFileTypes
from .eic_smear_reader import EicTreeReader, EicSmearEventData
from .hepmc_reader import HepMCReader
from .lund_to_hepmc import LUND_CONV_RULES, lund_to_hepmc

logger = logging.getLogger("mcconv.hepmc_convert")



def hepmc_convert(input_file, output_file, input_type, hepmc_vers=3, nskip=0, nprocess=0, begin_func=None, progress_func=None, transform_func=None, transform_args=None, reader=None, convert_func=None, convert_rules=None, beam_particles=None):

    # Choose the output format: hepmc 2 or 3 writer
    if hepmc_vers == 2 or hepmc_vers == "2" or (isinstance(hepmc_vers, str) and hepmc_vers.lower() == "hepmc2"):
        writer = hm.WriterAsciiHepMC2(output_file)
    else:
        writer = hm.WriterAscii(output_file)

    # What is the input type? Is it known?
    if not input_type or input_type == McFileTypes.UNKNOWN:
        logger.debug("Input file type is not given or UNKNOWN. Trying autodetect")

        # Input type is unknown, trying autodetection
        input_type = detect_mc_type(input_file)

    # If it is still UNKNOWN - we where unable to detect. Error raising
    if input_type == McFileTypes.UNKNOWN:
        raise ValueError("File format is UNKNOWN")

    # Create reusable hepmc event (hepmc readers may need it)
    hepmc_event = hm.GenEvent(hm.Units.GEV, hm.Units.MM)

    # Set event reader according to file type
    if not reader:
        if input_type == McFileTypes.EIC_SMEAR:
            reader = EicTreeReader()
        elif input_type == McFileTypes.HEPMC2:
            reader = HepMCReader(hepmc_event, 2)
        elif input_type == McFileTypes.HEPMC3:
            reader = HepMCReader(hepmc_event, 3)
        else:
            reader = GenericTextReader()
            if input_type == McFileTypes.BEAGLE:
                reader.particle_tokens_len = 18

    # Open input file
    reader.open(input_file)

    # This is basically the same as "with" statement. But HepMcWriter doesn't implement __enter__() etc.
    start_time = time.time()
    try:
        # call user function before iterating events
        if begin_func:
            begin_func(writer, reader, input_type)

        # Iterate events
        for evt_index, source_event in enumerate(reader.events(nskip, nprocess)):

            if convert_func:
                convert_func(evt_index, hepmc_event, source_event, rules=convert_rules, beam_particles=beam_particles)

            # What conversion function to use?
            if input_type == McFileTypes.EIC_SMEAR:
                # ROOT format EIC_SMEAR
                eic_smear_to_hepmc(hepmc_event, source_event, convert_rules, beam_particles=beam_particles)
            elif input_type in LUND_CONV_RULES.keys():
                # One of LUND formats
                lund_to_hepmc(hepmc_event, source_event, LUND_CONV_RULES[input_type], beam_particles=beam_particles)
            elif input_type == McFileTypes.USER and convert_rules:
                # User define conversion
                lund_to_hepmc(hepmc_event, source_event, convert_rules, beam_particles=beam_particles)

            # call transformation func (like boost or rotate)
            if transform_func:
                transform_func(evt_index, hepmc_event, transform_args)

            # Write event
            writer.write_event(hepmc_event)

            # call progress func, so one could work on it
            if progress_func:
                progress_func(evt_index, hepmc_event)

            hepmc_event.clear()
    finally:
        # closing everything (we are not using with statement as it is not supported by HepMC)
        writer.close()
        reader.close()
        hepmc_event.clear()
        logger.info(f"Time for the conversion = {time.time() - start_time} sec")

