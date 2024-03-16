import os, csv

def generateCSV(header: list, row: dict, output_filename: str) -> None:

    output_file_path = os.path.dirname(output_filename)

    if not os.path.exists(output_file_path):
        os.makedirs(output_file_path)

    # Write data
    with open(os.path.join(output_filename), "a", newline='', encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=header)
        if file.tell() == 0: writer.writeheader()
        writer.writerow(row)

def populateCSVRowDict(
        license_no: str, 
        csv_header_list: list, 
        csv_row_dict: dict, 
        rows: list, 
        is_multirow: bool = False) -> None:
    """
    Populates the given dictionary to prepare for CSV generation.

    Args:
        csv_header_list (list): A list of header column names needed for the fieldnames when generating CSV.
        csv_row_dict (dict): A dictionary that holds the final row for generating CSV.
        rows (list): A list of rows containing values for the columns.
        is_multirow (bool): Flag indicating whether the current table row spans multiple rows in the CSV.

    Returns:
        None: The function updates the given dictionary directly.
    """

    # Include license number in the csv row dictionary
    column = csv_header_list[0]
    csv_row_dict[column] = license_no

    # Set the loop at index 3 if the current row in the table has multiple rows
    start_loop_index = 3 if is_multirow else 0

    # A flag for multiple rows
    multirow_flag = False

    # Iterate through the list of row values in tuples
    for row_values in rows:

        if is_multirow:
            # Add license number in the row values
            row_values = [license_no,] + row_values
            # The flag will be True if the columns at the beginning are blank strings
            multirow_flag = all(map(lambda index: row_values[index] == '', range(start_loop_index-1, 0, -1)))
            if multirow_flag is not True: 
                # If the current row does not have multple rows within it, directly populate the csv row dictionary with row values
                csv_row_dict.update(dict(zip(csv_header_list, row_values)))

        for index in range(start_loop_index, len(row_values)):
            # Increment the index by 1 if the current row does not have multiple rows
            column = csv_header_list[index + (1 if not is_multirow else 0)]
            value = row_values[index]
            csv_row_dict[column] += f"{value}\n" if multirow_flag or not is_multirow else "\n"