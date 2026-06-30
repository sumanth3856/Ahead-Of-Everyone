/**
 * IST (Asia/Kolkata, UTC+5:30) date/time utilities.
 * All display-facing timestamps in the app MUST go through these helpers.
 */

const LOCALE = "en-IN";
const TZ = "Asia/Kolkata";

/** Format a UTC timestamp string or Date as a short IST time, e.g. "02:30 PM" */
export function toISTTime(value: string | Date): string {
  const date = typeof value === "string" ? new Date(value) : value;
  return date.toLocaleTimeString(LOCALE, {
    timeZone: TZ,
    hour: "2-digit",
    minute: "2-digit",
    hour12: true,
  });
}

/** Format a UTC timestamp string or Date as a short IST date, e.g. "30 Jun 2026" */
export function toISTDate(value: string | Date): string {
  const date = typeof value === "string" ? new Date(value) : value;
  return date.toLocaleDateString(LOCALE, {
    timeZone: TZ,
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

/** Format a UTC timestamp string or Date as full IST datetime, e.g. "30 Jun 2026, 02:30 PM IST" */
export function toISTDateTime(value: string | Date): string {
  return `${toISTDate(value)}, ${toISTTime(value)} IST`;
}
