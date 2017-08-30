from collections import OrderedDict
import struct

COLUMNS = ["pct_reflect", "tgt_count", "ref_count", "tgt_radiance",
           "ref_radiance", "tgt_irradiance", "ref_irradiance",
           "tgt_reflect", "ref_reflect"]
ASD_VERSIONS = ['ASD', 'asd', 'as6', 'as7', 'as8']
ASD_HAS_REF = {'ASD': False, 'asd': False, 'as6': True, 'as7': True,
               'as8': True}
ASD_DATA_TYPES = OrderedDict([("RAW_TYPE", "tgt_count"),
                              ("REF_TYPE", "tgt_reflect"),
                              ("RAD_TYPE", "tgt_radiance"),
                              ("NOUNITS_TYPE", None),
                              ("IRRAD_TYPE", "tgt_irradiance"),
                              ("QI_TYPE", None),
                              ("TRANS_TYPE", None),
                              ("UNKNOWN_TYPE", None),
                              ("ABS_TYPE", None)])
SED_COLUMNS = {
    "Wvl": "wavelength",
    "Rad. (Target)": "tgt_reflect",
    'Rad. (Ref.)': "ref_reflect",
    "Tgt./Ref. %": "pct_reflect",
    "Irrad. (Ref.)": "ref_irradiance",
    "Irrad. (Target)": "tgt_irradiance",
    "Reflect. %": "pct_reflect",
    "Reflect. [1.0]":"dec_reflect",
    "Chan.#":"channel_num",
}
ASD_GPS_DATA = struct.Struct("= 5d 2b cl 2b 5B 2c")

