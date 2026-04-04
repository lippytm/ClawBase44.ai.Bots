"""Web3 integration adapter using the web3.py library."""

from __future__ import annotations

import logging
from typing import Any

from web3 import Web3
from web3.types import TxParams

from config.settings import get_settings

logger = logging.getLogger(__name__)


class Web3Adapter:
    """Thin wrapper around :class:`web3.Web3` for common on-chain operations.

    Supports read-only operations by default; signing requires a private key
    configured in ``WEB3_PRIVATE_KEY``.

    Usage::

        adapter = Web3Adapter()
        balance = adapter.get_balance("0xAbC...")
    """

    def __init__(self) -> None:
        settings = get_settings()
        self._w3 = Web3(Web3.HTTPProvider(settings.web3_rpc_url))
        self._wallet = settings.web3_wallet_address
        self._private_key = settings.web3_private_key
        if not self._w3.is_connected():
            logger.warning("Web3 provider is not connected: %s", settings.web3_rpc_url)

    @property
    def is_connected(self) -> bool:
        """Return *True* when the provider node is reachable."""
        return self._w3.is_connected()

    # ------------------------------------------------------------------
    # Read-only helpers
    # ------------------------------------------------------------------

    def get_balance(self, address: str | None = None) -> float:
        """Return ETH balance in ether for *address* (defaults to configured wallet).

        Parameters
        ----------
        address:
            Checksummed or plain Ethereum address.  Defaults to the wallet
            configured in settings.

        Returns
        -------
        float
            Balance in ETH.
        """
        addr = Web3.to_checksum_address(address or self._wallet)
        wei = self._w3.eth.get_balance(addr)
        return float(Web3.from_wei(wei, "ether"))

    def get_block_number(self) -> int:
        """Return the latest block number."""
        return self._w3.eth.block_number

    def get_gas_price_gwei(self) -> float:
        """Return current gas price in Gwei."""
        return float(Web3.from_wei(self._w3.eth.gas_price, "gwei"))

    # ------------------------------------------------------------------
    # Transaction helpers
    # ------------------------------------------------------------------

    def send_eth(self, to: str, amount_eth: float) -> str:
        """Send *amount_eth* ETH from the configured wallet to *to*.

        Requires ``WEB3_PRIVATE_KEY`` to be set.

        Parameters
        ----------
        to:
            Recipient address.
        amount_eth:
            Amount in ETH.

        Returns
        -------
        str
            Transaction hash (hex string).
        """
        if not self._private_key:
            raise ValueError("WEB3_PRIVATE_KEY must be configured to send transactions.")

        checksum_to = Web3.to_checksum_address(to)
        nonce = self._w3.eth.get_transaction_count(
            Web3.to_checksum_address(self._wallet), "latest"
        )
        tx: TxParams = {
            "to": checksum_to,
            "value": Web3.to_wei(amount_eth, "ether"),
            "gas": 21000,
            "gasPrice": self._w3.eth.gas_price,
            "nonce": nonce,
            "chainId": self._w3.eth.chain_id,
        }
        signed = self._w3.eth.account.sign_transaction(tx, private_key=self._private_key)
        tx_hash = self._w3.eth.send_raw_transaction(signed.raw_transaction)
        hex_hash = tx_hash.hex()
        logger.info("ETH transfer sent: %s ETH → %s  tx=%s", amount_eth, to, hex_hash)
        return hex_hash

    def call_contract(
        self,
        address: str,
        abi: list[dict[str, Any]],
        function_name: str,
        *args: Any,
    ) -> Any:
        """Call a read-only smart contract function.

        Parameters
        ----------
        address:
            Contract address.
        abi:
            Contract ABI as a Python list.
        function_name:
            The name of the function to call.
        *args:
            Positional arguments forwarded to the function.

        Returns
        -------
        Any
            Return value of the contract function.
        """
        contract = self._w3.eth.contract(
            address=Web3.to_checksum_address(address), abi=abi
        )
        fn = getattr(contract.functions, function_name)
        return fn(*args).call()
