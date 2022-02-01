import { CONFIG } from './config'

export const ORTHOGRAPHY = [
  'p',
  'f',
  't',
  'c',
  'x',
  'k',
  'q',
  'h',
  'r',
  'z',
  'm',
  'n',
  'r',
  'l',
  'j',
  'w',
  'b',
  'v',
  'd',
  's',
  'g',
  'i',
  'y',
  'u',
  'o',
  'e',
  'a',
]

if (CONFIG.normalization) {
  ORTHOGRAPHY.forEach(
    (val, i) => (ORTHOGRAPHY[i] = val.normalize(CONFIG.normalization))
  )
}
