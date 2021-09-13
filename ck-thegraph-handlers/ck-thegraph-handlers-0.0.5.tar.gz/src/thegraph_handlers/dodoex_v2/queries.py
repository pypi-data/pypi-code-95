"""
https://github.com/DODOEX/dodoex_v2_subgraph/blob/master/subgraphs/dodoex/dodoex.graphql
"""


tokens_query = """
        query {
            result: lpTokens(
                first: 1000,
                orderBy: symbol,
                orderDirection: asc
            ) {
                symbol
                name
                id
                decimals
                totalSupply
                pair {
                    baseToken {
                        symbol
                        name
                        id
                        decimals
                    }
                    quoteToken {
                        symbol
                        name
                        id
                        decimals
                    }
                    baseReserve
                    quoteReserve
                }
            }
        }

    """

swaps_query = """
        query ($address: Bytes, $since: BigInt, $until: BigInt) {
            result: orderHistories(
                first: %d,
                orderBy: timestamp,
                orderDirection: asc,
                where: {sender: $address, timestamp_gte: $since, timestamp_lt: $until}
            ) {
                amountIn
                amountOut
                volumeUSD
                hash
                block
                timestamp
                sender
                id
                toToken {
                    symbol
                    name
                    id
                    decimals
                }
                fromToken {
                    symbol
                    name
                    id
                    decimals
                }
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
                liquidityTokenBalance
                liquidityTokenInMining
                lpToken {
                    symbol
                    name
                    id
                    decimals
                    totalSupply
                    pair {
                        baseToken {
                            symbol
                            name
                            id
                            decimals
                            totalSupply
                        }
                        quoteToken {
                            symbol
                            name
                            id
                            decimals
                            totalSupply
                        }
                        baseReserve
                        quoteReserve
                    }
                }
            }
        }
    """

mints_query = """
        query ($address: Bytes, $since: BigInt, $until: BigInt) {
            result: liquidityHistories(
                first: %d,
                orderBy: timestamp,
                orderDirection: asc,
                where: {from: $address, type: "DEPOSIT", timestamp_gte: $since, timestamp_lt: $until}
            ) {
                id
                from
                hash
                amount
                block
                timestamp
                baseAmountChange
                quoteAmountChange
                lpToken {
                    symbol
                    name
                    id
                    decimals
                    totalSupply
                    pair {
                        baseToken {
                            symbol
                            name
                            id
                            decimals
                        }
                        quoteToken {
                            symbol
                            name
                            id
                            decimals
                        }
                    }
                }
            }
        }
    """

burns_query = """
        query ($address: Bytes, $since: BigInt, $until: BigInt) {
            result: liquidityHistories(
                first: %d,
                orderBy: timestamp,
                orderDirection: asc,
                where: {from: $address, type: "WITHDRAW", timestamp_gte: $since, timestamp_lt: $until}
            ) {
                id
                from
                hash
                amount
                block
                timestamp
                baseAmountChange
                quoteAmountChange
                lpToken {
                    symbol
                    name
                    id
                    decimals
                    totalSupply
                    pair {
                        baseToken {
                            symbol
                            name
                            id
                            decimals
                        }
                        quoteToken {
                            symbol
                            name
                            id
                            decimals
                        }
                    }
                }
            }
        }
    """
