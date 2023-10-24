from frictionless import Check, errors
from abc import ABC, abstractmethod


def build_check_error(custom_check_code: str, note: str):
    custom_note = f"{custom_check_code!r}: {note}"
    return errors.CheckError(note=custom_note)


def valued(val):
    return not (val is None)


class CustomCheckSingleColumn(Check, ABC):
    """Abstract class used for custom checks related to only one column"""

    def __init__(self, descriptor=None):
        super().__init__(descriptor)
        self.__column = self.get("column")

    def validate_start(self):
        if self.__column not in self.resource.schema.field_names:
            # The column is not found -> ignore custom check
            return []
        else:
            yield from self._validate_start()

    @abstractmethod
    def _validate_start(self):
        return []

    def validate_row(self, row):

        cell_value = row[self.get("column")]

        # Empty cell, don't check!
        if not cell_value:
            return []
        else:
            yield from self._validate_row(cell_value, row)

    @abstractmethod
    def _validate_row(self, cell_value, row):
        return []


class CustomCheckMultipleColumns(Check, ABC):
    """
    Abstract class used for custom checks related to many columns.

    'column', 'column2', 'columns', 'othercolumns' correspond to the parameters used in the custom checks.

    Some custom checks concern only two columns and use parameters 'column' and 'column2' ( that is the case for example
     for compare_columns_value custom check)
    Other ones concern many columns and could use parameters:
        - 'column' and 'columns' which represents a table with the name of the others columns
    relative to this custom check (for example sum_columns_value)
        - 'column' and 'othercolumns' which represents a table with the name of the others columns
    relative to this custom check (for example cohesive_columns_value)

    __skip_empty_cells should be set to True in most situations (then the treatment of missing values depends as
    usual on the value of the required schema instruction), except when the custom check specifically deals with
    checking missing values.

    """

    def __init__(self, descriptor=None):
        super().__init__(descriptor)
        self.__column = self.get("column")
        self.__column2 = self.get("column2")
        self.__columns = self.get("columns")
        self.__other_columns = self.get("othercolumns")
        self.__skip_empty_cells = True

    def get_all_columns(self):
        if not self.__column2 is None:
            return [self.__column] + [self.__column2]
        elif not self.__other_columns is None:
            return [self.__column] + self.__other_columns
        elif not self.__columns is None:
            return [self.__column] + self.__columns
        else:
            raise Exception("Param 'column2' or 'othercolumns' or 'columns' is not defined in the custom check used in "
                            "the validation schema")

    def validate_start(self):
        try:
            all_columns = self.get_all_columns()
        except Exception as e:
            custom_note = f"Custom check using multiple columns: {e}."
            yield errors.CheckError(note=custom_note)
        else:
            all_columns_are_not_found_in_field_names = True
            for col in all_columns:
                if col in self.resource.schema.field_names:
                    all_columns_are_not_found_in_field_names = False
                    break
            if all_columns_are_not_found_in_field_names:
                # All the columns relative to the custom check are not found -> ignore custom check
                return []
            else:
                yield from self._validate_start(all_columns)

    @abstractmethod
    def _validate_start(self, all_columns):
        return []

    def validate_row(self, row):
        cell_values = [row[col] for col in self.get_all_columns()]
        # Empty cell, don't check!
        if not all(valued(cell_value) for cell_value in cell_values):
            return []
        else:
            yield from self._validate_row(cell_values, row)

    @abstractmethod
    def _validate_row(self, cell_values, row):
        return []
