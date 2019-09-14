"""Manages file manipulation."""

import enum
import os
from typing import Optional, Text, Union


class OpenMode(enum.Enum):
  """Open modes for files."""
  READ_BINARY = 'rb'
  READ_TEXT = 'r'
  WRITE_BINARY = 'wb'
  WRITE_BINARY_FORCE = 'wb+'
  WRITE_TEXT = 'w'
  WRITE_TEXT_FORCE = 'w+'


class OpenModeLists(enum.Enum):
  """Groups open modes for files."""
  READ = [OpenMode.READ_BINARY, OpenMode.READ_TEXT]
  WRITE = [
      OpenMode.WRITE_BINARY, OpenMode.WRITE_BINARY_FORCE,
      OpenMode.WRITE_TEXT, OpenMode.WRITE_TEXT_FORCE,
  ]


def create_file(filename: Text, contents: Optional[Text] = None,
                force_dir_creation: bool = True):
  """Creates a new file.

  Args:
    filename: Name of the file to create.
    contents: Contents of the file to create.
    force_dir_creation: If True, forces the creation of the directories.
  """
  absolute_filename = _get_absolute_filename(filename)

  if force_dir_creation:
    _create_folders_for_file(absolute_filename)

  contents = contents or ''
  write_mode = (
      OpenMode.WRITE_BINARY_FORCE
      if isinstance(contents, bytes) else
      OpenMode.WRITE_TEXT_FORCE)

  return _write_file_contents(filename, contents, write_mode)


def _create_folders_for_file(filename):
  """Creates all folders in filename path.

  Args:
    filename: File name for which to create directories.
  """
  os.makedirs(os.path.dirname(filename), exist_ok=True)


def _get_absolute_filename(filename: Text) -> Text:
  """Gets the absolute filename of a given file.

  Args:
    filename: Name of the file for which to get full path name.

  Returns:
    Full path and filename of given filename.
  """
  current_file_path = os.path.dirname(__file__)
  return os.path.join(current_file_path, '..', filename)


def get_file_text_content(filename: Text) -> Text:
  """Gets file contents of a given file.

  Args:
    filename: File for which to get contents.

  Returns:
    Text content of the file.
  """
  return _get_file_contents(filename, OpenMode.READ_TEXT)


def get_file_binary_content(filename: Text) -> bytes:
  """Gets file binary contents of a given file.

  Args:
    filename: File for which to get bytes.

  Returns:
    Binary content of the file.
  """
  return _get_file_contents(filename, OpenMode.READ_BINARY)


def _get_file_contents(
        filename: Text, read_mode: OpenMode) -> Union[Text, bytes]:
  """Gets contents of file.

  Args:
    filename: File from which to get contents.
    read_mode: Mode in which to get contents.

  Raises:
    ValueError: Unknown read_mode.

  Returns:
    Contents of the file.
  """
  if read_mode not in OpenModeLists.READ.value:
    raise ValueError(f'Unknown read mode {read_mode}.')

  absolute_filename = _get_absolute_filename(filename)

  existing_file = open(absolute_filename, read_mode.value)
  file_contents = existing_file.read()

  return file_contents


def _write_file_contents(filename: Text, contents: Union[Text, bytes],
                         write_mode: OpenMode):
  """Writes contents to a filename.

  Args:
    filename: File to which to write contents.
    contents: Contents to write to file.
    write_mode: Mode in which to write data.

  Raises:
    ValueError: Unknown write_mode.

  Returns:
    File to which contents are written.
  """
  if write_mode not in OpenModeLists.WRITE.value:
    raise ValueError(f'Unknown write mode {write_mode}.')

  absolute_filename = _get_absolute_filename(filename)

  new_file = open(absolute_filename, write_mode.value)
  new_file.write(contents)
  new_file.close()

  return new_file
