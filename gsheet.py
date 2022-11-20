from typing import Any, List, Tuple, Union

import gspread

# TODO refactor strucutre of files and folders


class GoogleSheet:
    def __init__(self, worksheet: gspread.Worksheet, parameters: dict):
        self.worksheet = worksheet
        self.parameters = parameters
        self.sheet_data = self.worksheet.get_all_records(**self.parameters)
        self.headers = self.get_headers()
        self._batch = []

    def get_headers(self) -> List[str]:
        if len(self.sheet_data) == 0:
            return []
        return list(self.sheet_data[0].keys())

    def refresh_data(self) -> List[dict]:
        self.sheet_data = self.worksheet.get_all_records(**self.parameters)
        self.headers = self.get_headers()
        return self.sheet_data

    @staticmethod
    def _int_column_index_to_excel_index(header_index: int) -> str:
        """
        Function translating integer column notation to google column notation
        Examples:
            1 -> A
            2 -> B
            6 -> F
            27 -> AA
        """
        string = ""
        while header_index > 0:
            header_index, remainder = divmod(header_index - 1, 26)
            string = chr(65 + remainder) + string
        return string

    def _get_column_and_row_index(
        self, row_index: int, column_index: Union[int, str], python_dict_indexing: bool
    ) -> Tuple[int, int]:
        if isinstance(column_index, str):
            column_index = self.headers.index(column_index) + 1
        if python_dict_indexing:
            row_index += 2
        return row_index, column_index

    def write_to_cell(
        self,
        index: int,
        column: Union[int, str],
        value: Any,
        python_dict_indexing: bool = True,
    ):
        index, column = self._get_column_and_row_index(index, column, python_dict_indexing)
        self.worksheet.update_cell(index, column, value)

    def _create_batch_list(
        self,
        cell_list: List[Tuple[int, Union[int, str], Any]],
        python_dict_indexing: bool,
    ):
        batch_list = []
        for index, column, value in cell_list:
            index, column = self._get_column_and_row_index(index, column, python_dict_indexing)
            excel_column_format = self._int_column_index_to_excel_index(column)
            batch_list.append({"range": f"{excel_column_format}{index}", "values": [[value]]})
        return batch_list

    def batch_add_single_cell(
        self,
        index: int,
        column: Union[int, str],
        value: Any,
        python_dict_indexing: bool = True,
    ):
        self._batch += self._create_batch_list([(index, column, value)], python_dict_indexing=python_dict_indexing)

    def batch_add_multiple_cells(
        self,
        cell_list: List[Tuple[int, Union[str, int], Any]],
        python_dict_indexing: bool = True,
    ):
        self._batch += self._create_batch_list(cell_list, python_dict_indexing=python_dict_indexing)

    def execute_batch(
        self,
        value_input_option: str = "RAW",
        raise_error_on_empty_batch: bool = False,
    ) -> bool:
        if self._batch:
            self.worksheet.batch_update(self._batch, value_input_option=value_input_option)
            self._batch.clear()
            return True
        if raise_error_on_empty_batch:
            raise Exception()

        print("The google sheet cannot be updated. Batch list is empty")

        return False


class GoogleWorkbook:
    SCOPE = ["https://spreadsheets.google.com/feeds"]

    def __init__(self, credentials_json: dict, sheet_url: str, sheet_parameters: dict = None):
        self.credentials_json = credentials_json
        self.sheet_url = sheet_url
        self.workbook = self._get_workbook_object()
        self.parameters = sheet_parameters if sheet_parameters else {}
        self._sheets = {}

    def _get_workbook_object(self) -> gspread.Spreadsheet:
        google_client = gspread.service_account_from_dict(self.credentials_json, self.SCOPE)
        return google_client.open_by_url(url=self.sheet_url)

    def pull_sheet(self, sheet_name: str, parameters: dict = None) -> GoogleSheet:
        if not parameters:
            parameters = self.parameters
        if sheet_name in self._sheets:
            return self._sheets[sheet_name]
        self._sheets[sheet_name] = GoogleSheet(self.workbook.worksheet(sheet_name), parameters)
        return self._sheets[sheet_name]

    def pull_all_sheets(self):
        for sheet in self.workbook.worksheets():
            self._sheets[sheet.title] = GoogleSheet(sheet, self.parameters)

    def get_sheet(self, sheet_name: str) -> GoogleSheet:
        if sheet_name not in self._sheets:
            raise Exception
        return self._sheets[sheet_name]

    def get_all_sheets(self):
        return list(self._sheets.values())
