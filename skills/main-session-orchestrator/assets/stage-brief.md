# Stage brief

- ID, title, owner:
- Purpose: the question to resolve and why now.
- Inputs: paths/versions/hashes, dependency acceptance, sources that must not be silently replaced.
- Method, allowed actions, explicit non-goals:
- Resources/concurrency/time/cost/storage/retry budget:
- Artifacts and locations, downstream interfaces:
- Acceptance gates: observable outcome, verification method, evidence path for each.
- Recovery: logs/state, retry conditions, stop/return-to-Main conditions.
- State maintenance and shared-file merger:
- Successor dispatcher and source of user authorization:

Register actual session and job IDs on startup. Main accepts delivery; process exit does not complete the stage.
