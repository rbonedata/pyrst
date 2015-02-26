# coding=utf-8

import pandas as pd
import logging
module_logger = logging.getLogger("pyrst.client")
module_logger.setLevel(logging.DEBUG)

class Handler(object):
    """
    Abstract class that represents Handler objects.

    In Pyrst, a Handler object receives the raw query result and converts it
    into a specified format, such as a pandas DataFrame or a D3 compatible
    JSON file.

    A Handler needs to have a process() function that takes the query_output
    as its argument. The return of that function is going to be the output of
    the Handler.
    """

    def __repr__(self):
        return "Pyrst output handler"

    def process(self,
                query_output):
        """
        Default query output processor, returns the query output in its raw
        form.

        :param query_output: raw query output
        :return: raw query output instance
        :rtype: str
        """
        return query_output


class DfHandler(Handler):
    """
    Handler that returns a `pandas` `DataFrame`.
    """
    def __init__(self):
        self.logger = logging.getLogger("pyrst.client")
        self.logger.info("Setting up handler...")

    def process(self,
                query_output):
        """
        Query output processor that returns a `pandas` `DataFrame` object.

        :param query_output: raw query output
        :return: `pandas` `DataFrame` object representing the result
        :rtype: DataFrame
        """
        self.logger.debug("Processing query output...")

        _series = []
        for each in query_output.rows:
            _series.append(each[0])

        _df = pd.DataFrame(_series)

        _df.columns = query_output.colnames
        self.logger.debug("Processing columns: %s" % _df.columns)
        return _df


class JsonHandler(Handler):
    """
    Handler that returns a JSON file, ready to be ingested by D3.

    Currently, this is implemented 'lazily', i.e. the DfHandler is invoked,
    and the output is then exported into JSON using pandas's JSON export
    function. Eventually, we will aim to create a thoroughbred JSON export
    function.
    """

    def __init__(self,
                 orient="records",
                 date_format="iso"):
        """
        Creates a JSON handler. Accepts an encoding orientation and a datetime
        format setting.

        Possible encoding formats are the same as for the `pandas` `DataFrame`
        `to_csv` method:
        - split: one dict per record with columns and data as separate fields
        - records (default): one array per record, with columns as separate
        dicts
        - index: one dict per record, assigning a dict of column-value pairs
        to the index
        - columns: one dict per column, assigning a dict of index-value pairs
        to the column name
        - values: just the values array

        Possible datetime formats are:
        - iso (default): ISO8601 date format
        - epoch: UNIX epoch milliseconds format

        :param orient: encoding orientation
        :param date_format: datetime format
        """
        self.orient = orient
        self.date_format = date_format
        self.logger = logging.getLogger("pyrst.client")
        self.logger.info("Setting up JSON handler...")
        self.logger.info("JSON Handler options: %s date format, %s orientation" % (self.date_format, self.orient))

    def process(self,
                query_output):
        """
        Query output processor that returns a JSON string representation.

        :param query_output: raw query output
        :return: the representation of the query results as a JSON string
        :rtype: str
        """

        self.logger.debug("Processing to DataFrame.")
        _df = DfHandler().process(query_output=query_output)
        self.logger.debug("Processing to DataFrame complete.")

        self.logger.debug("Exporting to JSON.")

        return _df.to_json(orient=self.orient,
                           date_format=self.date_format)


class CsvHandler(Handler):
    """
    Handler that returns a CSV file, ready to be ingested by Excel etc..

    Currently, this is implemented 'lazily', i.e. the DfHandler is invoked,
    and the output is then exported into JSON using pandas's CSV export
    function. Eventually, we will aim to create a thoroughbred CSV export
    function.
    """

    def __init__(self,
                 sep=',',
                 encoding="utf-8",
                 index=False):
        """
        Creates a CSV handler.

        :param sep: separator
        :type sep: str
        :param encoding: encoding (utf-8 or ascii)
        :type encoding: str
        :param index: whether to include index column in output (default:
        False)
        :type index: bool
        """
        self.sep = sep
        self.encoding = encoding
        self.index = index
        self.logger = logging.getLogger("pyrst.client")
        self.logger.info("Setting up CSV handler...")
        self.logger.info("CSV Handler options: separated by %s, encoding: %s" % (self.sep, self.encoding))


    def process(self,
                query_output):
        """
        Query output processor that returns a CSV as string representation.

        :param query_output: raw query output
        :return: representation of the result as a CSV string
        :rtype: str
        """

        self.logger.debug("Processing to DataFrame.")
        _df = DfHandler().process(query_output=query_output)
        self.logger.debug("Processing to DataFrame complete.")

        self.logger.debug("Exporting to CSV.")
        return _df.to_csv(sep=self.sep,
                          encoding=self.encoding,
                          index=self.index)