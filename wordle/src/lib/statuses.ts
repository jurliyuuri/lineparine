import { solution } from './words'
import { ORTHOGRAPHY } from '../constants/orthography'
import { ORTHOGRAPHY_PATTERN } from './tokenizer'

export type CharStatus = 'absent' | 'present' | 'correct'

export type CharValue = typeof ORTHOGRAPHY[number]

export const getStatuses = (
  guesses: string[][]
): { [key: string]: CharStatus } => {
  const charObj: { [key: string]: CharStatus } = {}
  const solutionChars = solution.split(ORTHOGRAPHY_PATTERN).filter((i) => i)
  guesses.forEach((word) => {
    word.forEach((letter, i) => {
      if (!solutionChars.includes(letter)) {
        // make status absent
        return (charObj[letter] = 'absent')
      }

      if (letter === solutionChars[i]) {
        //make status correct
        return (charObj[letter] = 'correct')
      }

      if (charObj[letter] !== 'correct') {
        //make status present
        return (charObj[letter] = 'present')
      }
    })
  })

  return charObj
}

export const getGuessStatuses = (guess: string[]): CharStatus[] => {
  const splitSolution = solution.split(ORTHOGRAPHY_PATTERN).filter((i) => i)
  const splitGuess = guess

  const solutionCharsTaken = splitSolution.map((_) => false)

  const statuses: CharStatus[] = Array.from(Array(guess.length))

  // handle all correct cases first
  splitGuess.forEach((letter, i) => {
    if (letter === splitSolution[i]) {
      statuses[i] = 'correct'
      solutionCharsTaken[i] = true
      return
    }
  })

  splitGuess.forEach((letter, i) => {
    if (statuses[i]) return

    if (!splitSolution.includes(letter)) {
      // handles the absent case
      statuses[i] = 'absent'
      return
    }

    // now we are left with "present"s
    const indexOfPresentChar = splitSolution.findIndex(
      (x, index) => x === letter && !solutionCharsTaken[index]
    )

    if (indexOfPresentChar > -1) {
      statuses[i] = 'present'
      solutionCharsTaken[indexOfPresentChar] = true
      return
    } else {
      statuses[i] = 'absent'
      return
    }
  })

  return statuses
}
