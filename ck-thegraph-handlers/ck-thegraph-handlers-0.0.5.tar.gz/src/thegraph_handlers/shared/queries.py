"""
All the queries need to have the result set aliased under `result` key and
also have format-string argument.
"""


burns_query = """
        query ($address: Bytes, $since: BigInt, $until: BigInt) {
            result: burns(
                first: %d,
                orderBy: timestamp,
                orderDirection: asc,
                where: {sender: $address, timestamp_gte: $since, timestamp_lt: $until}
            ) {
                id
                sender
                to
                transaction {
                    id
                    blockNumber
                    timestamp
                }
                pair {
                    id
                    token0 {
                        id
                        symbol
                        name
                        decimals
                    }
                    token1 {
                        id
                        symbol
                        name
                        decimals
                    }
                }
                amount0
                amount1
                timestamp
                liquidity
            }
        }
    """

liquidity_pool_shares_query = """
        query($address: Bytes, $min: BigInt) {
            result: liquidityPositions(
                first: 500,
                where: {user: $address, liquidityTokenBalance_gt: $min}
            ) {
                user {
                    id
                }
                pair {
                    id
                    token0 {
                        id
                        symbol
                        name
                        totalSupply
                        decimals
                    }
                    token1 {
                        id
                        symbol
                        name
                        totalSupply
                        decimals
                    }
                    reserve0
                    reserve1
                    reserveUSD
                    totalSupply
                }
                liquidityTokenBalance
            }
        }
    """

mints_query = """
        query ($address: Bytes, $since: BigInt, $until: BigInt) {
            result: mints(
                first: %d,
                orderBy: timestamp,
                orderDirection: asc,
                where: {to: $address, timestamp_gte: $since, timestamp_lt: $until}
            )  {
                id
                sender
                to
                transaction {
                    id
                    blockNumber
                    timestamp
                }
                pair {
                    id
                    token0 {
                        id
                        symbol
                        name
                        decimals
                    }
                    token1 {
                        id
                        symbol
                        name
                        decimals
                    }
                }
                amount0
                amount1
                timestamp
                liquidity
            }
        }
    """

swaps_query = """
        query ($address: Bytes, $since: BigInt, $until: BigInt) {
            result: swaps(
                first: %d,
                orderBy: timestamp,
                orderDirection: asc,
                where: {to: $address, timestamp_gte: $since, timestamp_lt: $until}
            ) {
                id
                sender
                to
                transaction {
                    id
                    blockNumber
                    timestamp
                }
                pair {
                    id
                    token0 {
                        id
                        symbol
                        name
                        decimals
                    }
                    token1 {
                        id
                        symbol
                        name
                        decimals
                    }
                }
                amount0In
                amount0Out
                amount1In
                amount1Out
                amountUSD
                timestamp
            }
        }
    """
