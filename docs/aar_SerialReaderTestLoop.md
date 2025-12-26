# AFTER-ACTION REPORT (AAR): SerialReader Debugging Loop

## Mission Objective
Stabilize the SerialReader implementation so that unit tests pass without modifying the tests, while preserving architectural boundaries and avoiding circular imports.

## Summary of Events

1. Import resolution behaved differently than expected.
   The shim module existed and was named correctly, but Python continued binding Serial to the real pyserial class. A diagnostic confirmed that the Serial attribute inside the shim pointed to serial.serialposix.Serial. This indicated that the shim module was imported, but the Serial name inside SerialReader was bound before the test patch applied. This reflects a known Python mocking pitfall: patching a module attribute does not affect names already imported into another module.

2. The shim was correct, but the import style prevented patching.
   SerialReader originally used a direct import:
   `from app.serial_reader.serial import Serial`
   This copied the object into the local namespace. When the test patched `app.serial_reader.serial.Serial`, the already-imported name remained unchanged. Switching to a module-level import (`import app.serial_reader.serial as serial_shim`) ensured that the patched attribute was used at runtime.

3. The package __init__.py introduced eager imports and shadowing.
   Earlier versions of __init__.py re-exported Serial, which forced early import of the shim, shadowed the module namespace, and interfered with the test patch path. Cleaning the file to expose only `parse_geiger_csv` resolved the namespace issues.

## Key Lessons for Future Debugging

1. Confirm that the module being imported is the intended one.
   Use a diagnostic such as printing the `__file__` attribute to verify the actual module path.

2. Confirm that patching is applied where the symbol is used, not where it is defined.
   Direct imports bind early and are not patch-friendly. Module imports bind late and allow patching.

3. Confirm that the package structure is not shadowing or being shadowed.
   Watch for directories named like top-level packages, missing `__init__.py` files, or re-exports that alter import order.

4. Confirm that no circular imports are forcing fallback behavior.
   Circular imports often cause partially initialized modules or fallback to top-level packages.

5. Confirm that names are not being bound too early for patches to affect them.
   Direct imports bind early. Module imports bind late and are safer for testing.

## Project Status at End of Session
SerialReader tests are passing.
The shim architecture is correct.
The import graph is stable.
No circular imports remain.
Deterministic behavior is restored.

## Next Engineering Task
Align IngestionLoop with the corrected SerialReader contract.
This includes setting the `_handle_parsed` callback correctly, ensuring the ingestion loop uses the patched SerialReader behavior, avoiding real serial port access, and satisfying the ingestion loop test suite.

## Upcoming Work
Resume repo-root consolidation.
Eliminate drift between application code and deployment artifacts.
Prepare CI/CD automation and promotion workflows.
