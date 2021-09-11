from contextlib import AbstractContextManager
from typing import Any, Iterable, List

from typing_extensions import Protocol


class CreateTransactionCall(Protocol):
    def __call__(self) -> str:
        ...


class CommitTransactionCall(Protocol):
    def __call__(self, transaction_id: str) -> str:
        ...


class AbortTransactionCall(Protocol):
    def __call__(self, transaction_id: str) -> str:
        ...


class AppendRowsCall(Protocol):
    def __call__(self, transaction_id: str, rows: Iterable[Any]) -> List[str]:
        ...


class TransactionManager(AbstractContextManager):
    """Implements a Python context manager, managing state for a Benchling transaction. Upon
    exit, the transaction manager will automatically attempt to commit the transaction. If
    an error is encountered, it will instead abort the transaction."""

    _transaction_id: str
    _create_transaction_call: CreateTransactionCall
    _commit_transaction_call: CommitTransactionCall
    _abort_transaction_call: AbortTransactionCall
    _append_row_call: AppendRowsCall

    def __init__(
        self,
        create_transaction_call: CreateTransactionCall,
        commit_transaction_call: CommitTransactionCall,
        abort_transaction_call: AbortTransactionCall,
        append_row_call: AppendRowsCall,
    ):
        self._create_transaction_call = create_transaction_call
        self._commit_transaction_call = commit_transaction_call
        self._abort_transaction_call = abort_transaction_call
        self._append_row_call = append_row_call

    def __enter__(self) -> "TransactionManager":
        self._transaction_id = self._create_transaction_call()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback) -> bool:
        if exc_type:
            self.abort()
        else:
            self.commit()
        return True

    def append(self, row: Any) -> List[str]:
        return self.extend([row])

    def extend(self, rows: Iterable[Any]) -> List[str]:
        return self._append_row_call(transaction_id=self._transaction_id, rows=rows)

    def commit(self) -> str:
        return self._commit_transaction_call(self._transaction_id)

    def abort(self) -> str:
        return self._abort_transaction_call(self._transaction_id)
