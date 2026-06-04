import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import { formatKRW } from "../../lib/money";
import type { CategorySummary } from "../../lib/types";

// Matches the --cat-1..8 design tokens (recharts needs concrete colors).
export const CHART_COLORS = [
  "#5b8def", "#34c7a8", "#f4b740", "#e06c9f",
  "#9b7be0", "#5bc0de", "#7bc86c", "#e8836b",
];

export function CategoryChart({ data }: { data: CategorySummary[] }) {
  const chartData = data.map((d) => ({ name: d.name, value: d.sum_minor }));

  return (
    <ResponsiveContainer width="100%" height={260}>
      <PieChart>
        <Pie
          data={chartData}
          dataKey="value"
          nameKey="name"
          innerRadius={84}
          outerRadius={110}
          paddingAngle={3}
          cornerRadius={6}
          stroke="none"
        >
          {chartData.map((_, i) => (
            <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
          ))}
        </Pie>
        <Tooltip
          formatter={(v: number) => formatKRW(v)}
          contentStyle={{
            background: "#20283a",
            border: "1px solid #2a3346",
            borderRadius: 12,
            color: "#f4f6fb",
          }}
        />
      </PieChart>
    </ResponsiveContainer>
  );
}
