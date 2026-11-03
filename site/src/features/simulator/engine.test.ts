import { describe, it, expect } from "vitest";
import { detectBeacons, periodicityScore } from "./engine";
import fixture from "./__fixtures__/beacon.json";

describe("periodicityScore parity", () => {
  for (const [name, data] of Object.entries(fixture as Record<string, { times: number[]; result: Record<string, number> }>)) {
    it(name, () => {
      const got = periodicityScore(data.times);
      expect(got.score).toBeCloseTo(data.result.score, 6);
      expect(got.period_s).toBeCloseTo(data.result.period_s, 6);
      expect(got.within_ten_percent).toBeCloseTo(data.result.within_ten_percent, 6);
    });
  }
});

describe("detectBeacons", () => {
  it("groups endpoint pairs without regard to direction", () => {
    const times = [0, 30, 60, 90, 120];
    const flows = times.map((started_at, index) => index % 2
      ? { host_hash: "h:b", peer_hash: "h:a", started_at }
      : { host_hash: "h:a", peer_hash: "h:b", started_at });
    expect(detectBeacons(flows)).toHaveLength(1);
  });

  it("does not alert below the configured threshold or group size", () => {
    const irregular = [0, 5, 40, 47, 100, 130, 137, 220];
    const flows = irregular.map((started_at) => ({ host_hash: "a", peer_hash: "b", started_at }));
    expect(detectBeacons(flows)).toHaveLength(0);
    const tooShort = flows.slice(0, 3);
    expect(detectBeacons(tooShort)).toHaveLength(0);
  });
});
