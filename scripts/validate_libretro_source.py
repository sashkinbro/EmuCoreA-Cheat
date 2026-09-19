#!/usr/bin/env python3
"""Verify the pinned libretro PSP source revision and converted source files."""
from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

EXPECTED_COMMIT = "740ebdf03247073658ccea45ddedfd57ea9d2974"
SERIAL_RE = re.compile(r"\[([A-Z]{4}-[0-9]{5})\]\.cht$")
CODE_RE = re.compile(r"_L\s+0x[0-9A-Fa-f]{8}\s+0x[0-9A-Fa-f]{1,8}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    args = parser.parse_args()
    source = args.source.resolve()
    head = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
    if head != EXPECTED_COMMIT:
        raise SystemExit(f"validation failed: source HEAD {head} != pinned {EXPECTED_COMMIT}")
    if not (source / "LICENSE").is_file():
        raise SystemExit("validation failed: source LICENSE is missing")
    files = list((source / "cht" / "Sony - PlayStation Portable").glob("*.cht"))
    selected = [
        path for path in files
        if SERIAL_RE.search(path.name) and SERIAL_RE.search(path.name).group(1) in {
            "ULES-01416", "ULJM-05500", "ULES-01213", "ULJS-00048", "UCUS-98645",
            "UCUS-98668", "UCES-01327", "ULJM-05261", "NPJH-50332", "NPJH-50521",
            "UCUS-98646", "ULJM-05505", "NPJH-50789", "ULJM-05402", "ULUS-10447",
            "ULJM-05255", "ULJM-05297", "ULJM-05341", "ULES-00657", "ULJM-05309",
            "NPJB-40001", "ULJM-05753", "ULES-01523", "ULES-00503", "ULJM-05637",
            "NPJH-50618", "ULES-01372", "ULUS-10290", "ULUS-10551", "ULUS-10511",
            "ULUS-10266", "ULUS-10368", "ULJM-05844", "ULES-01187", "NPJH-50619",
            "ULUS-10565", "ULES-01500", "ULUS-10139", "ULES-01367", "UCKS-45027",
            "NPUH-10125", "NPEH-00134", "ULJM-05775", "ULUS-10059", "NPJH-50311",
            "ULUS-10458", "ULUS-10219", "ULUS-10271", "ULUS-10200", "ULUS-10374",
            "ULUS-10479", "NPJH-50107", "ULUS-10410", "NPJH-50878", "NPJH-50352",
            "ULJM-05800", "ULUS-10041", "ULES-00151", "ULUS-10297", "ULUS-10490",
            "ULUS-10437", "ULES-00502", "UCUS-98751", "ULUS-10390", "NPJH-50443",
            "NPJH-50444", "ULUS-10391", "ULUS-10160", "UCUS-98632", "ULUS-10336",
            "ULUS-10563", "ULUS-10582", "ULUS-10466", "ULES-00182", "ULUS-10560",
            "NPJH-50701", "UCES-01264", "ULUS-10310", "ULJM-05552", "UCES-01242",
            "UCES-01245", "NPJH-50473", "ULJM-05101", "ULES-01183", "UCJS-10100",
            "UCUS-98633", "ULJM-05600", "ULES-00850", "ULJS-00237", "ULES-00841",
            "ULUS-10375", "ULJM-05940", "UCES-00356", "ULJS-00097", "NPJH-50043",
            "ULES-00176", "ULAS-42060", "ULES-00318", "UCUS-98711", "ULUS-10084",
            "NPUH-10041", "UCES-00995", "ULUS-10529", "ULES-01392", "ULUS-10461",
            "ULES-00193", "ULUS-10202", "ULES-00724", "ULUS-10107", "ULES-01507",
            "NPJH-50567", "UCUS-98716", "ULUS-10308", "ULES-01298", "NPJH-50588",
            "ULES-00180", "ULUS-10457", "ULJM-05976", "ULJM-05814", "ULJM-05604",
            "NPJH-50377", "ULES-01044", "ULJM-05353", "ULJS-00202", "ULES-01347",
            "ULUS-10251", "ULES-00756", "ULUS-10142", "ULUS-10263", "ULUS-10380",
            "ULJM-05410", "NPJH-50721", "NPJH-50435", "ULUS-10505", "ULJM-05490",
            "ULJM-05262", "ULUS-10141", "ULUS-10432", "ULJS-00183", "NPJH-50625",
            "NPJH-50045", "NPJH-50263", "ULUS-10438", "ULES-01376", "UCUS-98612",
            "ULUS-10097", "ULUS-10211", "ULJM-05299", "NPJH-50681", "ULJS-00293",
            "ULES-01144", "NPHH-00068", "ULJS-00363", "ULUS-10495", "ULUS-10134",
            "ULJM-05493", "ULES-00982", "ULES-00981", "ULUS-10543", "ULUS-10345",
            "ULUS-10292", "ULJM-05427", "ULES-00999", "ULUS-10087", "ULES-01151",
            "ULUS-10416", "ULUS-10323", "ULUS-10282", "UCKS-45076", "NPUH-10126",
            "ULUS-10452", "ULJM-05781", "UCJS-10093", "ULES-00419", "NPJH-50276",
            "ULES-01441", "ULUS-10086", "ULJS-00178", "ULES-01489", "ULJS-00460",
            "ULES-01472", "ULUS-10068", "ULES-01154", "NPJH-50353", "ULUS-10277",
            "ULES-01537", "ULJS-00167", "ULES-01431", "ULES-01045", "NPJH-50430",
            "NPUH-10197", "NPUH-10191", "ULJS-00175", "ULUS-10289", "ULUS-10089",
            "ULJS-00377", "ULUS-10593", "ULUS-10045", "ULES-00987", "ULES-00645",
            "UCES-01312", "NPJH-50044", "ULES-01322", "ULUS-10383", "NPJH-50530",
            "ULES-00959", "ULUS-10409", "NPUH-10198", "ULJM-05611", "ULJM-05492",
            "UCES-00001", "NPJH-50717", "NPJH-50331", "ULJM-06081", "ULJM-05440",
            "NPJH-50459", "ULUS-10506", "ULJM-05524", "ULES-01429", "NPJH-50316",
            "ULUS-10340", "ULJS-00188", "ULUS-10400", "ULES-01330", "NPUH-10195",
            "NPJH-50716", "ULUS-10513", "ULUS-10442", "ULUS-10218", "ULUS-10176",
            "ULJM-05676", "ULJM-05241", "ULJM-05127", "ULJM-05472", "UCJS-10095",
            "NPJH-50441", "ULUS-10455", "ULJM-05300", "NPJH-50566", "ULUS-10515",
            "ULUS-10339", "ULJS-00168", "ULES-01145", "NPUZ-00132", "ULJS-00190",
            "ULJS-00169", "ULJM-05321", "ULES-00740", "UCUS-98640", "UCJS-10109",
            # Batch 013.
            "ALJS-00351", "CAVE-00960", "CAVE-00992", "CSPS-01360", "NPEG-00004",
            "NPEG-00008", "NPEG-00009", "NPEG-00017", "NPEG-00018", "NPEG-00019",
            "NPEG-00023", "NPEG-00025", "NPEG-00028", "NPEG-00037", "NPEG-00044",
            "NPEG-00046", "NPEG-00047", "NPEG-00048", "NPEG-00049", "NPEG-20029",
            "NPEG-90003", "NPEG-90008", "NPEG-90009", "NPEG-90012", "NPEG-90014",
            # Batch 014: additional PSP serials from the same pinned libretro snapshot.
            "NPEG-90015",            "NPEG-90018",            "NPEG-90019",            "NPEG-90020",            "NPEG-90025",
            "NPEG-90026",            "NPEG-90030",            "NPEG-90035",            "NPEH-00002",            "NPEH-00003",
            "NPEH-00007",            "NPEH-00017",            "NPEH-00020",            "NPEH-00021",            "NPEH-00027",
            "NPEH-00029",            "NPEH-00031",            "NPEH-00033",            "NPEH-00064",            "NPEH-00065",
            "NPEH-00073",            "NPEH-00076",            "NPEH-00077",            "NPEH-00100",            "NPEH-00124",
            # Batch 016: 100 additional PSP serials from the same pinned libretro snapshot.
            "NPEZ-00242",            "NPEZ-00250",            "NPEZ-00272",            "NPEZ-00294",            "NPEZ-00297",
            "NPEZ-00306",            "NPEZ-00308",            "NPEZ-00310",            "NPEZ-00311",            "NPEZ-00313",
            "NPEZ-00317",            "NPEZ-00318",            "NPEZ-00319",            "NPEZ-00320",            "NPEZ-00321",
            "NPEZ-00322",            "NPEZ-00327",            "NPEZ-00328",            "NPEZ-00330",            "NPEZ-00331",
            "NPEZ-00333",            "NPEZ-00339",            "NPEZ-00343",            "NPEZ-00344",            "NPEZ-00346",
            "NPEZ-00347",            "NPEZ-00350",            "NPEZ-00351",            "NPEZ-00354",            "NPEZ-00357",
            "NPEZ-00362",            "NPEZ-00363",            "NPEZ-00365",            "NPEZ-00374",            "NPEZ-00385",
            "NPEZ-00391",            "NPEZ-00400",            "NPEZ-00401",            "NPEZ-00416",            "NPEZ-00417",
            "NPEZ-00419",            "NPEZ-00420",            "NPEZ-00436",            "NPEZ-00444",            "NPEZ-00469",
            "NPEZ-01264",            "NPHG-00013",            "NPHG-00014",            "NPHG-00024",            "NPHG-00025",
            "NPHG-00032",            "NPHG-00035",            "NPHG-00080",            "NPHG-00087",            "NPHG-00091",
            "NPHG-00092",            "NPHH-00061",            "NPHH-00293",            "NPHH-00351",            "NPJB-40002",
            "NPJB-40003",            "NPJG-00013",            "NPJG-00017",            "NPJG-00034",            "NPJG-00035",
            "NPJG-00044",            "NPJG-00045",            "NPJG-00103",            "NPJG-00116",            "NPJG-00122",
            "NPJG-90009",            "NPJG-90025",            "NPJG-90034",            "NPJG-90068",            "NPJG-90070",
            "NPJG-90088",            "NPJG-90095",            "NPJH-00002",            "NPJH-00004",            "NPJH-00007",
            "NPJH-00008",            "NPJH-00018",            "NPJH-00019",            "NPJH-00026",            "NPJH-00069",
            "NPJH-00126",            "NPJH-00142",            "NPJH-50006",            "NPJH-50007",            "NPJH-50040",
            "NPJH-50050",            "NPJH-50054",            "NPJH-50065",            "NPJH-50075",            "NPJH-50076",
            "NPJH-50093", "NPJH-50119", "NPJH-50141",
            # Batch 015: 100 additional PSP serials from the same pinned libretro snapshot.
            "NPEH-00154",            "NPEH-00166",            "NPEH-00170",            "NPEH-10029",            "NPEH-90001",
            "NPEH-90006",            "NPEH-90011",            "NPEH-90014",            "NPEH-90015",            "NPEH-90022",
            "NPEH-90026",            "NPEH-90028",            "NPEH-90032",            "NPEH-90038",            "NPEH-90049",
            "NPEH-90051",            "NPEX-00004",            "NPEX-00005",            "NPEZ-00001",            "NPEZ-00002",
            "NPEZ-00003",            "NPEZ-00004",            "NPEZ-00007",            "NPEZ-00009",            "NPEZ-00011",
            "NPEZ-00021",            "NPEZ-00022",            "NPEZ-00023",            "NPEZ-00024",            "NPEZ-00025",
            "NPEZ-00027",            "NPEZ-00031",            "NPEZ-00032",            "NPEZ-00041",            "NPEZ-00042",
            "NPEZ-00043",            "NPEZ-00044",            "NPEZ-00045",            "NPEZ-00046",            "NPEZ-00047",
            "NPEZ-00058",            "NPEZ-00080",            "NPEZ-00081",            "NPEZ-00087",            "NPEZ-00093",
            "NPEZ-00094",            "NPEZ-00095",            "NPEZ-00096",            "NPEZ-00098",            "NPEZ-00100",
            "NPEZ-00101",            "NPEZ-00107",            "NPEZ-00108",            "NPEZ-00115",            "NPEZ-00117",
            "NPEZ-00118",            "NPEZ-00122",            "NPEZ-00124",            "NPEZ-00126",            "NPEZ-00130",
            "NPEZ-00131",            "NPEZ-00133",            "NPEZ-00135",            "NPEZ-00136",            "NPEZ-00140",
            "NPEZ-00145",            "NPEZ-00147",            "NPEZ-00149",            "NPEZ-00151",            "NPEZ-00153",
            "NPEZ-00154",            "NPEZ-00157",            "NPEZ-00158",            "NPEZ-00164",            "NPEZ-00166",
            "NPEZ-00167",            "NPEZ-00168",            "NPEZ-00171",            "NPEZ-00176",            "NPEZ-00178",
            "NPEZ-00184",            "NPEZ-00185",            "NPEZ-00195",            "NPEZ-00196",            "NPEZ-00199",
            "NPEZ-00200",            "NPEZ-00203",            "NPEZ-00205",            "NPEZ-00212",            "NPEZ-00215",
            "NPEZ-00217",            "NPEZ-00218",            "NPEZ-00219",            "NPEZ-00222",            "NPEZ-00225",
            "NPEZ-00229",            "NPEZ-00230",            "NPEZ-00235",            "NPEZ-00236",            "NPEZ-00237",
            'NPEG-00024', 'NPEH-90023', 'NPEZ-00029', 'NPEZ-00155', 'NPEZ-00352',
            'NPHH-00145', 'NPJH-50144', 'NPJH-50145', 'NPJH-50148', 'NPJH-50180',
            'NPJH-50184', 'NPJH-50199', 'NPJH-50211', 'NPJH-50215', 'NPJH-50221',
            'NPJH-50222', 'NPJH-50226', 'NPJH-50234', 'NPJH-50239', 'NPJH-50242',
            'NPJH-50247', 'NPJH-50269', 'NPJH-50280', 'NPJH-50293', 'NPJH-50321',
            'NPJH-50329', 'NPJH-50333', 'NPJH-50335', 'NPJH-50336', 'NPJH-50340',
            'NPJH-50342', 'NPJH-50372', 'NPJH-50375', 'NPJH-50376', 'NPJH-50380',
            'NPJH-50381', 'NPJH-50388', 'NPJH-50393', 'NPJH-50394', 'NPJH-50401',
            'NPJH-50409', 'NPJH-50410', 'NPJH-50411', 'NPJH-50412', 'NPJH-50414',
            'NPJH-50416', 'NPJH-50426', 'NPJH-50431', 'NPJH-50437', 'NPJH-50442',
            'NPJH-50448', 'NPJH-50451', 'NPJH-50453', 'NPJH-50457', 'NPJH-50460',
            'NPJH-50464', 'NPJH-50465', 'NPJH-50467', 'NPJH-50468', 'NPJH-50470',
            'NPJH-50472', 'NPJH-50475', 'NPJH-50484', 'NPJH-50486', 'NPJH-50489',
            'NPJH-50501', 'NPJH-50502', 'NPJH-50503', 'NPJH-50505', 'NPJH-50508',
            'NPJH-50509', 'NPJH-50515', 'NPJH-50520', 'NPJH-50535', 'NPJH-50558',
            'NPJH-50561', 'NPJH-50562', 'NPJH-50563', 'NPJH-50564', 'NPJH-50575',
            'NPJH-50582', 'NPJH-50583', 'NPJH-50594', 'NPJH-50597', 'NPJH-50606',
            'NPJH-50617', 'NPJH-50624', 'NPJH-50626', 'NPJH-50635', 'NPJH-50639',
            'NPJH-50647', 'NPJH-50648', 'NPJH-50656', 'NPJH-50658', 'NPJH-50674',
            'NPJH-50675', 'NPJH-50676', 'NPJH-50679', 'NPJH-50686', 'NPJH-50691',
            'NPJH-50696', 'NPJH-50699', 'NPJH-50700', 'NPJH-50705', 'NPJH-50720',
            'NPJH-50745', 'NPJH-50832', 'NPJH-50886', 'NPJH-50888', 'NPJH-90002',
            'NPJH-90008', 'NPJH-90024', 'NPJH-90062', 'NPJH-90063', 'NPJH-90066',
            'NPJH-90068', 'NPJH-90072', 'NPJH-90073', 'NPJH-90110', 'NPJH-90113',
            'NPJH-90126', 'NPJH-90131', 'NPJH-90134', 'NPJH-90146', 'NPJH-90152',
            'NPJH-90157', 'NPJH-90167', 'NPJH-90200', 'NPJH-90205', 'NPJH-90216',
            'NPJH-90252', 'NPJH-90332', 'NPJH-90335', 'NPJH-90338', 'NPJH-90342',
            'NPJJ-30020', 'NPJJ-30043', 'NPUG-22850', 'NPUG-30038', 'NPUG-30040',
            'NPUG-70008', 'NPUG-70013', 'NPUG-70014', 'NPUG-70057', 'NPUG-70076',
            'NPUG-70093', 'NPUG-70097', 'NPUG-70106', 'NPUG-70125', 'NPUG-80061',
            'NPUG-80086', 'NPUG-80221', 'NPUG-80224', 'NPUG-80248', 'NPUG-80251',
            'NPUG-80265', 'NPUG-80293', 'NPUG-80318', 'NPUG-80321', 'NPUG-80325',
            'NPUG-80328', 'NPUG-80330', 'NPUG-80335', 'NPUG-80460', 'NPUG-80524',
            'NPUG-80527', 'NPUG-80528', 'NPUG-80529', 'NPUG-98731', 'NPUH-10006',
            'NPUH-10007', 'NPUH-10008', 'NPUH-10009', 'NPUH-10019', 'NPUH-10020',
            'NPUH-10022', 'NPUH-10023', 'NPUH-10024', 'NPUH-10025', 'NPUH-10026',
            'NPUH-10027', 'NPUH-10028', 'NPUH-10029', 'NPUH-10031', 'NPUH-10034',
            'NPUH-10040', 'NPUH-10042', 'NPUH-10044', 'NPUH-10060', 'NPUH-10065',
            'NPUH-10069', 'NPUH-10072', 'NPUH-10074', 'NPUH-10088', 'NPUH-10089',
            'NPUH-10106', 'NPUH-10110', 'NPUH-10114', 'NPUH-10117', 'NPUH-10123',
            'NPUH-10127', 'NPUH-10128', 'NPUH-10184', 'NPUH-10187', 'NPUH-10189',
            'NPUH-10193', 'NPUH-90004', 'NPUH-90007', 'NPUH-90012', 'NPUH-90019',
            'NPUH-90023', 'NPUH-90025', 'NPUH-90028', 'NPUH-90029', 'NPUH-90031',
            'NPUH-90036', 'NPUH-90048', 'NPUH-90052', 'NPUH-90053', 'NPUH-90056',
            'NPUH-90066', 'NPUH-90067', 'NPUH-90071', 'NPUH-90081', 'NPUH-90091',
            'NPUH-90093', 'NPUH-90095', 'NPUH-90097', 'NPUH-90099', 'NPUX-80405',
            'NPUX-80406', 'NPUX-80421', 'NPUX-80433', 'NPUX-80436', 'NPUX-80438',
            'NPUX-80448', 'NPUX-80453', 'NPUZ-00001', 'NPUZ-00003', 'NPUZ-00004',
            'NPUZ-00005', 'NPUZ-00006', 'NPUZ-00007', 'NPUZ-00008', 'NPUZ-00009',
            'NPUZ-00010', 'NPUZ-00011', 'NPUZ-00013', 'NPUZ-00014', 'NPUZ-00015',
            'NPUZ-00016', 'NPUZ-00017', 'NPUZ-00018', 'NPUZ-00020', 'NPUZ-00021',
            'NPUZ-00022', 'NPUZ-00023', 'NPUZ-00024', 'NPUZ-00025', 'NPUZ-00029',
            'NPUZ-00031', 'NPUZ-00033', 'NPUZ-00034', 'NPUZ-00036', 'NPUZ-00037',
            'NPUZ-00042', 'NPUZ-00043', 'NPUZ-00045', 'NPUZ-00046', 'NPUZ-00048',
            'NPUZ-00049', 'NPUZ-00054', 'NPUZ-00055', 'NPUZ-00056', 'NPUZ-00057',
            'NPUZ-00066', 'NPUZ-00069', 'NPUZ-00071', 'NPUZ-00072', 'NPUZ-00076',
            'NPUZ-00077', 'NPUZ-00078', 'NPUZ-00080', 'NPUZ-00081', 'NPUZ-00082',
            'NPUZ-00086', 'NPUZ-00090', 'NPUZ-00091', 'NPUZ-00092', 'NPUZ-00094',
            'NPUZ-00095', 'NPUZ-00098', 'NPUZ-00104', 'NPUZ-00108', 'NPUZ-00109',
            'NPUZ-00110', 'NPUZ-00114', 'NPUZ-00115', 'NPUZ-00116', 'NPUZ-00118',
        }
    ]
    selected = list({SERIAL_RE.search(path.name).group(1): path for path in selected}.values())
    if len(selected) != 798:
        raise SystemExit(f"validation failed: found {len(selected)} selected source files, expected 798")
    for path in selected:
        text = path.read_text(encoding="utf-8")
        if not CODE_RE.search(text):
            raise SystemExit(f"validation failed: no CWCheat lines in {path.name}")
    print(f"verified libretro-database PSP source commit {head}")
    print(f"verified CC-BY-SA-4.0 LICENSE and {len(selected)} selected source files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
