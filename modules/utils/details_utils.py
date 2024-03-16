from modules.utils.csv_utils import generateCSV, populateCSVRowDict
import os, logging

logger = logging.getLogger()

def saveCSV(details: dict[str, any], output_dir: str):

    if not details: return

    output_dir = os.path.join(output_dir, "csv")

    if not os.path.exists(output_dir): os.makedirs(output_dir)

    POLII_items = dict(details["POLII"]["items"])
    license_no = POLII_items["Licence No."]

    csv_header_list = POLII_items.keys()
    csv_row_dict = POLII_items
    generateCSV(csv_header_list, csv_row_dict, os.path.join(output_dir, 'polii.csv'))

    csv_row_dict = {"License No.": license_no}
    for title in ("AWCAP", "PL", "COL", "PDAL5", "N"):
        table = details.get(title)
        header_columns = table['header_columns']
        data_rows = table['data_rows']

        if len(data_rows) == 0: continue

        csv_row_dict.update({header_column: "" for header_column in header_columns})
        csv_row_dict_keys = list(csv_row_dict.keys())

        populateCSVRowDict(license_no, csv_row_dict_keys, csv_row_dict, data_rows, is_multirow = title == 'PL')
        generateCSV(csv_row_dict_keys, csv_row_dict, os.path.join(output_dir, f"{title.lower()}.csv"))

    csv_header_list = ["License No.", "Remark",]
    csv_row_dict = {"License No.": license_no, "Remark": "\n".join([f"{number}. {value}\n" for number, value in enumerate(details["R"]["items"], start=1)])}
    generateCSV(csv_header_list, csv_row_dict, os.path.join(output_dir, 'r.csv'))
