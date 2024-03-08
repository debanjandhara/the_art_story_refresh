import csv
from datetime import datetime



# Function to add a new record to the CSV file
def add_record(record):
    csv_file = 'database.csv'
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(record)

# Function to read all records from the CSV file
def read_records():
    csv_file = 'database.csv'
    with open(csv_file, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        records = list(reader)
    return records


# Adding a new record
# record_to_add = ['Type1', 'ID001', str(datetime.now()), str(datetime.now()), str(datetime.now())]

# record_to_add = ['Type', 'ID', 'last_checked', 'last_modified', 'last_vectorised', 'merged/not-merged']

# add_record(csv_file_path, record_to_add)

# Reading all records
# read_records(csv_file_path)



def update_record(record_id, new_value, column_index):
    csv_file = 'database.csv'
    records = read_records()

    for record in records:
        if record[1] == record_id:  # Assuming ID is in the second column
            record[column_index] = new_value
            break

    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # print("---writer enabled---")
        # print(records)
        writer.writerows(records)

def is_value_in_csv(target_value):
    csv_file = 'database.csv'
    with open(csv_file, 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            if target_value in row:
                return True
    return False



# # Example usage
# csv_file_path = 'database.csv'
# record_id_to_update = '02'
# new_last_modified_value = 'merged'
# column_index_to_update = 5  # Assuming 'last modified' is the fourth column (index 3)

# # # Update a single value in the record with the specified ID
# update_record(csv_file_path, record_id_to_update, new_last_modified_value, column_index_to_update)

# update_record("sosaku_hanga_creative_prints", "sōsaku-hanga creative prints", 5)