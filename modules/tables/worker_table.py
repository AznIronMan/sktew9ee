from typing import Any, List, Tuple
from database.tewdb import TEWDB
from utils.sk_logger import sk_log


class WorkerTable:
    def __init__(self) -> None:
        try:
            self.tewdb = TEWDB()
        except Exception as e:
            sk_log.error(f"WorkerTable __init__ error: {e}")
            raise e


class WorkerFunctions:
    def __init__(self) -> None:
        try:
            self.tewdb = TEWDB()
        except Exception as e:
            sk_log.error(f"WorkerFunctions __init__ error: {e}")
            raise e

    def __enter__(self) -> "WorkerFunctions":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        if hasattr(self, "tewdb"):
            self.tewdb.close()
            sk_log.debug("WorkerFunctions database connection closed")

    def fetch_all_workers_in_table(self) -> List[Tuple]:
        try:
            self.worker_table = self.tewdb.select("SELECT * FROM tblWorker")
            return self.worker_table
        except Exception as e:
            sk_log.error(
                f"WorkerFunctions fetch_all_workers_in_table error: {e}"
            )
            raise e

    def fetch_worker_by_uid(self, uid: int) -> Tuple:
        try:
            self.worker_table = self.tewdb.select(
                "SELECT * FROM tblWorker WHERE uid = ?", (uid,)
            )
            return self.worker_table
        except Exception as e:
            sk_log.error(f"WorkerFunctions fetch_worker_by_uid error: {e}")
            raise e

    def fetch_all_workers_specific_cols(
        self, columns: List[str]
    ) -> List[Tuple]:
        try:
            self.worker_table = self.tewdb.select(
                f"SELECT {', '.join(columns)} FROM tblWorker"
            )
            return self.worker_table
        except Exception as e:
            sk_log.error(
                f"WorkerFunctions fetch_all_workers_specific_cols error: {e}"
            )
            raise e

    def fetch_worker_specific_cols(
        self, uid: int, columns: List[str]
    ) -> List[Tuple]:
        try:
            cols = columns.copy()
            if "uid" not in cols:
                cols.insert(0, "uid")
            query = f"SELECT {', '.join(cols)} FROM tblWorker WHERE uid = ?"
            sk_log.debug(f"Constructed query: {query} with params: [{uid}]")

            self.worker_table = self.tewdb.select(query, [uid])
            return self.worker_table
        except Exception as e:
            sk_log.error(
                f"WorkerFunctions fetch_specific_columns_from_worker_table error: {e}"
            )
            raise e

    def fetch_worker_colvalue_by_colname(
        self, column_name: str
    ) -> List[Tuple[int, Any]]:
        try:
            self.worker_table = self.tewdb.select(
                f"SELECT uid, {column_name} FROM tblWorker"
            )
            return self.worker_table
        except Exception as e:
            sk_log.error(
                "WorkerFunctions fetch_all_workers_column_value_by_column_name "
                f"error: {e}"
            )
            raise e
