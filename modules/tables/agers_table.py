from typing import Any, List, Tuple
from database.tewdb import TEWDB
from utils.sk_logger import sk_log


class AgersTable:
    def __init__(self):
        try:
            self.tewdb = TEWDB()
        except Exception as e:
            sk_log.error(f"AgersTable __init__ error: {e}")
            raise e


class AgersFunctions:
    def __init__(self):
        try:
            self.tewdb = TEWDB()
        except Exception as e:
            sk_log.error(f"AgersFunctions __init__ error: {e}")
            raise e

        def __enter__(self) -> "AgersFunctions":
            """Context manager entry."""
            return self

        def __exit__(self, exc_type, exc_val, exc_tb) -> None:
            """Context manager exit."""
            if hasattr(self, "tewdb"):
                self.tewdb.close()
                sk_log.debug("AgersFunctions database connection closed")

    def fetch_all_agers_in_table(self) -> List[Tuple]:
        try:
            self.agers_table = self.tewdb.select("SELECT * FROM tblAger")
            return self.agers_table
        except Exception as e:
            sk_log.error(f"AgersFunctions fetch_all_agers_in_table error: {e}")
            raise e

    def fetch_ager_by_recordname(self, recordname: str) -> Tuple:
        try:
            self.agers_table = self.tewdb.select(
                "SELECT * FROM tblAger WHERE Recordname = ?", (recordname,)
            )
            return self.agers_table
        except Exception as e:
            sk_log.error(f"AgersFunctions fetch_ager_by_recordname error: {e}")
            raise e

    def fetch_ager_colvalue_by_colname(
        self, column_name: str
    ) -> List[Tuple[int, Any]]:
        try:
            self.agers_table = self.tewdb.select(
                f"SELECT uid, {column_name} FROM tblAger"
            )
            return self.agers_table
        except Exception as e:
            sk_log.error(
                "AgersFunctions fetch_ager_colvalue_by_colname error: {e}"
            )
            raise e

    def fetch_ager_recordname_list_by_worker_uid(
        self, worker_uid: int
    ) -> List[str]:
        try:
            self.agers_table = self.tewdb.select(
                "SELECT Recordname FROM tblAger WHERE Worker = ?", (worker_uid,)
            )
            return self.agers_table
        except Exception as e:
            sk_log.error(
                f"AgersFunctions fetch_ager_recordname_list_by_worker_uid error: {e}"
            )
            raise e

    def fetch_all_agers_specific_cols(self, columns: List[str]) -> List[Tuple]:
        try:
            self.agers_table = self.tewdb.select(
                f"SELECT {', '.join(columns)} FROM tblAger"
            )
            return self.agers_table
        except Exception as e:
            sk_log.error(
                f"AgersFunctions fetch_all_agers_specific_cols error: {e}"
            )
            raise e

    def fetch_ager_specific_cols(self, columns: List[str]) -> List[Tuple]:
        try:
            self.agers_table = self.tewdb.select(
                f"SELECT {', '.join(columns)} FROM tblAger"
            )
            return self.agers_table
        except Exception as e:
            sk_log.error(f"AgersFunctions fetch_ager_specific_cols error: {e}")
            raise e

    def fetch_ager_specific_cols_by_recordname(
        self, recordname: str, columns: List[str]
    ) -> List[Tuple]:
        try:
            cols = columns.copy()
            if "uid" not in cols:
                cols.insert(0, "uid")
            query = (
                f"SELECT {', '.join(cols)} FROM tblAger WHERE Recordname = ?"
            )
            sk_log.debug(
                f"Constructed query: {query} with params: [{recordname}]"
            )

            self.agers_table = self.tewdb.select(query, [recordname])
            return self.agers_table
        except Exception as e:
            sk_log.error(
                f"AgersFunctions fetch_ager_specific_cols_by_recordname error: {e}"
            )
            raise e

    def fetch_ager_uid_list_by_worker_uid(self, worker_uid: int) -> List[int]:
        try:
            self.agers_table = self.tewdb.select(
                "SELECT uid FROM tblAger WHERE Worker = ?", (worker_uid,)
            )
            return self.agers_table
        except Exception as e:
            sk_log.error(
                f"AgersFunctions fetch_ager_uid_list_by_worker_uid error: {e}"
            )
            raise e
