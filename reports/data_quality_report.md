# Data Quality Report — Lead Management

**Database:** LEADMANAGEMENT | **Schema:** PUBLIC

## 1. LEADS Table

| Metric | Value |
|--------|-------|
| Total rows | 100 |

### Completeness (nulls)
| Column | Null count | Pass |
|--------|------------|------|
| ID | 0 | ✅ |
| STATE | 0 | ✅ |
| CREATEDDATEUTC | 0 | - |
| SOLDEMPLOYEE | 0 | - |
| CANCELLEDEMPLOYEE | 50 | - |
| UPDATEDDATEUTC | 0 | - |

### State distribution
| State | Label | Count |
|-------|-------|-------|
| 0 | Sold | 25 |
| 1 | Cancellation Requested | 25 |
| 2 | Cancelled | 25 |
| 3 | Cancellation Rejected | 25 |

### Uniqueness
| Metric | Value | Pass |
|--------|-------|------|
| Duplicate IDs | 20 leads with multiple rows | ✅ Expected (lead lifecycle) |

## 2. LeadEvents Table

| Metric | Value |
|--------|-------|
| Total rows | 100 |

### Event type distribution
| EventType | Count |
|------------|-------|
| LeadCancellationRequested | 25 |
| LeadCancellationRejected | 25 |
| LeadSold | 25 |
| LeadCancelled | 25 |

### Completeness (nulls)
| Column | Null count | Pass |
|--------|------------|------|
| LEADID | 0 | ✅ |
| EVENTTYPE | 0 | ✅ |
| EVENTDATE | 0 | - |

## 3. Referential Integrity

| Check | Result | Pass |
|-------|--------|------|
| LeadEvents.LEADID exists in LEADS | 0 orphan events | ✅ |

## 4. Summary

- **LEADS:** 100 rows
- **LeadEvents:** 100 rows
- **Orphan events:** 0

**Overall: ✅ Data quality checks passed**