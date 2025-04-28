import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union
from fnmatch import fnmatch

from utils.sk_logger import sk_log


class Filer:
    def __init__(self) -> None:
        try:
            self.current_working_directory: Path = Path.cwd()
        except Exception as e:
            sk_log.error(f"Filer __init__ error: {e}")
            raise e

    def __enter__(self) -> "Filer":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        pass

    def fetch_files_from_directory(
        self,
        folder_path: Union[str, Path],
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        include_extensions: Optional[List[str]] = None,
        exclude_extensions: Optional[List[str]] = None,
        recursive: bool = False,
    ) -> List[Path]:
        sk_log.debug(
            f"Filer fetch_files_from_directory folder_path: {folder_path}, "
            f"include_patterns: {include_patterns}, exclude_patterns: "
            f"{exclude_patterns}, include_extensions: {include_extensions}, "
            f"exclude_extensions: {exclude_extensions}, recursive: {recursive}"
        )
        try:
            folder = Path(folder_path)
            if not folder.exists():
                raise FileNotFoundError(f"Directory {folder} does not exist")

            if recursive:
                files = [f for f in folder.rglob("*") if f.is_file()]
            else:
                files = [f for f in folder.iterdir() if f.is_file()]

            if include_patterns:
                files = [
                    f
                    for f in files
                    if any(
                        fnmatch(f.name.lower(), pattern.lower())
                        for pattern in include_patterns
                    )
                ]
            if exclude_patterns:
                exclude_patterns = [p.lower() for p in exclude_patterns]
                files = [
                    f
                    for f in files
                    if not any(p in f.name.lower() for p in exclude_patterns)
                ]
            if include_extensions:
                include_extensions = [ext.lower() for ext in include_extensions]
                files = [
                    f
                    for f in files
                    if f.suffix.lower()[1:] in include_extensions
                ]
            if exclude_extensions:
                exclude_extensions = [ext.lower() for ext in exclude_extensions]
                files = [
                    f
                    for f in files
                    if f.suffix.lower()[1:] not in exclude_extensions
                ]
            sk_log.debug(f"Filer fetch_files_from_directory result: {files}")
            return files
        except Exception as e:
            sk_log.error(f"Filer fetch_files_from_directory error: {e}")
            raise e

    def get_file_metadata(self, file_path: Union[str, Path]) -> Dict:
        try:
            sk_log.debug(f"Filer get_file_metadata file_path: {file_path}")
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"File {path} does not exist")

            stats = path.stat()
            sk_log.debug(f"Filer get_file_metadata result: {stats}")
            return {
                "size": stats.st_size,
                "created": datetime.fromtimestamp(stats.st_ctime),
                "modified": datetime.fromtimestamp(stats.st_mtime),
                "accessed": datetime.fromtimestamp(stats.st_atime),
                "extension": path.suffix,
                "name": path.name,
                "is_hidden": path.name.startswith("."),
            }
        except Exception as e:
            sk_log.error(f"Filer get_file_metadata error: {e}")
            raise e

    def safe_copy(
        self,
        source: Union[str, Path],
        destination: Union[str, Path],
        overwrite: bool = False,
    ) -> Path:
        try:
            sk_log.debug(
                f"Filer safe_copy source: {source}, destination: {destination},"
                f" overwrite: {overwrite}"
            )
            src_path = Path(source)
            dst_path = Path(destination)
            if not src_path.exists():
                raise FileNotFoundError(
                    f"Source file {src_path} does not exist"
                )
            if dst_path.exists() and not overwrite:
                raise FileExistsError(
                    f"Destination file {dst_path} already exists"
                )
            sk_log.debug(
                f"Filer safe_copy result: {Path(shutil.copy2(src_path, dst_path))}"
            )
            return Path(shutil.copy2(src_path, dst_path))
        except Exception as e:
            sk_log.error(f"Filer safe_copy error: {e}")
            raise e

    def safe_move(
        self,
        source: Union[str, Path],
        destination: Union[str, Path],
        overwrite: bool = False,
    ) -> Path:
        try:
            src_path = Path(source)
            dst_path = Path(destination)
            if not src_path.exists():
                raise FileNotFoundError(
                    f"Source file {src_path} does not exist"
                )
            if dst_path.exists() and not overwrite:
                raise FileExistsError(
                    f"Destination file {dst_path} already exists"
                )
            return Path(shutil.move(src_path, dst_path))
        except Exception as e:
            sk_log.error(f"Filer safe_move error: {e}")
            raise e

    def safe_delete(self, file_path: Union[str, Path]) -> None:
        sk_log.debug(f"Filer safe_delete file_path: {file_path}")
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"File {path} does not exist")
            sk_log.debug(f"Filer safe_delete file_path: {file_path}")
            path.unlink()
        except Exception as e:
            sk_log.error(f"Filer safe_delete error: {e}")
            raise e

    def ensure_directory(self, directory_path: Union[str, Path]) -> Path:
        sk_log.debug(f"Filer ensure_directory directory_path: {directory_path}")
        try:
            path = Path(directory_path)
            path.mkdir(parents=True, exist_ok=True)
            sk_log.debug(f"Filer ensure_directory result: {path}")
            return path
        except Exception as e:
            sk_log.error(f"Filer ensure_directory error: {e}")
            raise e

    def filepath_formatter(
        self, filepath: Union[str, Path], extension: Optional[str] = None
    ) -> str:
        """Format the filepath to include an extension if it is not already included.

        Args:
            filepath (Union[str, Path]): The filepath to format.
            extension (Optional[str], optional): The extension to include if
            it is not already included. Defaults to None.

        Raises:
            Exception: If there is an error formatting the filepath.

        Returns:
            str: The formatted filepath.
        """
        try:
            path_obj = Path(filepath) if isinstance(filepath, str) else filepath
            if not extension:
                return str(filepath)
            if (
                path_obj.suffix.lower() == f".{extension.lower()}"
                or path_obj.suffix.lower() == extension.lower()
            ):
                return str(filepath)
            else:
                return f"{filepath}.{extension}"
        except Exception as e:
            sk_log.error(f"Filer filepath_formatter error: {e}")
            raise e

    def filename_formatter(
        self, filename: Union[str, Path], extension: Optional[str] = None
    ) -> str:
        """Format the filename to include an extension if it is not already included.

        Args:
            filename (Union[str, Path]): The filename to format.
            extension (Optional[str], optional): The extension to include if
            it is not already included. Defaults to None.

        Raises:
            Exception: If there is an error formatting the filename.

        Returns:
            str: The formatted filename.
        """
        try:
            path_obj = Path(filename)
            stripped_filename = path_obj.name
            if not extension:
                return stripped_filename
            if (
                path_obj.suffix.lower() == f".{extension.lower()}"
                or path_obj.suffix.lower() == extension.lower()
            ):
                return stripped_filename
            else:
                return f"{stripped_filename}.{extension}"
        except Exception as e:
            sk_log.error(f"Filer filename_formatter error: {e}")
            raise e

    def extract_extension(self, filename: Union[str, Path]) -> Optional[str]:
        """Extract the extension from the filename.

        Args:
            filename (Union[str, Path]): The filename to extract the extension from.

        Returns:
            Optional[str]: The extension from the filename or None if there is an error.
        """
        try:
            extracted_extension = Path(filename).suffix
            return extracted_extension if extracted_extension else None
        except Exception as e:
            sk_log.error(f"Filer extract_extension error: {e}")
            raise e

    def get_filesize_from_filename(
        self, filename: Union[str, Path], unit: str = "KB"
    ) -> Optional[int]:
        try:
            filesize = Path(filename).stat().st_size
            final_filesize = filesize
            if unit == "KB":
                final_filesize = filesize / 1024
            elif unit == "MB":
                final_filesize = filesize / 1024 / 1024
            elif unit == "RAW":
                final_filesize = filesize
            else:
                raise ValueError(f"Invalid unit: {unit}")
            if unit == "RAW":
                return f"{final_filesize} Bytes"
            else:
                return f"{final_filesize} {unit.upper()}"

        except Exception as e:
            sk_log.error(f"Filer get_filesize_from_filename error: {e}")
            raise e
