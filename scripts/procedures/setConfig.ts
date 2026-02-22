import { compat, types as T } from "../deps.ts";

export const setConfig: T.ExpectedExports.setConfig = async (
  effects,
  config,
) => {
  return await compat.setConfig(effects, config);
};
