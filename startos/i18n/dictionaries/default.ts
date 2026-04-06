export const DEFAULT_LANG = 'en_US'

const dict = {
  // main.ts
  'Starting Tailrelay!': 0,
  'Web UI': 1,
  'The web interface is ready': 2,
  'The web interface is not ready': 3,

  // interfaces.ts
  'Tailrelay Web UI': 4,
  'The Tailrelay browser interface': 5,
} as const

/**
 * Plumbing. DO NOT EDIT.
 */
export type I18nKey = keyof typeof dict
export type LangDict = Record<(typeof dict)[I18nKey], string>
export default dict
