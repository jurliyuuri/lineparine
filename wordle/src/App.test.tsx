import { render, screen } from '@testing-library/react'
import App from './App'
import { ORTHOGRAPHY } from './constants/orthography'
import { WORDS } from './constants/wordlist'
import { ORTHOGRAPHY_PATTERN } from './lib/tokenizer'

test('renders Not Wordle', () => {
  render(<App />)
  const linkElement = screen.getByText(/Not Wordle/i)
  expect(linkElement).toBeInTheDocument()
})

test('no surprise characters', () => {
  let splitWords = WORDS.map((x) =>
    x.split(ORTHOGRAPHY_PATTERN).filter((x) => x)
  )
  splitWords.forEach((word) => {
    expect(ORTHOGRAPHY).toEqual(expect.arrayContaining(word))
  })
})
