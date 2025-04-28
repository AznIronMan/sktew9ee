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
            # Validate column names for security
            valid_columns = [
                "UID",
                "FedUID",
                "WorkerUID",
                "Name",
                "Picture",
                "Nickname",
                "Shortname",
            ]

            # Filter and ensure only valid columns are used
            validated_columns = [col for col in columns if col in valid_columns]

            if not validated_columns:
                raise ValueError("No valid columns provided for the query")

            # Approach 1: Try using direct column names (original approach)
            try:
                column_str = ", ".join(validated_columns)
                query = f"SELECT {column_str} FROM tblContract"
                sk_log.debug(f"Selecting columns (approach 1): {column_str}")
                self.contract_table = self.tewdb.select(query)
                return self.contract_table
            except Exception as e1:
                # If the direct approach fails, try approach 2 with qualified column names
                err_msg = f"Direct query failed, trying approach 2: {e1}"
                sk_log.warning(err_msg)

                try:
                    # Approach 2: Use qualified column names with square brackets
                    cols_with_brackets = [
                        f"[{col}]" for col in validated_columns
                    ]
                    column_str = ", ".join(cols_with_brackets)
                    query = f"SELECT {column_str} FROM tblContract"
                    sk_log.debug(
                        f"Selecting columns (approach 2): {column_str}"
                    )
                    self.contract_table = self.tewdb.select(query)
                    return self.contract_table
                except Exception as e2:
                    # If approach 2 fails, try the fallback approach
                    err_msg = (
                        f"Qualified column names failed, trying fallback: {e2}"
                    )
                    sk_log.warning(err_msg)

                    # Approach 3: Fallback to SELECT * with filtering
                    try:
                        # Use a simple query
                        query = "SELECT * FROM tblContract"
                        debug_msg = (
                            "Selecting all columns and filtering (approach 3)"
                        )
                        sk_log.debug(debug_msg)
                        results = self.tewdb.select(query)

                        # Filter results to include only requested columns
                        filtered_results = []
                        for row in results:
                            filtered_row = {
                                col: row[col]
                                for col in validated_columns
                                if col in row
                            }
                            filtered_results.append(filtered_row)

                        return filtered_results
                    except Exception as e3:
                        sk_log.error(f"All approaches failed: {e3}")
                        raise e3
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
