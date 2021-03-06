# coding: utf-8
#
# Copyright 2020 The Oppia Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Lint checks for Python files."""

from __future__ import absolute_import  # pylint: disable=import-only-modules
from __future__ import unicode_literals  # pylint: disable=import-only-modules

import os
import re
import sys
import time

import python_utils

from . import linter_utils
from .. import common

_PATHS_TO_INSERT = [
    common.PYLINT_PATH,
    common.PYCODESTYLE_PATH,
    common.PYLINT_QUOTES_PATH
]
for path in _PATHS_TO_INSERT:
    sys.path.insert(1, path)

# pylint: disable=wrong-import-order
# pylint: disable=wrong-import-position
from pylint import lint  # isort:skip
import isort  # isort:skip
import pycodestyle # isort:skip
# pylint: enable=wrong-import-order
# pylint: enable=wrong-import-position

_MESSAGE_TYPE_SUCCESS = 'SUCCESS'
_MESSAGE_TYPE_FAILED = 'FAILED'


class PythonLintChecksManager(python_utils.OBJECT):
    """Manages all the Python linting functions.

    Attributes:
        files_to_lint: list(str). A list of filepaths to lint.
        verbose_mode_enabled: bool. True if verbose mode is enabled.
    """
    def __init__(
            self, files_to_lint, verbose_mode_enabled):
        """Constructs a PythonLintChecksManager object.

        Args:
            files_to_lint: list(str). A list of filepaths to lint.
            verbose_mode_enabled: bool. True if mode is enabled.
        """
        self.files_to_lint = files_to_lint
        self.verbose_mode_enabled = verbose_mode_enabled

    @property
    def py_filepaths(self):
        """Return all Python file paths."""
        return self.files_to_lint

    @property
    def all_filepaths(self):
        """Return all filepaths."""
        return self.py_filepaths

    def _check_import_order(self):
        """This function is used to check that each file
        has imports placed in alphabetical order.
        """
        if self.verbose_mode_enabled:
            python_utils.PRINT('Starting import-order checks')
            python_utils.PRINT('----------------------------------------')
        summary_messages = []
        files_to_check = self.py_filepaths
        failed = False
        stdout = sys.stdout
        with linter_utils.redirect_stdout(stdout):
            for filepath in files_to_check:
                # This line prints the error message along with file path
                # and returns True if it finds an error else returns False
                # If check is set to True, isort simply checks the file and
                # if check is set to False, it autocorrects import-order errors.
                if (isort.SortImports(
                        filepath, check=True, show_diff=(
                            True)).incorrectly_sorted):
                    failed = True
                    python_utils.PRINT('')

            python_utils.PRINT('')
            if failed:
                summary_message = (
                    '%s   Import order checks failed, file imports should be '
                    'alphabetized, see affect files above.' % (
                        _MESSAGE_TYPE_FAILED))
                python_utils.PRINT(summary_message)
                summary_messages.append(summary_message)
            else:
                summary_message = (
                    '%s   Import order checks passed' % _MESSAGE_TYPE_SUCCESS)
                python_utils.PRINT(summary_message)
                summary_messages.append(summary_message)
        return summary_messages

    def perform_all_lint_checks(self):
        """Perform all the lint checks and returns the messages returned by all
        the checks.

        Returns:
            all_messages: str. All the messages returned by the lint checks.
        """

        if not self.all_filepaths:
            python_utils.PRINT('')
            python_utils.PRINT('There are no Python files to lint.')
            return []

        return self._check_import_order()


