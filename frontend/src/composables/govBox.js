export function roundToStep(value) {
  return (Math.round(Math.round(Number(value) * 100) / 5) * 5) / 100
}

function round2(value) {
  return Math.round(value * 100) / 100
}

export function boundingRange(value, distance) {
  const center = roundToStep(value)
  const d = Number(distance)
  return [round2(center - d), round2(center + d)]
}

export const distanceOptions = Array.from({ length: 10 }, (_, i) => round2((i + 1) * 0.05))
