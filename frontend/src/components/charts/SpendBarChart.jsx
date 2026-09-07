import {
  BarChart, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, Cell,
} from 'recharts'

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-card border border-border rounded-xl px-3 py-2 shadow-xl">
      <p className="text-xs text-secondary mb-1">{label}</p>
      <p className="text-sm font-semibold text-primary">
        ${Number(payload[0].value).toLocaleString()}
      </p>
    </div>
  )
}

export default function SpendBarChart({ data, activeIndex }) {
  return (
    <ResponsiveContainer width="100%" height={180}>
      <BarChart data={data} barSize={18} margin={{ top: 8, right: 4, bottom: 0, left: -24 }}>
        <XAxis
          dataKey="label"
          tick={{ fill: '#9ca3af', fontSize: 11 }}
          axisLine={false}
          tickLine={false}
        />
        <YAxis
          tick={{ fill: '#9ca3af', fontSize: 11 }}
          axisLine={false}
          tickLine={false}
          tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`}
        />
        <Tooltip content={<CustomTooltip />} cursor={false} />
        <Bar dataKey="value" radius={[4, 4, 0, 0]}>
          {data.map((_, i) => (
            <Cell
              key={i}
              fill={i === activeIndex ? '#7B6EF6' : '#2e2e32'}
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
