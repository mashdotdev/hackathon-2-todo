// Polyfill for crypto.randomUUID in non-secure contexts (HTTP)
// This must be imported before any code that uses crypto.randomUUID

if (typeof globalThis !== "undefined" && typeof globalThis.crypto !== "undefined") {
  const crypto = globalThis.crypto as Crypto & { randomUUID?: () => string };
  if (!crypto.randomUUID) {
    crypto.randomUUID = function (): `${string}-${string}-${string}-${string}-${string}` {
      // Implementation based on the official spec
      const getRandomHex = (bytes: number): string => {
        const arr = new Uint8Array(bytes);
        globalThis.crypto.getRandomValues(arr);
        return Array.from(arr, (b) => b.toString(16).padStart(2, "0")).join("");
      };

      const timeLow = getRandomHex(4);
      const timeMid = getRandomHex(2);
      const timeHiAndVersion = (0x4000 | (parseInt(getRandomHex(2), 16) & 0x0fff)).toString(16).padStart(4, "0");
      const clockSeqHiAndReserved = (0x80 | (parseInt(getRandomHex(1), 16) & 0x3f)).toString(16).padStart(2, "0");
      const clockSeqLow = getRandomHex(1);
      const node = getRandomHex(6);

      return `${timeLow}-${timeMid}-${timeHiAndVersion}-${clockSeqHiAndReserved}${clockSeqLow}-${node}` as `${string}-${string}-${string}-${string}-${string}`;
    };
  }
}

export {};
