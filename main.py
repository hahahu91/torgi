from inc.get_data import get_data_from_torgi_gov
from inc.analize_data import transform_into_flatter_structure
from inc.export_to_xlsx import export_to_xlsx
from inc.get_predicted import get_predicted
from get_population import get_from_kontur_population, get_population_from_osm, get_residence
from setting import SUBJ_RF

def main():
    #lotStatus=SUCCEED сбор завершенных данных; status = "APPLICATIONS_SUBMISSION прием заявок
    #subj_rf='1,2,3,5,10,11,13,14,18,19,20,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,44,45,46,47,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,66,68,69,70,71,72,73,74,76,77,78,79,86,89'
    amount_files=''
    status = "APPLICATIONS_SUBMISSION"
    folder = "cache/APPLICATIONS_SUBMISSION" if status != "SUCCEED" else "cache/SUCCEED"
    out_file = "torgi/output.xlsx" if status != "SUCCEED" else "torgi/output_archive.xlsx"
    subj_rf = ','.join(map(str, SUBJ_RF.keys())) if status == 'APPLICATIONS_SUBMISSION' else ""

    amount_files = get_data_from_torgi_gov(subj_rf=subj_rf,  lot_status=status, out_folder=folder)
    path = transform_into_flatter_structure(amount_files=3, folder=folder)
    export_to_xlsx(path, out_file)
    get_from_kontur_population(out_file)
    get_population_from_osm(out_file)
    get_predicted(out_file)

if __name__ == "__main__":
    main()