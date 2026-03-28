// Chess Theater — ReconnectStrategy
// Exponential backoff: 1s, 2s, 4s, 8s, ... up to 30s ceiling

const BASE_DELAY_MS = 1_000
const MAX_DELAY_MS = 30_000

export class ReconnectStrategy {
  private attempt = 0

  reset(): void {
    this.attempt = 0
  }

  nextDelay(): number {
    const delay = Math.min(BASE_DELAY_MS * 2 ** this.attempt, MAX_DELAY_MS)
    this.attempt++
    return delay
  }

  get attempts(): number {
    return this.attempt
  }
}
