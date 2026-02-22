import { compat, types as T } from "../deps.ts";

export const getConfig: T.ExpectedExports.getConfig = compat.getConfig({
  "tailscale-auth-key": {
    type: "string",
    name: "Tailscale Auth Key",
    description:
      "Reusable auth key from your Tailscale admin console (https://login.tailscale.com/admin/settings/keys).",
    nullable: true,
    masked: true,
    copyable: true,
    placeholder: "tskey-auth-...",
  },
});
