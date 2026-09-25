const steps = ['Upload', 'Analyze', 'Results', 'Improve']

export default function ProgressSteps({ currentStep }) {
  return (
    <section className="progress-steps" aria-label={`Step ${currentStep} of ${steps.length}: ${steps[currentStep - 1]}`}>
      <div className="progress-steps__mobile-copy">
        <span>Step {currentStep} of {steps.length}</span>
        <strong>{steps[currentStep - 1]}</strong>
      </div>
      <ol>
        {steps.map((step, index) => {
          const number = index + 1
          const state = number < currentStep ? 'complete' : number === currentStep ? 'current' : 'upcoming'
          return (
            <li className={`progress-step progress-step--${state}`} key={step} aria-current={state === 'current' ? 'step' : undefined}>
              <span className="progress-step__number">{number}</span>
              <span className="progress-step__label">{step}</span>
            </li>
          )
        })}
      </ol>
    </section>
  )
}
