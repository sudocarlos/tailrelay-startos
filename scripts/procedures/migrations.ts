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
    "0.4.3": {
      up: compat.migrations.updateConfig(
        (config: any) => config,
        true,
        { version: "0.4.3", type: "script" }
      ),
      down: compat.migrations.updateConfig(
        (config: any) => config,
        true,
        { version: "0.5.0", type: "script" }
      ),
    },
    "0.5.0": {
      up: compat.migrations.updateConfig(
        (config: any) => config,
        true,
        { version: "0.5.0", type: "script" }
      ),
      down: compat.migrations.updateConfig(
        (config: any) => config,
        true,
        { version: "0.6.0", type: "script" }
      ),
    },
    "0.6.0": {
      up: compat.migrations.updateConfig(
        (config: any) => config,
        true,
        { version: "0.6.0", type: "script" }
      ),
      down: compat.migrations.updateConfig(
        (config: any) => config,
        true,
        { version: "0.6.1", type: "script" }
      ),
    },
    "0.6.1": {
      up: compat.migrations.updateConfig(
        (config: any) => config,
        true,
        { version: "0.6.1", type: "script" }
      ),
      down: compat.migrations.updateConfig(
        (config: any) => config,
        true,
        { version: "0.7.0", type: "script" }
      ),
    },
    "0.7.0": {
      up: compat.migrations.updateConfig(
        (config: any) => config,
        true,
        { version: "0.7.0", type: "script" }
      ),
      down: compat.migrations.updateConfig(
        (config: any) => config,
        true,
        { version: "0.7.1", type: "script" }
      ),
    },
    "0.7.1": {
      up: compat.migrations.updateConfig(
        (config: any) => config,
        true,
        { version: "0.7.1", type: "script" }
      ),
      down: compat.migrations.updateConfig(
        (config: any) => config,
        true,
        { version: "0.8.0", type: "script" }
      ),
    },
    "0.8.0": {
      up: compat.migrations.updateConfig(
        (config: any) => config,
        true,
        { version: "0.8.0", type: "script" }
      ),
      down: compat.migrations.updateConfig(
        (config: any) => config,
        true,
        { version: "0.8.1", type: "script" }
      ),
    },
    "0.8.1": {
      up: compat.migrations.updateConfig(
        (config: any) => config,
        true,
        { version: "0.8.1", type: "script" }
      ),
      down: compat.migrations.updateConfig(
        (config: any) => config,
        true,
        { version: "0.8.2", type: "script" }
      ),
    },
    "0.8.2": {
      up: compat.migrations.updateConfig(
        (config: any) => config,
        true,
        { version: "0.8.2", type: "script" }
      ),
      down: compat.migrations.updateConfig(
        (config: any) => config,
        true,
        { version: "0.8.3", type: "script" }
      ),
    },
    "0.8.3": {
      up: compat.migrations.updateConfig(
        (config: any) => config,
        true,
        { version: "0.8.3", type: "script" }
      ),
      down: compat.migrations.updateConfig(
        (config: any) => config,
        true,
        { version: "0.8.4", type: "script" }
      ),
    },
    "0.8.4": {
      up: compat.migrations.updateConfig(
        (config: any) => config,
        true,
        { version: "0.8.4", type: "script" }
      ),
      down: compat.migrations.updateConfig(
        (config: any) => config,
        true,
        { version: "0.8.5", type: "script" }
      ),
    },
    "0.8.5": {
      up: compat.migrations.updateConfig(
        (config: any) => config,
        true,
        { version: "0.8.5", type: "script" }
      ),
      down: compat.migrations.updateConfig(
        (config: any) => config,
        true,
        { version: "0.8.6", type: "script" }
      ),
    },
  }, "0.8.6");