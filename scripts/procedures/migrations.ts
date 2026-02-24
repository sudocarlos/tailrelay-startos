import { compat, types as T } from "../deps.ts";

export const migration: T.ExpectedExports.migration = compat.migrations
  .fromMapping({
    "0.4.1": {
      up: compat.migrations.updateConfig(
        (config: any) => config,
        true,
        { version: "0.4.1", type: "script" }
      ),
      down: compat.migrations.updateConfig(
        (config: any) => config,
        true,
        { version: "0.4.2", type: "script" }
      ),
    },
    "0.4.2": {
      up: compat.migrations.updateConfig(
        (config: any) => config,
        true,
        { version: "0.4.2", type: "script" }
      ),
      down: compat.migrations.updateConfig(
        (config: any) => config,
        true,
        { version: "0.4.3", type: "script" }
      ),
    },
  }, "0.4.3");
