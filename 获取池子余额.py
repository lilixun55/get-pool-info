#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from typing import Any

import requests


DEFAULT_TIMEOUT_SECS = 20
DEXSCREENER_BASE = "https://api.dexscreener.com/latest/dex/pairs/solana"


@dataclass
class BalanceResult:
    dex: str | None
    pool_address: str
    source: str
    token_a_mint: str | None
    token_b_mint: str | None
    token_a_symbol: str | None
    token_b_symbol: str | None
    raw_amount_a: str | None
    raw_amount_b: str | None
    ui_amount_a: str | None
    ui_amount_b: str | None
    liquidity_usd: str | None
    price_usd: str | None
    note: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data = {
            "dex": self.dex,
            "pool_address": self.pool_address,
            "source": self.source,
            "token_a_mint": self.token_a_mint,
            "token_b_mint": self.token_b_mint,
            "token_a_symbol": self.token_a_symbol,
            "token_b_symbol": self.token_b_symbol,
            "raw_amount_a": self.raw_amount_a,
            "raw_amount_b": self.raw_amount_b,
            "ui_amount_a": self.ui_amount_a,
            "ui_amount_b": self.ui_amount_b,
            "liquidity_usd": self.liquidity_usd,
            "price_usd": self.price_usd,
        }
        if self.note:
            data["note"] = self.note
        return data


class DexScreenerFetcher:
    def __init__(self, timeout_secs: int = DEFAULT_TIMEOUT_SECS):
        self.timeout_secs = timeout_secs
        self.http = requests.Session()

    def fetch(self, pool_address: str) -> BalanceResult:
        url = f"{DEXSCREENER_BASE}/{pool_address}"
        response = self.http.get(url, timeout=self.timeout_secs)
        response.raise_for_status()
        payload = response.json()

        pairs = payload.get("pairs") or []
        if not pairs:
            raise RuntimeError("DexScreener未返回该池子数据")

        pair = pairs[0]
        base = pair.get("baseToken") or {}
        quote = pair.get("quoteToken") or {}
        liquidity = pair.get("liquidity") or {}
        price_usd = pair.get("priceUsd")

        raw_amount_a = liquidity.get("base")
        raw_amount_b = liquidity.get("quote")
        liquidity_usd = liquidity.get("usd")

        return BalanceResult(
            dex=pair.get("dexId"),
            pool_address=pair.get("pairAddress") or pool_address,
            source="dexscreener",
            token_a_mint=base.get("address"),
            token_b_mint=quote.get("address"),
            token_a_symbol=base.get("symbol"),
            token_b_symbol=quote.get("symbol"),
            raw_amount_a=str(raw_amount_a) if raw_amount_a is not None else None,
            raw_amount_b=str(raw_amount_b) if raw_amount_b is not None else None,
            ui_amount_a=str(raw_amount_a) if raw_amount_a is not None else None,
            ui_amount_b=str(raw_amount_b) if raw_amount_b is not None else None,
            liquidity_usd=str(liquidity_usd) if liquidity_usd is not None else None,
            price_usd=str(price_usd) if price_usd is not None else None,
            note="DexScreener返回的是池子流动性口径（base/quote）。",
        )


def print_human(result: BalanceResult) -> None:
    print(f"DEX: {result.dex}")
    print(f"池子: {result.pool_address}")
    print(f"来源: {result.source}")
    print(f"Token A Mint: {result.token_a_mint}")
    print(f"Token B Mint: {result.token_b_mint}")
    print(f"Token A Symbol: {result.token_a_symbol}")
    print(f"Token B Symbol: {result.token_b_symbol}")
    print(f"余额A(raw/ui): {result.raw_amount_a} / {result.ui_amount_a}")
    print(f"余额B(raw/ui): {result.raw_amount_b} / {result.ui_amount_b}")
    print(f"流动性(USD): {result.liquidity_usd}")
    print(f"价格(USD): {result.price_usd}")
    if result.note:
        print(f"说明: {result.note}")


def main() -> None:
    parser = argparse.ArgumentParser(description="查询池子余额（仅 DexScreener API）")
    parser.add_argument("--pool", help="池子地址；不传则进入交互模式")
    parser.add_argument("--json", action="store_true", help="以JSON输出")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SECS, help="HTTP超时时间(秒)")
    args = parser.parse_args()

    fetcher = DexScreenerFetcher(timeout_secs=args.timeout)

    def run_once(pool_address: str) -> None:
        try:
            result = fetcher.fetch(pool_address.strip())
            if args.json:
                print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
            else:
                print_human(result)
        except Exception as exc:
            print(f"查询失败: {exc}")

    if args.pool:
        run_once(args.pool)
        return

    print("获取池子余额工具（仅 DexScreener）")
    print("输入池子地址后回车查询；输入 quit/exit 退出")
    print("-" * 60)
    while True:
        text = input("池子地址> ").strip()
        if text.lower() in {"quit", "exit", "q"}:
            print("再见！")
            break
        if not text:
            continue
        run_once(text)
        print("-" * 60)


if __name__ == "__main__":
    main()
