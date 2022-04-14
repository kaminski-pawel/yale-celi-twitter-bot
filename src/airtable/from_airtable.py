import json
import re
import typing as t
import unicodedata


def slugify(value: str) -> str:
    """
    Converts to lowercase ascii, removes non-alphanumerics characters
    and converts spaces to hyphens. Also strips leading and
    trailing whitespaces.
    """
    value = unicodedata.normalize('NFKD', value).encode(
        'ascii', 'ignore').decode('ascii')
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    return re.sub('[-\s]+', '-', value)


def join_on_key(
    l1: t.List[t.Dict[str, t.Any]],
    l2: t.List[t.Dict[str, t.Any]],
    join_on: str,
) -> t.List[t.Dict[str, t.Any]]:
    """
    Create one big dictionary where the `join_on` value serves as a dict key,
    merging values of two lists of dictionaries, `l1` and `l2`. 
    Return as a list of merged dictionaries.
    """
    d1 = {d[join_on]: d for d in l1}
    return [dict(d, **d1.get(d[join_on], {})) for d in l2]


class AirtableTransformer:
    """
    Transforms table data from airtable data saved in `self.input_json`.

    To populate such .json file:
        1. Open Developer Console (if using Google Chrome) in the "Network" tab
        2. Find readSharedViewData response
        3. In "Preview" tab copy value of the data variable
        4. Save the copied value to .json file
    """

    def __init__(self):
        self.prefix = 'e_'  # 'e' as in 'extended'
        self.input_json = None
        self.use_created_time = False

    def get_table(self):
        self._set_initial_table_data()
        self._set_columns_mapping()
        self._set_choices_mapping()
        return self._update_table_data_with_slugs(self._get_table_data())

    def _set_initial_table_data(self) -> None:
        with open(self.input_json, encoding='utf-8') as f:
            self.data = json.load(f)

    def _set_columns_mapping(self) -> t.Dict[str, str]:
        """
        Returns a mapping of Airtable internal field id to human readable field names
        """
        if self.use_created_time:
            self._columns = {item['id']: item['name'] for item in [
                *self.data['table']['columns'],
                {'id': 'createdTime', 'name': 'Created time'}]}
        else:
            self._columns = {item['id']: item['name']
                             for item in self.data['table']['columns']}

    def _set_choices_mapping(self) -> t.Dict[str, str]:
        """
        Returns a mapping of Airtable internal id to human readable choice' names
        """
        self._choices = {}
        for item in self.data['table']['columns']:
            if item['typeOptions'] and 'choices' in item['typeOptions']:
                for choice_name, choice_vals in item['typeOptions']['choices'].items():
                    self._choices[choice_name] = choice_vals['name']
        return self._choices

    def _get_table_data(self) -> t.List[t.Dict[str, str]]:
        """
        Extracts table data into list of human readable dicts
        """
        if self.use_created_time:
            self._add_created_time()
        return [{self._prepare_header(header): self._prepare_cell(cell)
                 for header, cell in row['cellValuesByColumnId'].items()}
                for row in self.data['table']['rows'] if row.get('cellValuesByColumnId', {})]

    def _add_created_time(self):
        for row in self.data['table']['rows']:
            if row.get('cellValuesByColumnId', {}):
                row['cellValuesByColumnId']['createdTime'] = row['createdTime']

    def _prepare_header(self, header: str) -> str:
        """Transforms 'Market Cap' to 'e_market_cap' str (except 'slug' field)"""
        _header = self._columns[header].lower().strip()
        if _header == 'slug':
            return _header
        return self.prefix + _header.replace(' ', '_')

    def _prepare_cell(self, cell: str) -> str:
        """
        Transforms value of a single cell to human readable flat format
        """
        if type(cell) == str and ' ' not in cell and cell.startswith('sel'):
            return self._choices[cell]
        if type(cell) == list and 'url' in cell[0]:
            return cell[0]['url']
        return cell

    def _update_table_data_with_slugs(self,
                                      table_data: t.List[t.Dict[str, str]],
                                      ) -> t.List[t.Dict[str, str]]:
        """
        Iterates over list of dicts and adds a slug to each object
        """
        return [{**item, 'slug': slugify(item[self.prefix + 'name'])} for item in table_data]
