const paths = {
  upload: <><path d="M12 16V4" /><path d="m7 9 5-5 5 5" /><path d="M5 15v4a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-4" /></>,
  file: <><path d="M6 2h8l4 4v16H6z" /><path d="M14 2v5h5" /><path d="M9 12h6M9 16h6" /></>,
  shield: <><path d="M12 22s8-3 8-10V5l-8-3-8 3v7c0 7 8 10 8 10Z" /><path d="m9 12 2 2 4-4" /></>,
  check: <path d="m5 12 4 4L19 6" />,
  alert: <><path d="M12 3 2.5 20h19Z" /><path d="M12 9v4M12 17h.01" /></>,
  layers: <><path d="m12 2 9 5-9 5-9-5 9-5Z" /><path d="m3 12 9 5 9-5M3 17l9 5 9-5" /></>,
  spark: <><path d="m12 3 1.5 4.5L18 9l-4.5 1.5L12 15l-1.5-4.5L6 9l4.5-1.5L12 3Z" /><path d="m19 15 .75 2.25L22 18l-2.25.75L19 21l-.75-2.25L16 18l2.25-.75L19 15Z" /></>,
  chart: <><path d="M5 20v-7M12 20V4M19 20v-11" /><path d="M3 20h18" /></>,
  replace: <><path d="M20 7h-5V2" /><path d="M4 17h5v5" /><path d="M5.6 9A8 8 0 0 1 19 6l1 1M4 17l1 1a8 8 0 0 0 13.4-3" /></>,
  download: <><path d="M12 3v12" /><path d="m7 10 5 5 5-5" /><path d="M5 21h14" /></>,
  chevron: <path d="m9 18 6-6-6-6" />,
  menu: <><path d="M4 7h16M4 12h16M4 17h16" /></>,
  close: <><path d="m6 6 12 12M18 6 6 18" /></>,
  external: <><path d="M14 3h7v7" /><path d="m10 14 11-11" /><path d="M21 14v6a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h6" /></>,
  arrow: <><path d="M5 12h14" /><path d="m14 7 5 5-5 5" /></>,
  target: <><circle cx="12" cy="12" r="8" /><circle cx="12" cy="12" r="3" /><path d="M12 2v3M22 12h-3M12 22v-3M2 12h3" /></>,
}

export function Icon({ name, size = 20, className = '' }) {
  return (
    <svg className={className} width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      {paths[name] || paths.spark}
    </svg>
  )
}

export function BrandMark() {
  return (
    <svg className="brand-mark" viewBox="0 0 40 40" role="img" aria-label="ResumeAI">
      <rect width="40" height="40" rx="11" />
      <path d="M10.5 20h5.25m8.5 0h5.25M20 10.5v3.75m0 11.5v3.75" />
      <circle cx="20" cy="20" r="6.25" />
      <path d="m24.4 24.4 4.2 4.2" />
    </svg>
  )
}

export function ResumeIllustration() {
  return (
    <svg className="resume-illustration" viewBox="0 0 320 230" aria-hidden="true">
      <path className="resume-illustration__shadow" d="M60 196h218l-32 18H88Z" />
      <g className="resume-illustration__sheet resume-illustration__sheet--back">
        <rect x="145" y="50" width="116" height="142" rx="12" transform="rotate(8 145 50)" />
        <path d="m174 86 57 8M171 103l51 7M168 120l59 8M166 138l45 6" />
      </g>
      <g className="resume-illustration__sheet resume-illustration__sheet--front">
        <rect x="76" y="34" width="128" height="166" rx="12" transform="rotate(-7 76 34)" />
        <circle cx="126" cy="78" r="16" />
        <path d="M109 105h64M106 124h72M104 143h55M101 162h68" />
      </g>
      <path className="resume-illustration__spark" d="m53 64 4 11 11 4-11 4-4 11-4-11-11-4 11-4 4-11Z" />
      <path className="resume-illustration__spark" d="m246 26 2.5 7 7 2.5-7 2.5-2.5 7-2.5-7-7-2.5 7-2.5 2.5-7Z" />
    </svg>
  )
}
