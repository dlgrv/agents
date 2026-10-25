# Bulk Mailbox Cleanup (spam deletion + unsubscribes)

Use when asked to clean a mailbox of spam/ads, mass-unsubscribe from mailing lists, or delete messages in bulk via himalaya.

Procedure for cleaning a large mailbox (hundreds-thousands of messages) via himalaya. Order matters: census, classify, verify, move, unsubscribe, repeat.

## 1. Census before any deletion

Build a sender-frequency table by paginating through the whole mailbox, not just the first page:

```python
# v2 has no `search` subcommand — paginate `envelope list` and group by sender
for page in range(1, 20):
    r = subprocess.run(['himalaya','envelope','list','--page',str(page),'--page-size','50'], ...)
```

Promo senders hide deep in a large mailbox; a classification done from the top-50 view misses half of them and the user will ask again.

## 2. Verify ambiguous senders by sampling subjects

Before deleting any sender that could be transactional (marketplace, bank, wallet, delivery), sample its subject lines. The same sender name often sends BOTH receipts/orders and promo. Split by subject pattern and delete only the promo subset.

Never bulk-delete by sender name alone. Receipts, order statuses, security alerts, and fiscal documents (чеки) must survive the cleanup.

## 3. Move to Trash, never hard delete

`himalaya message move --to Trash <id> [<id>...]` accepts many ids per call. Run the mover as a background process with a small sleep between batches, and loop: re-list, collect matching ids, move — until a full re-scan returns zero matches. Trash gives a recovery window the user may need.

Message ids are relative to the current listing and shift after moves — collect ids and move them in the same iteration; do not cache id lists across passes.

## 4. Expect sender-name variants; repeat passes

The same mailing arrives under several spellings and display-name formats (dot vs space in «Яндекс Плюс», «HD» suffixes, localized vs English names). After each mover pass, re-run the census. Repeat until the total inbox count stops dropping. One pass over a hand-made name list is never enough.

## 5. Unsubscribe via headers, not body links

Read `himalaya message export <id> --full` and use the `List-Unsubscribe` / `List-Unsubscribe-Post` headers:

- **One-Click (RFC 8058)**: POST to the https URL with the `List-Unsubscribe-Post` body — the most reliable path. Needs network access; route through the user's proxy if direct connections fail.
- **mailto: fallback**: send a short unsubscribe note via `himalaya message send --no-save`.

Unsubscribe links embedded in older emails' bodies frequently 404 (tokens expired) — prefer header-based unsubscribe every time.

## 6. Sending gotchas

See SKILL.md: Yandex SMTP stalls behind shell proxies — strip `https_proxy`/`all_proxy` for `message send`.
