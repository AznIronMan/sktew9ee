from typing import Any, List, Tuple
from database.tewdb import TEWDB
from utils.sk_logger import sk_log


class ContractTable:
    def __init__(self) -> None:
        try:
            self.tewdb = TEWDB()
        except Exception as e:
            sk_log.error(f"ContractTable __init__ error: {e}")
            raise e


class ContractFunctions:
    def __init__(self) -> None:
        try:
            self.tewdb = TEWDB()
        except Exception as e:
            sk_log.error(f"ContractFunctions __init__ error: {e}")
            raise e

    def __enter__(self) -> "ContractFunctions":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        if hasattr(self, "tewdb"):
            self.tewdb.close()
            sk_log.debug("ContractFunctions database connection closed")

    def fetch_all_contracts_in_table(self) -> List[Tuple]:
        try:
            self.contract_table = self.tewdb.select("SELECT * FROM tblContract")
            return self.contract_table
        except Exception as e:
            sk_log.error(
                f"ContractFunctions fetch_all_contracts_in_table error: {e}"
            )
            raise e

    def fetch_contract_by_uid(self, uid: int) -> Tuple:
        try:
            self.contract_table = self.tewdb.select(
                "SELECT * FROM tblContract WHERE uid = ?", (uid,)
            )
            return self.contract_table
        except Exception as e:
            sk_log.error(f"ContractFunctions fetch_contract_by_uid error: {e}")
            raise e

    def fetch_all_contracts_specific_cols(
        self, columns: List[str]
    ) -> List[Tuple]:
        try:
            self.contract_table = self.tewdb.select(
                f"SELECT {', '.join(columns)} FROM tblContract"
            )
            return self.contract_table
        except Exception as e:
            sk_log.error(
                f"ContractFunctions fetch_all_contracts_specific_cols error: {e}"
            )
            raise e

    def fetch_contract_specific_cols(
        self, uid: int, columns: List[str]
    ) -> List[Tuple]:
        try:
            cols = columns.copy()
            if "uid" not in cols:
                cols.insert(0, "uid")
            query = f"SELECT {', '.join(cols)} FROM tblContract WHERE uid = ?"
            sk_log.debug(f"Constructed query: {query} with params: [{uid}]")

            self.contract_table = self.tewdb.select(query, [uid])
            return self.contract_table
        except Exception as e:
            sk_log.error(
                "ContractFunctions fetch_specific_columns_from_contract_table "
                f"error: {e}"
            )
            raise e

    def fetch_contract_colvalue_by_colname(
        self, column_name: str
    ) -> List[Tuple[int, Any]]:
        try:
            self.contract_table = self.tewdb.select(
                f"SELECT uid, {column_name} FROM tblContract"
            )
            return self.contract_table
        except Exception as e:
            sk_log.error(
                "ContractFunctions fetch_all_contracts_column_value_by_column_name "
                f"error: {e}"
            )
            raise e

    def fetch_all_contract_uids_by_worker_uid(
        self, worker_uid: int
    ) -> List[int]:
        try:
            self.contract_table = self.tewdb.select(
                "SELECT uid FROM tblContract WHERE WorkerUID = ?", (worker_uid,)
            )
            return [row[0] for row in self.contract_table]
        except Exception as e:
            sk_log.error(
                f"ContractFunctions fetch_all_contract_uids_by_worker_uid error: {e}"
            )
            raise e

    def fetch_all_contract_fedids_by_worker_uid(
        self, worker_uid: int
    ) -> List[int]:
        try:
            self.contract_table = self.tewdb.select(
                "SELECT FedUID FROM tblContract WHERE WorkerUID = ?",
                (worker_uid,),
            )
            return [row[0] for row in self.contract_table]
        except Exception as e:
            sk_log.error(
                f"ContractFunctions fetch_all_contract_fedids_by_worker_uid error: {e}"
            )
            raise e

    def fetch_all_worker_uids_by_fed_uid(self, fed_uid: int) -> List[int]:
        try:
            self.contract_table = self.tewdb.select(
                "SELECT WorkerUID FROM tblContract WHERE FedUID = ?", (fed_uid,)
            )
            return [row[0] for row in self.contract_table]
        except Exception as e:
            sk_log.error(
                f"ContractFunctions fetch_all_worker_uids_by_fed_uid error: {e}"
            )
            raise e
