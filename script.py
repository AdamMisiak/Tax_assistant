import csv
import settings

def open_csv_file():
    rows = []
    with open(settings.DIVIDEND_FILE_CSV, 'r') as file:
        csvreader = csv.reader(file)
        header = next(csvreader)
        for row in csvreader:
            print(row)
            # rows.append(row)
    # print(header)
    # print(rows)


if __name__ == '__main__':
    open_csv_file()