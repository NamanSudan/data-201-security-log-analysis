# Normalization Rules Sheet

Based on: Lecture 4 (Normalization), Lecture 5 (Review + Quiz 2)
Professor: Dr. Guannan Liu, DATA 201, Spring 2026

Use this to check raw data for violations at each normal form level during notebook analysis.

---

## Functional Dependencies (prerequisite)

A functional dependency X -> Y means: if two rows have the same value of X, they must have the same value of Y. Knowing X is enough to know Y.

How to identify FDs:
- Think about business rules, not just what you see in sample data
- For each potential determinant, ask: "Does this attribute uniquely determine those other attributes?"
- Document the reasoning

---

## 1NF - First Normal Form

**Rule:** No repeating groups, no arrays/lists. Every column holds a single, indivisible (atomic) value.

**What to check in raw data:**
- Are there columns that contain lists, arrays, or comma-separated values?
- Are there columns that contain multiple values packed into one cell?
- Are there repeating groups (same type of information stored in multiple columns, like phone1, phone2, phone3)?

**Violation examples:**
- A `groups` column containing `["servers", "intranet", "dmz"]` (list in one cell)
- A `labels` column containing `["escalate", "attacker_change_user"]` (array)
- Columns like `ip1`, `ip2`, `ip3` (repeating group)

**Resolution:** Explode repeating groups so each cell holds one atomic value. Multi-valued fields become separate rows or separate tables (junction tables).

**From Lecture 4 (Slide 26):** "Every column should hold a single value, no lists, no repeating groups."

---

## 2NF - Second Normal Form

**Rule:** Must be in 1NF + no partial dependencies. Every non-key attribute must depend on the ENTIRE primary key, not just part of it.

**When it applies:** Only relevant when a table has a composite primary key (two or more columns as the key). If the primary key is a single column, 2NF is automatically satisfied - partial dependencies are impossible.

**What to check in raw data:**
- After resolving 1NF, does the table have a composite key?
- If yes: does every non-key column depend on the WHOLE composite key, or only part of it?
- If a non-key column depends on only part of the composite key, that is a partial dependency (2NF violation)

**Violation example (from Lecture 4, Slide 32):**
- Table key = (OrderID, ProductID)
- CustomerName depends only on OrderID, not on ProductID
- This is a partial dependency: CustomerName depends on part of the key

**Resolution:** Split the table so that attributes depending on part of the key move to a table where that part is the full key.

**From Lecture 4 (Slide 33):** "If a table has a composite primary key, then every non-key attribute must depend on the whole key, not just part of it."

**Important for our project:** After 1NF decomposition, junction tables like host_groups(host_id, group_name) have composite keys but typically no non-key attributes, so 2NF is satisfied automatically. Check any table where a composite key has additional non-key columns.

---

## 3NF - Third Normal Form

**Rule:** Must be in 2NF + no transitive dependencies. No non-key attribute depends on another non-key attribute. Every non-key attribute must depend directly on the primary key.

**What to check in raw data:**
- For each non-key column, does it depend directly on the primary key, or does it depend on another non-key column?
- Pattern to look for: PK -> A -> B, where A and B are both non-key. If knowing A is enough to know B without needing PK, that is a transitive dependency.
- Look for groups of columns where one determines the others (but none of them are the key)

**Violation example (from Lecture 4, Slide 41):**
- Student table: StudentID -> SchoolID -> SchoolName
- SchoolID is non-key. SchoolName depends on SchoolID (non-key), not directly on StudentID.
- This is a transitive dependency.

**Our project example:**
- hosts_raw: host_key -> distribution_release -> (distribution, distribution_version)
- distribution_release is non-key. distribution and distribution_version depend on distribution_release (non-key), not directly on host_key.
- This is a transitive dependency (3NF violation).

**Resolution:** Extract the transitively dependent attributes into a separate table where the intermediate determinant becomes the primary key.

**From Lecture 4 (Slide 43):** "A table is in 3NF if it is already in 2NF, and every non-key attribute depends only on the key, not on another non-key attribute."

---

## Quick Reference (Lecture 4, Slide 47)

| Normal Form | Rule |
|---|---|
| 1NF | No repeating groups, no arrays/lists. Every value atomic. |
| 2NF | 1NF + no partial dependencies (non-key attributes must depend on the whole key). |
| 3NF | 2NF + no transitive dependencies (non-key depending on another non-key). |
| BCNF | Stronger than 3NF. Every determinant must be a candidate key. |

For most real-world business systems: designing up to 3NF is usually good enough.

---

## Normalization Process (Lecture 4, Slide 49)

1. Start with a flat, denormalized table (DataFrame/CSV)
2. 1NF: Explode repeating groups so every cell holds a single atomic value
3. Identify the composite key (if one exists)
4. Identify functional dependencies using business rules
5. 2NF: Remove partial dependencies by splitting into separate tables per entity
6. 3NF: Check for and remove transitive dependencies

---

## Checklist for Notebook Analysis

For each raw data file being analyzed:

1NF check:
- [ ] Identify all multi-valued fields (lists, arrays, comma-separated)
- [ ] Identify all repeating groups (phone1/phone2/phone3 patterns)
- [ ] Document each violation with: field name, value range (min/max per row), distinct values count, resolution direction

2NF check:
- [ ] After 1NF resolution, does any resulting table have a composite key?
- [ ] If yes: does every non-key attribute depend on the full composite key?
- [ ] If no composite key exists (single-column PK): state "2NF satisfied - single-column primary key"

3NF check:
- [ ] List all non-key-to-non-key dependencies found (A -> B where neither A nor B is the primary key)
- [ ] For each: confirm it is a transitive dependency (PK -> A -> B pattern)
- [ ] Document the resolution direction (extract into lookup table)

FD identification:
- [ ] List all functional dependencies with business rule reasoning
- [ ] Identify candidate keys
- [ ] Flag any FDs that indicate 2NF or 3NF violations