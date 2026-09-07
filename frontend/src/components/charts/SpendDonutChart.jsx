import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts'

const COLORS = ['#7B6EF6', '#4ade80', '#f59e0b', '#f97316', '#a855f7', '#38bdf8']

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-card border border-border rounded-xl px-3 py-2 shadow-xl">
      <p className="text-xs text-secondary">{payload[0].name}</p>
      <p className="text-sm font-semibold text-primary">
        ${Number(payload[0].value).toLocaleString()}
      </p>
      <p className="text-xs text-secondary">
        {payload[0].payload.pct}%
      </p>
    </div>
  )
}

export default function SpendDonutChart({ data, total }) {
  return (
    <div className="flex items-center gap-6">
      <div className="relative shrink-0" style={{ width: 160, height: 160 }}>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={52}
              outerRadius={72}
              paddingAngle={2}
              dataKey="value"
            >
              {data.map((_, i) => (
                <Cell key={i} fill={COLORS[i % COLORS.length]} strokeWidth={0} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
          </PieChart>
        </ResponsiveContainer>
        {/* Center label */}
        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
          <span className="text-[10px] text-secondary">Total</span>
          <span className="text-sm font-semibold text-primary">
            ${(total / 1000).toFixed(0)}k
          </span>
        </div>
      </div>

      {/* Legend */}
      <div className="flex flex-col gap-2 flex-1">
        {data.map((item, i) => (
          <div key={i} className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <span
                className="w-2 h-2 rounded-full shrink-0"
                style={{ background: COLORS[i % COLORS.length] }}
              />
              <span className="text-xs text-secondary truncate max-w-[100px]">{item.name}</span>
            </div>
            <span className="text-xs text-primary font-medium">{item.pct}%</span>
          </div>
        ))}
      </div>
    </div>
  )
}
