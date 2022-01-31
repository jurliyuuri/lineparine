import { getGuessStatuses } from '../../lib/statuses'
import { MiniCell } from './MiniCell'

type Props = {
  guess: string[]
}

export const MiniCompletedRow = ({ guess }: Props) => {
  const statuses = getGuessStatuses(guess)

  return (
    <div className="flex justify-center mb-1">
      {guess.map((letter, i) => (
        <MiniCell key={i} status={statuses[i]} letter={letter} />
      ))}
    </div>
  )
}
