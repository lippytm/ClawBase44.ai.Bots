/**
 * Web3 integration module.
 * Connects to EVM-compatible blockchains via JSON-RPC.
 * Does NOT import heavy wallet libraries to keep the module lightweight;
 * contract calls are made through raw eth_call JSON-RPC requests.
 */

const fetch = (...args) =>
  import("node-fetch").then(({ default: f }) => f(...args));

class Web3Integration {
  constructor(config = {}) {
    this.rpcUrl = config.rpcUrl || process.env.WEB3_RPC_URL;
    this.chainId = config.chainId || parseInt(process.env.WEB3_CHAIN_ID || "1", 10);
    this.contractAddress = config.contractAddress || process.env.WEB3_CONTRACT_ADDRESS;
  }

  async _rpc(method, params = []) {
    const res = await fetch(this.rpcUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        jsonrpc: "2.0",
        id: Date.now(),
        method,
        params,
      }),
    });
    if (!res.ok) {
      throw new Error(`Web3 RPC request failed: ${res.status} ${res.statusText}`);
    }
    const json = await res.json();
    if (json.error) {
      throw new Error(`Web3 RPC error: ${json.error.message}`);
    }
    return json.result;
  }

  async getBlockNumber() {
    const hex = await this._rpc("eth_blockNumber");
    return parseInt(hex, 16);
  }

  async getBalance(address) {
    const hex = await this._rpc("eth_getBalance", [address, "latest"]);
    return parseInt(hex, 16);
  }

  async getChainId() {
    const hex = await this._rpc("eth_chainId");
    return parseInt(hex, 16);
  }

  async call(contractAddress, data, blockTag = "latest") {
    const addr = contractAddress || this.contractAddress;
    return this._rpc("eth_call", [{ to: addr, data }, blockTag]);
  }

  async getTransactionReceipt(txHash) {
    return this._rpc("eth_getTransactionReceipt", [txHash]);
  }
}

module.exports = Web3Integration;