class ThirdPartyPythonLintChecksManager(python_utils.OBJECT):
    """Manages all the third party Python linting functions.

    Attributes:
        files_to_lint: list(str). A list of filepaths to lint.
        verbose_mode_enabled: bool. True if verbose mode is enabled.
    """
    def __init__(
            self, files_to_lint, verbose_mode_enabled):
        """Constructs a ThirdPartyPythonLintChecksManager object.

        Args:
            files_to_lint: list(str). A list of filepaths to lint.
            verbose_mode_enabled: bool. True if verbose mode is enabled.
        """
        self.files_to_lint = files_to_lint
        self.verbose_mode_enabled = verbose_mode_enabled

    @property
    def all_filepaths(self):
        """Return all filepaths."""
        return self.files_to_lint

    def _lint_py_files(self, config_pylint, config_pycodestyle):
        """Prints a list of lint errors in the given list of Python files.

        Args:
            config_pylint: str. Path to the .pylintrc file.
            config_pycodestyle: str. Path to the tox.ini file.

        Return:
            summary_messages: list(str). Summary messages of lint check.
        """
        files_to_lint = self.all_filepaths
        start_time = time.time()
        are_there_errors = False
        summary_messages = []

        num_py_files = len(files_to_lint)

        python_utils.PRINT('Linting %s Python files' % num_py_files)

        _batch_size = 50
        current_batch_start_index = 0
        stdout = python_utils.string_io()

        while current_batch_start_index < len(files_to_lint):
            # Note that this index is an exclusive upper bound -- i.e.,
            # the current batch of files ranges from 'start_index' to
            # 'end_index - 1'.
            current_batch_end_index = min(
                current_batch_start_index + _batch_size, len(files_to_lint))
            current_files_to_lint = files_to_lint[
                current_batch_start_index: current_batch_end_index]
            if self.verbose_mode_enabled:
                python_utils.PRINT('Linting Python files %s to %s...' % (
                    current_batch_start_index + 1, current_batch_end_index))

            with linter_utils.redirect_stdout(stdout):
                # This line invokes Pylint and prints its output
                # to the target stdout.
                pylinter = lint.Run(
                    current_files_to_lint + [config_pylint],
                    exit=False).linter
                # These lines invoke Pycodestyle and print its output
                # to the target stdout.
                style_guide = pycodestyle.StyleGuide(
                    config_file=config_pycodestyle)
                pycodestyle_report = style_guide.check_files(
                    paths=current_files_to_lint)

            if pylinter.msg_status != 0 or pycodestyle_report.get_count() != 0:
                summary_message = stdout.getvalue()
                python_utils.PRINT(summary_message)
                summary_messages.append(summary_message)
                are_there_errors = True

            current_batch_start_index = current_batch_end_index

        if are_there_errors:
            summary_message = ('%s    Python linting failed' % (
                _MESSAGE_TYPE_FAILED))
        else:
            summary_message = ('%s   %s Python files linted (%.1f secs)' % (
                _MESSAGE_TYPE_SUCCESS, num_py_files, time.time() - start_time))

        python_utils.PRINT(summary_message)
        summary_messages.append(summary_message)

        python_utils.PRINT('Python linting finished.')
        return summary_messages

    def _lint_py_files_for_python3_compatibility(self):
        """Prints a list of Python 3 compatibility errors in the given list of
        Python files.

        Returns:
            summary_messages: list(str). Summary of lint check.
        """
        files_to_lint = self.all_filepaths
        start_time = time.time()
        any_errors = False
        stdout = python_utils.string_io()
        summary_messages = []

        files_to_lint_for_python3_compatibility = [
            file_name for file_name in files_to_lint if not re.match(
                r'^.*python_utils.*\.py$', file_name)]
        num_py_files = len(files_to_lint_for_python3_compatibility)
        if not files_to_lint_for_python3_compatibility:
            python_utils.PRINT('')
            python_utils.PRINT(
                'There are no Python files to lint for Python 3 compatibility.')
            return []

        python_utils.PRINT(
            'Linting %s Python files for Python 3 compatibility.' % (
                num_py_files))

        _batch_size = 50
        current_batch_start_index = 0

        while current_batch_start_index < len(
                files_to_lint_for_python3_compatibility):
            # Note that this index is an exclusive upper bound -- i.e.,
            # the current batch of files ranges from 'start_index' to
            # 'end_index - 1'.
            current_batch_end_index = min(
                current_batch_start_index + _batch_size, len(
                    files_to_lint_for_python3_compatibility))
            current_files_to_lint = files_to_lint_for_python3_compatibility[
                current_batch_start_index: current_batch_end_index]
            if self.verbose_mode_enabled:
                python_utils.PRINT(
                    'Linting Python files for Python 3 compatibility %s to %s..'
                    % (current_batch_start_index + 1, current_batch_end_index))

            with linter_utils.redirect_stdout(stdout):
                # This line invokes Pylint and prints its output
                # to the target stdout.
                python_utils.PRINT('Messages for Python 3 support:')
                pylinter_for_python3 = lint.Run(
                    current_files_to_lint + ['--py3k'], exit=False).linter

            if pylinter_for_python3.msg_status != 0:
                summary_message = stdout.getvalue()
                python_utils.PRINT(summary_message)
                summary_messages.append(summary_message)
                any_errors = True

            current_batch_start_index = current_batch_end_index

        if any_errors:
            summary_message = (
                '%s    Python linting for Python 3 compatibility failed'
                % _MESSAGE_TYPE_FAILED)
        else:
            summary_message = (
                '%s   %s Python files linted for Python 3 compatibility '
                '(%.1f secs)'
                % (_MESSAGE_TYPE_SUCCESS, num_py_files, (
                    time.time() - start_time)))

        python_utils.PRINT(summary_message)
        summary_messages.append(summary_message)

        python_utils.PRINT(
            'Python linting for Python 3 compatibility finished.')
        return summary_messages

    def perform_all_lint_checks(self):
        """Perform all the lint checks and returns the messages returned by all
        the checks.

        Returns:
            all_messages: str. All the messages returned by the lint checks.
        """
        pylintrc_path = os.path.join(os.getcwd(), '.pylintrc')

        config_pylint = '--rcfile=%s' % pylintrc_path

        config_pycodestyle = os.path.join(os.getcwd(), 'tox.ini')

        all_messages = []
        if not self.all_filepaths:
            python_utils.PRINT('')
            python_utils.PRINT('There are no Python files to lint.')
            return []

        all_messages.extend(
            self._lint_py_files(config_pylint, config_pycodestyle))

        all_messages.extend(self._lint_py_files_for_python3_compatibility())

        return all_messages


def get_linters(files_to_lint, verbose_mode_enabled=False):
    """Creates PythonLintChecksManager and ThirdPartyPythonLintChecksManager
        objects and return them.

    Args:
        files_to_lint: list(str). A list of filepaths to lint.
        verbose_mode_enabled: bool. True if verbose mode is enabled.

    Returns:
        tuple(PythonLintChecksManager, ThirdPartyPythonLintChecksManager). A
        2-tuple of custom and third_party linter objects.
    """
    custom_linter = PythonLintChecksManager(
        files_to_lint, verbose_mode_enabled)

    third_party_linter = ThirdPartyPythonLintChecksManager(
        files_to_lint, verbose_mode_enabled)

    return custom_linter, third_party_linter
