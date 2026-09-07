import {
  AreaChart, Area, XAxis, YAxis, Tooltip,
  ResponsiveContainer, ReferenceLine,
} from 'recharts'

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-card border border-border rounded-xl px-3 py-2 shadow-xl">
      <p className="text-xs text-secondary mb-1">{label}</p>
      {payload.map((p, i) => (
        <p key={i} className="text-sm font-semibold" style={{ color: p.color }}>
          ${Number(p.value).toLocaleString()}
        </p>
      ))}
    </div>
  )
}

export default function ForecastLineChart({ data, forecastStart }) {
  return (
    <ResponsiveContainer width="100%" height={180}>
      <AreaChart data={data} margin={{ top: 8, right: 4, bottom: 0, left: -24 }}>
        <defs>
          <linearGradient id="actual" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%"  stopColor="#7B6EF6" stopOpacity={0.3} />
            <stop offset="95%" stopColor="#7B6EF6" stopOpacity={0} />
          </linearGradient>
          <linearGradient id="forecast" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%"  stopColor="#4ade80" stopOpacity={0.2} />
            <stop offset="95%" stopColor="#4ade80" stopOpacity={0} />
          </linearGradient>
        </defs>
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
        <Tooltip content={<CustomTooltip />} />
        {forecastStart && (
          <ReferenceLine
            x={forecastStart}
            stroke="#2e2e32"
            strokeDasharray="4 4"
            label={{ value: 'Forecast', fill: '#555558', fontSize: 10, position: 'top' }}
          />
        )}
        <Area
          type="monotone"
          dataKey="actual"
          stroke="#7B6EF6"
          strokeWidth={2}
          fill="url(#actual)"
          dot={false}
          connectNulls
        />
        <Area
          type="monotone"
          dataKey="forecast"
          stroke="#4ade80"
          strokeWidth={2}
          strokeDasharray="5 3"
          fill="url(#forecast)"
          dot={false}
          connectNulls
        />
      </AreaChart>
    </ResponsiveContainer>
  )
}
