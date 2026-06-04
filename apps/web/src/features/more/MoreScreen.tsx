import { ChevronRight, Settings, Tags, Wallet, type LucideIcon } from "lucide-react";

type MoreTarget = "budgets" | "categories" | "settings";

interface Props {
  onNavigate: (view: MoreTarget) => void;
}

const ITEMS: { key: MoreTarget; label: string; icon: LucideIcon }[] = [
  { key: "budgets", label: "예산", icon: Wallet },
  { key: "categories", label: "카테고리", icon: Tags },
  { key: "settings", label: "설정", icon: Settings },
];

export function MoreScreen({ onNavigate }: Props) {
  return (
    <div className="more-screen">
      <h2>더보기</h2>
      <ul className="more-list">
        {ITEMS.map(({ key, label, icon: Icon }) => (
          <li key={key}>
            <button type="button" className="more-row" onClick={() => onNavigate(key)}>
              <Icon size={20} className="more-icon" />
              <span className="more-label">{label}</span>
              <ChevronRight size={18} className="more-chevron" />
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
