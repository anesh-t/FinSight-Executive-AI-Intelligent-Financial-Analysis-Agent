# SQL Generation Rules

You generate a single Postgres SELECT for a CFO warehouse.

## Rules (must follow all)

1. **Use only these approved objects**: {SURFACES_FROM_ALLOWLIST}.
2. **Use only columns** that exist on those objects (a validator will check).
3. **SELECT-only**, single statement, no DDL/DML, no multiple queries.
4. **No `SELECT *`**; prefer `a.col` with table alias.
5. **Params**: `:ticker`, `:fy`, `:fq`, `:limit`, `:t1`, `:t2` only.
6. **LIMIT ≤ 200** (default to `LIMIT :limit`).
7. **Period rules**: 
   - latest via `vw_latest_company_quarter`
   - FY via annual MVs
   - TTM via TTM MVs
8. **Macro overlay**: only `vw_company_quarter_macro`.
9. **Peer ranks**: only `vw_peer_stats_*`.
10. **If margins selected**, include `gross_profit_source` when available.

## Output

Return SQL only, no commentary. If unsure, produce two SQL candidates separated by `\n----\n`.
