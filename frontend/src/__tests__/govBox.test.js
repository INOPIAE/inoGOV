import { describe, expect, it } from 'vitest'
import { boundingRange, distanceOptions, roundToStep } from '../composables/govBox'

describe('govBox', () => {
  it('rounds to the nearest multiple of 0.05', () => {
    expect(roundToStep(50.730346)).toBe(50.75)
    expect(roundToStep(50.72)).toBe(50.7)
    expect(roundToStep(7.5)).toBe(7.5)
  })

  it('computes the bounding range around the rounded value', () => {
    expect(boundingRange(50.730346, 0.05)).toEqual([50.7, 50.8])
    expect(boundingRange(25.2, 0.2)).toEqual([25, 25.4])
  })

  it('offers distances from 0.05 to 0.5 in 0.05 steps', () => {
    expect(distanceOptions).toEqual([0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5])
  })
})
