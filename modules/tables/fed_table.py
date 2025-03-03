from typing import Any, List, Tuple
from database.tewdb import TEWDB
from utils.sk_logger import sk_log


class FedTable:
    def __init__(self) -> None:
        try:
            self.tewdb = TEWDB()
        except Exception as e:
            sk_log.error(f"FedTable __init__ error: {e}")
            raise e


class FedFunctions:
    def __init__(self) -> None:
        try:
            self.tewdb = TEWDB()
        except Exception as e:
            sk_log.error(f"FedFunctions __init__ error: {e}")
            raise e

    def __enter__(self) -> "FedFunctions":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        if hasattr(self, "tewdb"):
            self.tewdb.close()
            sk_log.debug("FedFunctions database connection closed")

    def fetch_all_feds_in_table(self) -> List[Tuple]:
        try:
            self.fed_table = self.tewdb.select("SELECT * FROM tblFed")
            return self.fed_table
        except Exception as e:
            sk_log.error(f"FedFunctions fetch_all_feds_in_table error: {e}")
            raise e

    def fetch_fed_by_uid(self, uid: int) -> Tuple:
        try:
            self.fed_table = self.tewdb.select(
                "SELECT * FROM tblFed WHERE uid = ?", (uid,)
            )
            return self.fed_table
        except Exception as e:
            sk_log.error(f"FedFunctions fetch_fed_by_uid error: {e}")
            raise e

    def fetch_fedname_by_uid(self, uid: int) -> str:
        try:
            self.fed_table = self.tewdb.select(
                "SELECT Name FROM tblFed WHERE uid = ?", (uid,)
            )
            return self.fed_table[0][0]
        except Exception as e:
            sk_log.error(f"FedFunctions fetch_fedname_by_uid error: {e}")
            raise e

    def fetch_fedinitials_by_uid(self, uid: int) -> str:
        try:
            self.fed_table = self.tewdb.select(
                "SELECT Initials FROM tblFed WHERE uid = ?", (uid,)
            )
            return self.fed_table[0][0]
        except Exception as e:
            sk_log.error(f"FedFunctions fetch_fedinitials_by_uid error: {e}")
            raise e

    def fetch_all_feds_specific_cols(self, columns: List[str]) -> List[Tuple]:
        try:
            self.fed_table = self.tewdb.select(
                f"SELECT {', '.join(columns)} FROM tblFed"
            )
            return self.fed_table
        except Exception as e:
            sk_log.error(
                f"FedFunctions fetch_all_feds_specific_cols error: {e}"
            )
            raise e

    def fetch_fed_specific_cols(
        self, uid: int, columns: List[str]
    ) -> List[Tuple]:
        try:
            cols = columns.copy()
            if "uid" not in cols:
                cols.insert(0, "uid")
            query = f"SELECT {', '.join(cols)} FROM tblFed WHERE uid = ?"
            sk_log.debug(f"Constructed query: {query} with params: [{uid}]")

            self.fed_table = self.tewdb.select(query, [uid])
            return self.fed_table
        except Exception as e:
            sk_log.error(
                f"FedFunctions fetch_specific_columns_from_fed_table error: {e}"
            )
            raise e

    def fetch_fed_colvalue_by_colname(
        self, column_name: str
    ) -> List[Tuple[int, Any]]:
        try:
            self.fed_table = self.tewdb.select(
                f"SELECT uid, {column_name} FROM tblFed"
            )
            return self.fed_table
        except Exception as e:
            sk_log.error(
                "FedFunctions fetch_all_feds_column_value_by_column_name "
                f"error: {e}"
            )
            raise e
