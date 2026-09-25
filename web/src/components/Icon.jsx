const paths = {
  file: <><path d="M6 2h8l4 4v16H6z" /><path d="M14 2v5h5" /><path d="M9 12h6M9 16h6" /></>,
  check: <path d="m5 12 4 4L19 6" />,
  alert: <><path d="M12 3 2.5 20h19Z" /><path d="M12 9v4M12 17h.01" /></>,
  replace: <><path d="M20 7h-5V2" /><path d="M4 17h5v5" /><path d="M5.6 9A8 8 0 0 1 19 6l1 1M4 17l1 1a8 8 0 0 0 13.4-3" /></>,
  download: <><path d="M12 3v12" /><path d="m7 10 5 5 5-5" /><path d="M5 21h14" /></>,
  chevron: <path d="m9 18 6-6-6-6" />,
  close: <><path d="m6 6 12 12M18 6 6 18" /></>,
  external: <><path d="M14 3h7v7" /><path d="m10 14 11-11" /><path d="M21 14v6a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h6" /></>,
  arrow: <><path d="M5 12h14" /><path d="m14 7 5 5-5 5" /></>,
  sun: <><circle cx="12" cy="12" r="4" /><path d="M12 2v2M12 20v2M4.93 4.93l1.42 1.42M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.42-1.42M17.66 6.34l1.41-1.41" /></>,
  moon: <path d="M20.5 14.3A8.5 8.5 0 0 1 9.7 3.5 8.5 8.5 0 1 0 20.5 14.3Z" />,
}

export function Icon({ name, size = 20, className = '' }) {
  return (
    <svg className={className} width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      {paths[name] || paths.file}
    </svg>
  )
}

export function BrandMark() {
  return (
    <svg className="brand-mark" viewBox="0 0 40 40" role="img" aria-label="cvLens">
      <rect width="40" height="40" rx="11" />
      <path d="M10.5 20h5.25m8.5 0h5.25M20 10.5v3.75m0 11.5v3.75" />
      <circle cx="20" cy="20" r="6.25" />
      <path d="m24.4 24.4 4.2 4.2" />
    </svg>
  )
}
