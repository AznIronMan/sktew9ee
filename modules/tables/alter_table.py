from typing import Any, List, Tuple
from database.tewdb import TEWDB
from utils.sk_logger import sk_log


class AlterTable:
    def __init__(self) -> None:
        try:
            self.tewdb = TEWDB()
        except Exception as e:
            sk_log.error(f"AlterTable __init__ error: {e}")
            raise e


class AlterFunctions:
    def __init__(self) -> None:
        try:
            self.tewdb = TEWDB()
        except Exception as e:
            sk_log.error(f"AlterFunctions __init__ error: {e}")
            raise e

    def __enter__(self) -> "AlterFunctions":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        if hasattr(self, "tewdb"):
            self.tewdb.close()
            sk_log.debug("AlterFunctions database connection closed")

    def fetch_all_alters_in_table(self) -> List[Tuple]:
        try:
            self.alter_table = self.tewdb.select("SELECT * FROM tblAlternate")
            return self.alter_table
        except Exception as e:
            sk_log.error(f"AlterFunctions fetch_all_alters_in_table error: {e}")
            raise e

    def fetch_alter_by_recordname(self, recordname: str) -> Tuple:
        try:
            self.alter_table = self.tewdb.select(
                "SELECT * FROM tblAlternate WHERE Recordname = ?", (recordname,)
            )
            return self.alter_table
        except Exception as e:
            sk_log.error(f"AlterFunctions fetch_alter_by_recordname error: {e}")
            raise e

    def fetch_alter_colvalue_by_colname(
        self, column_name: str
    ) -> List[Tuple[int, Any]]:
        try:
            self.alter_table = self.tewdb.select(
                f"SELECT uid, {column_name} FROM tblAlternate"
            )
            return self.alter_table
        except Exception as e:
            sk_log.error(
                "AlterFunctions fetch_all_alters_column_value_by_column_name "
                f"error: {e}"
            )
            raise e

    def fetch_alter_recordname_list_by_worker_uid(
        self, worker_uid: int
    ) -> List[str]:
        try:
            self.alter_table = self.tewdb.select(
                "SELECT Recordname FROM tblAlternate WHERE WorkerUID = ?",
                (worker_uid,),
            )
            return self.alter_table
        except Exception as e:
            sk_log.error(
                f"AlterFunctions fetch_alter_recordname_list_by_worker_uid error: {e}"
            )
            raise e

    def fetch_all_alters_specific_cols(self, columns: List[str]) -> List[Tuple]:
        try:
            self.alter_table = self.tewdb.select(
                f"SELECT {', '.join(columns)} FROM tblAlternate"
            )
            return self.alter_table
        except Exception as e:
            sk_log.error(
                f"AlterFunctions fetch_all_alters_specific_cols error: {e}"
            )
            raise e

    def fetch_alter_specific_cols(self, columns: List[str]) -> List[Tuple]:
        try:
            self.alter_table = self.tewdb.select(
                f"SELECT {', '.join(columns)} FROM tblAlternate"
            )
            return self.alter_table
        except Exception as e:
            sk_log.error(f"AlterFunctions fetch_alter_specific_cols error: {e}")
            raise e

    def fetch_alter_specific_cols_by_recordname(
        self, recordname: str, columns: List[str]
    ) -> List[Tuple]:
        try:
            cols = columns.copy()
            if "uid" not in cols:
                cols.insert(0, "uid")
            query = f"SELECT {', '.join(cols)} FROM tblAlternate WHERE Recordname = ?"
            sk_log.debug(
                f"Constructed query: {query} with params: [{recordname}]"
            )

            self.alter_table = self.tewdb.select(query, [recordname])
            return self.alter_table
        except Exception as e:
            sk_log.error(
                f"AlterFunctions fetch_specific_columns_from_alter_table error: {e}"
            )
            raise e

    def fetch_alter_uid_list_by_worker_uid(self, worker_uid: int) -> List[int]:
        try:
            self.alter_table = self.tewdb.select(
                "SELECT uid FROM tblAlternate WHERE WorkerUID = ?",
                (worker_uid,),
            )
            return self.alter_table
        except Exception as e:
            sk_log.error(
                f"AlterFunctions fetch_alter_uid_list_by_worker_uid error: {e}"
            )
            raise e
