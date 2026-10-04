# Right of reply

Precondition for publication. The record lives here so the fact of contact,
not just the content, is auditable.

The *Broadcasting Services Act 1992* s 17 requires a reasonable opportunity to
respond to a matter of public interest that is capable of damaging reputation.
In practice: send the specific claims, in writing, to the party's registered
address, with a real deadline, and publish the reply in full if one is given.

---

## Status

| Field | Value |
|---|---|
| Thesis sent | Not yet. Thesis settled by task 0001; blocked on the contact address. |
| Contact address | Not on file. AEC search 2026-10-04 found the registered address is not published. See Log. |
| Date sent | — |
| Deadline given | — |
| Date replied | — |
| Reply published | — |

---

## Log

Append-only, newest last.

### 2026-10-04 — AEC searched for the registered address; not published where expected

Task 0003 was expected to surface the party's registered address incidentally.
Searched on 2026-10-04 and it is **not** published in an accessible form. What was
tried, all against `aec.gov.au`:

| URL | Result |
|---|---|
| `/parties/` | HTTP 200, body is "404 - Sauce not found" |
| `/parties/registered-entities.htm` | HTTP 200, same 404 body |
| `/Parties_and_Representatives/party_registration/` | Real page. Requirements and forms only. **No list of registered parties.** |
| `/Parties_and_Representatives/financial_disclosure/transparency-register/` | Real page. No One Nation entry found. |
| `.../transparency-register/annual-returns.htm` | Real page. Links a bulk download, `All-Annual-Data.zip`, 13 files, 2.3MB. |
| `.../transparency-register/profiles/` | HTTP 200, 404 body. Dead. |

`Party Returns.csv` inside the bulk download was unpacked and inspected. Its
columns are `Financial Year`, `Name`, `Party Group`, `Total Receipts`,
`Total Payments`, `Total Debts`, `Total Discretionary Benefits`. **There is no
address column.** The annual returns carry financial disclosure only.

Note the URL case: the live path is `Parties_and_Representatives`, capitalised.
The lowercase `/parties/` paths return a success status with a 404 body, which is
the exact trap recorded in `AGENTS.md` gotchas and the reason every fetch here
was validated on page title rather than status code.

**Conclusion: the address is not obtainable from published AEC pages.** It sits on
the registration statement lodged by the party, which the AEC holds but does not
publish. Under `AGENTS.md` and the instruction in `TASKS.md` `## BLOCKED`, an
address must not be taken from a news report or a social media profile, so none
is recorded here.

**Next options, none of which this project should choose unilaterally:**

1. **AEC freedom of information request** for the party's current registration
   statement. Slow, and the address is the only thing actually needed.
2. **Written request to the AEC's party registration team** asking how a
   member of the public may obtain a registered party's address. A short,
   specific question with a statutory hook.
3. **The party's own published contact channel** — a letter to the party at the
   address it publishes for correspondence on its own website, which is a
   channel the party has chosen to publish. This is not "an address from a news
   report"; it is the party's own published contact point. Defensible, and
   available now. Still leaves the substance of non-negotiable 3, which requires
   correspondence to the **registered** address.

Option 3 unblocks the clock fastest and option 2 is the one that satisfies the
standard as written. Doing 3 and 2 together is the pragmatic answer. **This needs
Dale's decision.**


### 2026-10-03 — Recipient not identified

No contact address on file. Do not take an address from a news report or a
social media profile. The party's registered address is on its most recent
party registration statement, lodged with the AEC and published by the AEC.

Task 0003 (source the AEC data) should surface this incidentally, since the
registration statements and the funding returns are both on the AEC site.

Note that the federal registered address is a party office or a lawyer's
address, not a private residence, and correspondence to it is expected.

---

## Method

1. Draft the thesis as one sentence, plus the specific claims that could damage
   reputation. Not "here is a draft" — the actual claims.
2. Send to the registered address, addressed to the party, by email and post.
3. Give a deadline of at least five business days. State the date.
4. If no reply arrives by the deadline, record that fact and publish.
5. If a reply arrives, publish it **verbatim and in full**, unedited, in a
   clearly marked block. Do not summarise a hostile reply favourably and do not
   omit an inconvenient one.
6. Note any correction the reply produces in `corrections.md`.