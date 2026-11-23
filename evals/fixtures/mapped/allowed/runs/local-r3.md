# Fictional run record

Revision: demo-r3. Environment: isolated Python fixture; no server or concurrent calls.
Scenario: call `approve` twice in sequence with the same set and item, then check the set size.
Observed: responses were `approved` then `already_approved`; final size was 1. The sequential exercise passed.
No production, load or concurrent-worker validation was run in this record.
