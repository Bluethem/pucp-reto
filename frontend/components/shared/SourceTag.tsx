interface SourceTagProps {
  source: string
  date?: string
}

export default function SourceTag({ source, date }: SourceTagProps) {
  return (
    <span className="inline-flex items-center gap-1 text-[10px] font-medium text-gray-500 bg-gray-100 px-1.5 py-0.5 rounded uppercase tracking-wide">
      {source}
      {date && <span className="opacity-60">· {date}</span>}
    </span>
  )
}
