interface Props {
  label: string;
  value: string | number | null;
  sub?: string;
  color?: "green" | "yellow" | "red" | "blue" | "default";
}

const colorMap = {
  green:   "text-green-400",
  yellow:  "text-yellow-400",
  red:     "text-red-400",
  blue:    "text-blue-400",
  default: "text-white",
};

export default function MetricCard({ label, value, sub, color = "default" }: Props) {
  return (
    <div className="bg-gray-900 border border-gray-700 rounded-xl p-4">
      <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">{label}</p>
      <p className={`text-2xl font-bold ${colorMap[color]}`}>
        {value !== null && value !== undefined ? value : "—"}
      </p>
      {sub && <p className="text-xs text-gray-500 mt-1">{sub}</p>}
    </div>
  );
}
