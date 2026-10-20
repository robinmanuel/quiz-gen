/** Tiny class-name joiner — falsy values are dropped. */
export function cx(...values: Array<string | false | null | undefined>): string {
  return values.filter(Boolean).join(' ')
}
