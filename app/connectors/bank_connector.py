from abc import ABC, abstractmethod
from typing import Iterable, Dict, Any, IO


class BankConnector(ABC):
    @abstractmethod
    def import_transactions(self, file: IO, account_id: str = None) -> Iterable[Dict[str, Any]]:
        """Parse an uploaded bank export and yield normalized transaction dicts.

        Each dict should match the canonical transaction input shape expected by the service.
        """
        raise NotImplementedError()
